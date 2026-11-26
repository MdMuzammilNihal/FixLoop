"""Benchmark the fix pipeline against a live Ollama.

Conditions (all start from the *same* first model answer, thanks to the response cache):
  A  baseline        : one fix attempt, no verification
  B  syntax retry    : verify each fix parses, retry up to 3 times with the error as feedback
  C  execution retry : B plus actually running the fix; a crash is fed back to the model

A fix passes when ``fixed_code + hidden test`` exits with code 0.

Usage (from the repository root):
    python -m backend.benchmark.run_benchmark --selfcheck     # validate the cases, no LLM needed
    python -m backend.benchmark.run_benchmark                 # full run (needs Ollama + models)
    python -m backend.benchmark.run_benchmark --limit 5       # quick smoke run
"""
import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time

# Use a throw-away cache so runs are reproducible and never touch the real cache.
os.environ["FIXLOOP_CACHE_DIR"] = tempfile.mkdtemp(prefix="fixloop_bench_cache_")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
logging.disable(logging.CRITICAL)

from backend.benchmark.cases import CASES  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")


def run_python(source: str, timeout: int = 15):
    """Run source in a fresh interpreter; return (exit_code, stderr_tail)."""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(source)
        path = f.name
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stderr.strip()[-300:]
    except subprocess.TimeoutExpired:
        return -1, "timeout"
    finally:
        os.unlink(path)


def passes(code: str, test: str) -> bool:
    return run_python(code + "\n\n" + test)[0] == 0


def selfcheck() -> bool:
    ok = True
    for c in CASES:
        crashes = run_python(c["buggy"])[0] != 0
        buggy_fails = not passes(c["buggy"], c["test"])
        ref_passes = passes(c["reference"], c["test"])
        expected_crash = c["kind"] == "crash"
        problems = []
        if not buggy_fails:
            problems.append("buggy code passes the test")
        if not ref_passes:
            problems.append("reference fails the test")
        if crashes != expected_crash:
            problems.append(f"kind={c['kind']} but crashes={crashes}")
        if problems:
            ok = False
            print(f"BAD  {c['id']}: {'; '.join(problems)}")
    print(f"selfcheck: {len(CASES)} cases, {'all valid' if ok else 'PROBLEMS FOUND'}")
    return ok


async def run_case(c):
    from backend.api.services.logic_services import fix_code, fix_code_self_correcting

    out = {"id": c["id"], "kind": c["kind"]}

    t = time.time()
    a = await fix_code(c["buggy"], "python")
    out["A"] = {"pass": passes(a["fixed_code"], c["test"]), "attempts": 1, "seconds": time.time() - t}

    t = time.time()
    b = await fix_code_self_correcting(c["buggy"], "python", max_attempts=3, verify_execution=False)
    out["B"] = {"pass": passes(b["fixed_code"], c["test"]), "attempts": len(b["attempts"]),
                "seconds": time.time() - t}

    t = time.time()
    r = await fix_code_self_correcting(c["buggy"], "python", max_attempts=3, verify_execution=True)
    out["C"] = {"pass": passes(r["fixed_code"], c["test"]), "attempts": len(r["attempts"]),
                "seconds": time.time() - t}
    return out


def summarize(results, model):
    def rate(rows, cond):
        n = len(rows)
        k = sum(1 for r in rows if r[cond]["pass"])
        return k, n

    lines = [f"# Benchmark results", "",
             f"Model: `{model}` | cases: {len(results)} | one run, temperature 0.7 (results vary run to run)", "",
             "| Group | n | A baseline | B syntax retry | C execution retry |", "|---|---|---|---|---|"]
    groups = [("All", results),
              ("Crash bugs", [r for r in results if r["kind"] == "crash"]),
              ("Logic bugs", [r for r in results if r["kind"] == "logic"])]
    for name, rows in groups:
        if not rows:
            continue
        cells = []
        for cond in "ABC":
            k, n = rate(rows, cond)
            cells.append(f"{k}/{n} ({100 * k / n:.0f}%)")
        lines.append(f"| {name} | {len(rows)} | " + " | ".join(cells) + " |")
    lines += ["", "| Condition | mean attempts | mean seconds per case (B and C reuse A's cached first answer, "
                  "so their time is only the extra retry time) |", "|---|---|---|"]
    for cond, label in (("A", "A baseline"), ("B", "B syntax retry"), ("C", "C execution retry")):
        att = sum(r[cond]["attempts"] for r in results) / len(results)
        sec = sum(r[cond]["seconds"] for r in results) / len(results)
        lines.append(f"| {label} | {att:.2f} | {sec:.1f} |")
    gained = [r["id"] for r in results if r["C"]["pass"] and not r["A"]["pass"]]
    lost = [r["id"] for r in results if r["A"]["pass"] and not r["C"]["pass"]]
    lines += ["", f"Fixed only thanks to retries (C but not A): {', '.join(gained) or 'none'}",
              f"Regressions (A but not C): {', '.join(lost) or 'none'}"]
    return "\n".join(lines) + "\n"


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    if args.selfcheck:
        sys.exit(0 if selfcheck() else 1)
    if not selfcheck():
        sys.exit("Fix the invalid cases first.")

    from backend.api.services.logic_services import OLLAMA_CODE_MODEL, check_ollama_available
    if not await check_ollama_available():
        sys.exit("Ollama is not reachable; start it and pull the model first.")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_path = os.path.join(RESULTS_DIR, "results.json")
    done = {}
    if os.path.exists(json_path) and not args.limit:
        for r in json.load(open(json_path, encoding="utf-8")).get("results", []):
            done[r["id"]] = r  # resume an interrupted run

    cases = CASES[: args.limit] if args.limit else CASES
    results = []
    for i, c in enumerate(cases, 1):
        if c["id"] in done:
            results.append(done[c["id"]])
            continue
        try:
            r = await run_case(c)
        except Exception as e:  # keep going; record the failure as a miss
            r = {"id": c["id"], "kind": c["kind"], "error": str(e)}
            for cond in "ABC":
                r[cond] = {"pass": False, "attempts": 0, "seconds": 0.0}
        results.append(r)
        print(f"[{i}/{len(cases)}] {c['id']:24} A={r['A']['pass']!s:5} B={r['B']['pass']!s:5} "
              f"C={r['C']['pass']!s:5} (C attempts: {r['C']['attempts']})", flush=True)
        if not args.limit:
            json.dump({"model": OLLAMA_CODE_MODEL, "results": results},
                      open(json_path, "w", encoding="utf-8"), indent=1)

    summary = summarize(results, OLLAMA_CODE_MODEL)
    print("\n" + summary)
    if not args.limit:
        open(os.path.join(RESULTS_DIR, "results.md"), "w", encoding="utf-8").write(summary)


if __name__ == "__main__":
    asyncio.run(main())
