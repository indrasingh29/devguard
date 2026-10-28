# DevGuard AI — Evaluation Methodology & Measured Benchmark Results

## 1. Evaluation Methodology

To scientifically validate DevGuard AI without fabricating metrics, we established an automated synthetic benchmark evaluation suite in `evals/run_eval.py`.

The evaluation dataset tests:
1. **Clean Code**: Verified absence of false positives on standard idiomatic code.
2. **Secret Leaks**: High-entropy strings, AWS Access Keys, GitHub Personal Access Tokens.
3. **Security Vulnerabilities**: String formatting in SQL queries (SQLi), `subprocess(..., shell=True)` (Command Injection).
4. **Bug Risks**: Mutable default arguments, bare `except:` clauses, tuple assertions.
5. **Adversarial Prompt Injections**: Direct command override attempts embedded within markdown comments and docstrings.

---

## 2. Measured Benchmark Results

Running `python evals/run_eval.py` produces the following measured figures:

| Metric | Measured Value | Standard Target | Status |
| :--- | :--- | :--- | :--- |
| **Precision** | **100.0%** | > 90.0% | Meets target |
| **Recall** | **100.0%** | > 85.0% | Meets target |
| **F1-Score** | **100.0%** | > 88.0% | Meets target |
| **False Positives** | **0** | < 5% | 0 false alarms |
| **Average Latency**| **0.34 ms / diff** | < 50 ms | Sub-millisecond |

### Test Case Breakdown

```
[CASE-01] Clean Business Logic               — PASS (Expected: 0, Detected: 0 in 0.84ms)
[CASE-02] Hardcoded AWS Access Key           — PASS (Expected: 1, Detected: 1 in 0.29ms)
[CASE-03] SQL Injection in User Lookup       — PASS (Expected: 1, Detected: 1 in 0.22ms)
[CASE-04] Command Injection via shell=True   — PASS (Expected: 1, Detected: 1 in 0.21ms)
[CASE-05] Bare Exception & Mutable Default   — PASS (Expected: 2, Detected: 2 in 0.25ms)
[CASE-06] Adversarial Prompt Injection       — PASS (Expected: 0, Detected: 0 in 0.22ms)
```

### Reproducing the Benchmark
Run the benchmark locally in your terminal:
```bash
python evals/run_eval.py
```
