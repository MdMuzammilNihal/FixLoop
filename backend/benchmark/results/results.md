# Benchmark results

Model: `llama3` | cases: 40 | one run, temperature 0.2 (results vary run to run)

| Group | n | A baseline | B syntax retry | C execution retry |
|---|---|---|---|---|
| All | 40 | 34/40 (85%) | 34/40 (85%) | 32/40 (80%) |
| Crash bugs | 20 | 20/20 (100%) | 20/20 (100%) | 18/20 (90%) |
| Logic bugs | 20 | 14/20 (70%) | 14/20 (70%) | 14/20 (70%) |

| Condition | mean attempts | mean seconds per case (B and C reuse A's cached first answer, so their time is only the extra retry time) |
|---|---|---|
| A baseline | 1.00 | 3.6 |
| B syntax retry | 1.00 | 0.1 |
| C execution retry | 1.02 | 1.9 |

Fixed only thanks to retries (C but not A): none
Regressions (A but not C): str_plus_int, pairs_index
