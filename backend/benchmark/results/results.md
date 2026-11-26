# Benchmark results

Model: `codellama` | cases: 40 | one run, temperature 0.7 (results vary run to run)

| Group | n | A baseline | B syntax retry | C execution retry |
|---|---|---|---|---|
| All | 40 | 20/40 (50%) | 20/40 (50%) | 23/40 (58%) |
| Crash bugs | 20 | 15/20 (75%) | 15/20 (75%) | 16/20 (80%) |
| Logic bugs | 20 | 5/20 (25%) | 5/20 (25%) | 7/20 (35%) |

| Condition | mean attempts | mean seconds per case (B and C reuse A's cached first answer, so their time is only the extra retry time) |
|---|---|---|
| A baseline | 1.00 | 6.5 |
| B syntax retry | 1.00 | 0.1 |
| C execution retry | 1.27 | 2.1 |

Fixed only thanks to retries (C but not A): append_returns_none, reverse_drops_char, flatten_wrong_var
Regressions (A but not C): none
