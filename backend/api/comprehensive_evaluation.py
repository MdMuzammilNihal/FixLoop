import requests
import time
import json
from collections import defaultdict

API_URL = "http://127.0.0.1:8000/api/code"
STREAM_URL = "http://127.0.0.1:8000/api/code/stream"

REPORT_TXT = "comprehensive_evaluation_output.txt"
REPORT_MD = "comprehensive_evaluation_report.md"

# Helper for scoring
SCORE_LABELS = {
    1: "Poor",
    2: "Fair",
    3: "Good",
    4: "Excellent",
    5: "Outstanding"
}

def post_api(payload, stream=False):
    url = STREAM_URL if stream else API_URL
    try:
        resp = requests.post(url, json=payload, timeout=60)
        if stream:
            return resp.text
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def score(val):
    if val >= 4.5:
        return 5, SCORE_LABELS[5]
    elif val >= 3.5:
        return 4, SCORE_LABELS[4]
    elif val >= 2.5:
        return 3, SCORE_LABELS[3]
    elif val >= 1.5:
        return 2, SCORE_LABELS[2]
    else:
        return 1, SCORE_LABELS[1]

def run_tests():
    results = defaultdict(list)
    # 1. Code Analysis
    analysis_tests = [
        {
            "desc": "Simple bug detection (static)",
            "code": "def add(a, b):\n    return a + b\nprint(add(2))",
            "expect_error": True
        },
        {
            "desc": "Security vulnerability (eval)",
            "code": "def run(cmd):\n    eval(cmd)",
            "expect_error": True
        },
        {
            "desc": "Style issue (bad naming)",
            "code": "def BADNAME():\n    pass",
            "expect_warning": True
        },
        {
            "desc": "Contextual awareness (uses helper)",
            "code": "def helper(x):\n    return x*2\ndef main():\n    return helper(5)",
            "expect_suggestion": True
        }
    ]
    for test in analysis_tests:
        payload = {"code": test["code"], "language": "python", "action": "analyze"}
        resp = post_api(payload)
        results["analysis"].append({"test": test, "resp": resp})
    # 2. Code Optimization
    optimization_tests = [
        {
            "desc": "Inefficient loop",
            "code": "s = 0\nfor i in range(10000):\n    for j in range(10000):\n        s += i*j"
        },
        {
            "desc": "Unoptimized string concat",
            "code": "s = ''\nfor i in range(1000):\n    s += str(i)"
        }
    ]
    for test in optimization_tests:
        payload = {"code": test["code"], "language": "python", "action": "optimize"}
        resp = post_api(payload)
        results["optimization"].append({"test": test, "resp": resp})
    # 3. Code Fixing
    fix_tests = [
        {
            "desc": "Syntax error",
            "code": "def foo(\nprint('oops')"
        },
        {
            "desc": "Name error",
            "code": "print(xyz)"
        },
        {
            "desc": "Edge case: empty list",
            "code": "def sum_list(lst):\n    return sum(lst)\nprint(sum_list([]))"
        }
    ]
    for test in fix_tests:
        payload = {"code": test["code"], "language": "python", "action": "fix"}
        resp = post_api(payload)
        results["fixing"].append({"test": test, "resp": resp})
    # 4. Hints
    hint_tests = [
        {
            "desc": "Hints for basic function",
            "code": "def square(x):\n    return x*x"
        },
        {
            "desc": "Hints for code with anti-pattern",
            "code": "def f():\n    global x\n    x = 5"
        }
    ]
    for test in hint_tests:
        payload = {"code": test["code"], "language": "python", "action": "hint"}
        resp = post_api(payload)
        results["hints"].append({"test": test, "resp": resp})
    # 5. Execution (standard)
    exec_tests = [
        {"desc": "Simple print", "code": "print('hello world')"},
        {"desc": "Data types", "code": "print([1,2,3]); print({'a':1})"},
        {"desc": "File I/O", "code": "with open('testfile.txt', 'w') as f: f.write('abc')\nwith open('testfile.txt') as f: print(f.read())"},
        {"desc": "Standard lib", "code": "import math\nprint(math.sqrt(16))"}
    ]
    for test in exec_tests:
        payload = {"code": test["code"], "language": "python", "action": "execute"}
        resp = post_api(payload)
        results["execution"].append({"test": test, "resp": resp})
    # 5b. Execution (errors)
    error_exec_tests = [
        {"desc": "Syntax error", "code": "def foo(\nprint('oops')"},
        {"desc": "Name error", "code": "print(xyz)"},
        {"desc": "Type error", "code": "print(5 + 'a')"},
        {"desc": "Index error", "code": "a = [1]; print(a[5])"},
        {"desc": "Key error", "code": "d = {}; print(d['x'])"},
        {"desc": "ZeroDivisionError", "code": "print(1/0)"},
        {"desc": "FileNotFoundError", "code": "open('nope.txt')"},
        {"desc": "Custom exception", "code": "class E(Exception): pass\nraise E('fail')"},
        {"desc": "Infinite recursion", "code": "def f(): f()\nf()"}
    ]
    for test in error_exec_tests:
        payload = {"code": test["code"], "language": "python", "action": "execute"}
        resp = post_api(payload)
        results["execution_errors"].append({"test": test, "resp": resp})
    # 5c. Visualization
    viz_tests = [
        {"desc": "Matplotlib line plot", "code": "import matplotlib.pyplot as plt\nplt.plot([1,2,3],[4,5,6])\nplt.savefig('test_plot.png')"},
        {"desc": "Seaborn barplot", "code": "import seaborn as sns\nimport matplotlib.pyplot as plt\nsns.barplot(x=[1,2,3], y=[4,5,6])\nplt.savefig('bar.png')"}
    ]
    for test in viz_tests:
        payload = {"code": test["code"], "language": "python", "action": "execute"}
        resp = post_api(payload)
        results["visualization"].append({"test": test, "resp": resp})
    # 5d. ML/DL/NLP
    ml_tests = [
        {"desc": "scikit-learn classification", "code": "from sklearn.linear_model import LogisticRegression\nfrom sklearn.datasets import load_iris\nX, y = load_iris(return_X_y=True)\nmodel = LogisticRegression().fit(X, y)\nprint(model.score(X, y))"},
        {"desc": "PyTorch tensor", "code": "import torch\nt = torch.tensor([1,2,3])\nprint(t)"},
        {"desc": "TensorFlow constant", "code": "import tensorflow as tf\nt = tf.constant([1,2,3])\nprint(t)"},
        {"desc": "NLTK tokenization", "code": "import nltk\nprint(nltk.word_tokenize('hello world'))"}
    ]
    for test in ml_tests:
        payload = {"code": test["code"], "language": "python", "action": "execute"}
        resp = post_api(payload)
        results["ml"].append({"test": test, "resp": resp})
    return results

def evaluate_and_report(results):
    # For each category, assign scores and write markdown
    lines = []
    lines.append("# Comprehensive Evaluation Report\n")
    overall_scores = []
    for cat, tests in results.items():
        lines.append(f"## {cat.title()}\n")
        cat_scores = []
        for entry in tests:
            test = entry["test"]
            resp = entry["resp"]
            score_val = 3  # Default
            rating = "Good"
            # Heuristic scoring based on response
            if cat == "analysis":
                if resp.get("errors") or resp.get("warnings"):
                    score_val = 4
                    rating = "Excellent"
                if resp.get("errors") and test.get("expect_error"):
                    score_val = 5
                    rating = "Outstanding"
                if resp.get("error"):
                    score_val = 2
                    rating = "Fair"
            elif cat == "optimization":
                if resp.get("processed_code") and resp.get("explanation"):
                    score_val = 4
                    rating = "Excellent"
                if resp.get("error"):
                    score_val = 2
                    rating = "Fair"
            elif cat == "fixing":
                if resp.get("processed_code") or resp.get("fixed_code"):
                    score_val = 4
                    rating = "Excellent"
                if resp.get("error"):
                    score_val = 2
                    rating = "Fair"
            elif cat == "hints":
                if resp.get("hints") and len(resp["hints"]) >= 3:
                    score_val = 4
                    rating = "Excellent"
                if resp.get("error"):
                    score_val = 2
                    rating = "Fair"
            elif cat.startswith("execution") or cat == "ml":
                if resp.get("execution_result"):
                    if resp["execution_result"].get("stderr"):
                        score_val = 3
                        rating = "Good"
                    else:
                        score_val = 4
                        rating = "Excellent"
                if resp.get("error"):
                    score_val = 2
                    rating = "Fair"
            elif cat == "visualization":
                if resp.get("execution_result") and "visualization" in json.dumps(resp["execution_result"]):
                    score_val = 5
                    rating = "Outstanding"
                elif resp.get("execution_result"):
                    score_val = 4
                    rating = "Excellent"
                else:
                    score_val = 2
                    rating = "Fair"
            cat_scores.append(score_val)
            lines.append(f"### {test['desc']}")
            lines.append(f"- **Input:**\n```python\n{test['code']}\n```")
            lines.append(f"- **Output:**\n```")
            lines.append(json.dumps(resp, indent=2))
            lines.append("```")
            lines.append(f"- **Score:** {score_val} ({rating})\n")
        avg_cat_score = sum(cat_scores)/len(cat_scores) if cat_scores else 0
        overall_scores.append(avg_cat_score)
        lines.append(f"**Category Average Score:** {avg_cat_score:.2f}\n")
    overall = sum(overall_scores)/len(overall_scores) if overall_scores else 0
    lines.append(f"\n# Overall Performance Score: {overall:.2f} / 5\n")
    # Suggestions
    lines.append("\n## Suggestions for Improvement\n")
    lines.append("- Improve error message clarity and traceability.\n- Enhance contextual awareness for multi-function code.\n- Broaden ML/DL/NLP library support and error reporting.\n- Add more proactive hints and best-practice suggestions.\n- Improve handling of edge cases in code fixing and execution.\n")
    # Write to files
    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Report written to {REPORT_TXT} and {REPORT_MD}")

def main():
    print("Running comprehensive evaluation...")
    results = run_tests()
    evaluate_and_report(results)

if __name__ == "__main__":
    main() 