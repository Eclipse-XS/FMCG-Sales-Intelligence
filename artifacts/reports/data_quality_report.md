# Data quality report

Generated validation results.

| Check | Result | Detail |
|---|---|---|
| sales business key unique | PASS | rows=35892 |
| sales nonnegative | PASS |  |
| inventory business key unique | PASS | rows=17280 |
| inventory nonnegative | PASS |  |
| inventory flow equation | PASS | stock[t] = stock[t-1] - fulfilled + replenishment + adjustment |
| order items have parents | PASS | items=24216 |
| order totals reconcile | PASS | tolerance=0.01 |
