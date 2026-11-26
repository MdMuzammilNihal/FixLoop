# Benchmark results

Model: `llama3` | cases: 40 | one run, temperature 0.2 (results vary run to run)

| Group | n | A baseline | B syntax retry | C execution retry |
|---|---|---|---|---|
| All | 40 | 32/40 (80%) | 32/40 (80%) | 32/40 (80%) |
| Crash bugs | 20 | 19/20 (95%) | 19/20 (95%) | 19/20 (95%) |
| Logic bugs | 20 | 13/20 (65%) | 13/20 (65%) | 13/20 (65%) |

| Condition | mean attempts | mean seconds per case (B and C reuse A's cached first answer, so their time is only the extra retry time) |
|---|---|---|
| A baseline | 1.00 | 2.5 |
| B syntax retry | 1.00 | 0.1 |
| C execution retry | 1.05 | 1.4 |

Fixed only thanks to retries (C but not A): none
Regressions (A but not C): none
