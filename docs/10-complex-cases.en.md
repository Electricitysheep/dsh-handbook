[English](./10-complex-cases.en.md) | [中文](./10-complex-cases.md) · [← Back](../README.md)

# Chapter 10: Complex Real-World Cases (Run Live in dsh)

> **Goal of this chapter:** Demonstrate dsh's actual capabilities, output quality, and timing on multi-step tool chains through two **complex tasks completed live in dsh.**
> **Privacy notice:** Both cases use **synthetic data / self-authored code** only. No real business data or sensitive information is involved.

## TL;DR (30-second version)

1. **Case A (data quality analysis, 186 seconds)**: 52 rows of dirty data → analysis → cleaning script → visualization → run verification. 52 → 35 rows, all issues resolved.
2. **Case B (5-bug fix + 49 tests, 94 seconds)**: calculator module with 5 planted bugs → all fixed → 49 tests pass, covering edge cases, precision, and exceptions.
3. **dsh's profile**: auto-orchestrated multi-step tool chains, shows judgment (proactively explains data trade-offs), artifact tracking, controllable timing (94-186s).
4. **Key insight**: write acceptance criteria clearly in the prompt (e.g. "run and verify"), and dsh will close the loop. For complex tasks, specify "what to do + how to verify."
5. **Failure recovery**: not triggered in these cases. Production recommendation: pair with guard timeouts + human approval.

## Case A: Data Quality Analysis + Cleaning + Visualization (186 seconds)

### Task

Give dsh a synthetic JSON file with dirty data (52 rows: missing values, type errors, duplicate rows, outlier value 99999), and ask it to:
1. Analyze data quality issues
2. Write a cleaning script `clean.py`
3. Write a visualization script `visualize.py` (generating `chart.png`)
4. Run both scripts to verify

### How dsh Did It (Tool Chain)

<!-- [style] 工具链示意代码块统一补 text 语言标签 -->
```text
read(sales_data.json) → write(clean.py) → bash(python clean.py)
→ write(visualize.py) → bash(python visualize.py) → read(output) → summary
```

### Output & Verification

| Artifact | Result |
|---|---|
| `clean.py` | ✅ Runs successfully, 52 → **35 rows**, all issues resolved |
| `visualize.py` + `chart.png` | ✅ Valid PNG generated (1950×825) |
| Cleaning strategy | Median imputation for missing amounts, outlier removal, deduplication, type normalization |

![dsh-generated sales visualization (Case A artifact)](./assets/case-chart.png)

### Output Highlights (Shows Judgment, Not Just Mechanical Execution)

> - Median imputation creates a 510 spike in the histogram — an inherent side effect of imputation, worth noting
> - If 99999 represents a genuine large order, consider IQR/quantile methods instead of blanket deletion
> - Post-cleaning stats: N=35, mean 489.43, median 510, std dev 181.73

**dsh didn't just execute the task — it proactively explained the trade-offs and assumptions in data processing.** This is evidence of "thinking" at the agent engineering layer.

## Case B: 5-Bug Code Fix + 49 Tests (94 seconds)

### Task

Give dsh a Python calculator module **deliberately seeded with 5 bugs**, and ask it to: find all bugs → fix them → write comprehensive unit tests → run and verify.

### The Planted Bugs

1. `add` mistakenly written as `a - b`
2. `divide` silently returns 0 on division by zero (should throw)
3. `factorial` silently returns -1 for negative input (should throw)
4. `factorial`'s `range(1, n)` misses multiplying by n
5. `format_money` doesn't format to two decimal places

### dsh's Fixes + Tests (Verification: 49 passed)

Full test file: [case-test-calculator.py](./assets/case-test-calculator.py) — 49 test cases covering:

| Function | Coverage |
|---|---|
| `add` | Positive / negative / zero / float / precision / commutativity |
| `subtract` | Negative results / zero boundary / float |
| `multiply` | Sign combinations / multiply by zero / float |
| `divide` | Integer division / signs / float / **division by zero must throw ZeroDivisionError** |
| `factorial` | 0!/1! boundary / known values / **negative must throw ValueError** |
| `format_money` | Zero-padding / rounding / **0.1+0.2 rounding** / negative |

```bash
python -m pytest test_calculator.py -v   # 49 passed in 0.37s
```

### Observations: dsh's Performance

- **Full closed loop:** Read → fix → write tests → run tests → summarize, with no human intervention
- **Fix quality:** All 5 bugs fixed, with docstring explanations added
- **Test design:** Covers edge cases (division by zero / negatives / precision), not just "does it run"

## Case Summary: dsh's Profile on Complex Tasks

| Dimension | Performance |
|---|---|
| Multi-step tool chain | ✅ Auto-orchestrated (read → write → run → verify → summarize) |
| Complex task timing | 94s–186s (same model, same gateway; slower than benchmark simple tasks but manageable) |
| Output quality | ✅ Shows judgment (data trade-off explanations, test edge-case design) |
| Artifact tracking | ✅ Generated files can be opened directly at the end of the conversation |
| Failure recovery | Not triggered in these cases; production recommendation: pair with guard timeouts + human approval |

**Takeaway for newcomers:** dsh excels at tasks involving "multiple files, multiple steps, and verification" — which is also its primary value proposition as an agent runtime. For complex tasks, the recommendation is to **write acceptance criteria clearly in the prompt** (e.g. "run to verify"), and dsh will follow through to completion.

---

## Hands-on exercises

1. **Reproduce Case A**: create a synthetic JSON file with dirty data (missing values, type errors, duplicates, outliers). Give it to dsh with the same prompt. Compare your results with the case study.
2. **Reproduce Case B**: create a Python module with 5 planted bugs. Ask dsh to find and fix them, then write tests. How many bugs does it find? How many tests does it write?
3. **Prompt variation**: run Case A twice. First time, say "clean the data." Second time, say "clean the data, run and verify, and explain your trade-offs." Compare the output quality.
4. **Timing analysis**: measure how long each step takes (read, write, bash, verify). Which step is the bottleneck? How does this compare to the 90% / <1% split from Chapter 6?
5. **Failure injection**: give dsh an impossible task (e.g. "fix this code, but don't run the tests"). Does it still try to verify? What happens when the acceptance criteria are unclear?
6. **Think**: why does dsh "show judgment" (explain trade-offs, design edge-case tests)? Is this a feature of the model, the harness, or the prompt?

## FAQ

- **Q: Are these real-world cases or synthetic?** Synthetic. The data and code are self-authored to demonstrate capabilities. No real business data is involved.
- **Q: Why 94 seconds for Case B?** That's the total wall-clock time for reading the code, finding 5 bugs, fixing them, writing 49 tests, running them, and summarizing. Most of the time is model thinking (Chapter 6).
- **Q: What if dsh misses a bug?** In Case B, it found all 5. But in general, the quality depends on the prompt. If you say "find all bugs," it will try. If you say "fix the obvious bugs," it might miss subtle ones.
- **Q: Can I use dsh for production data cleaning?** Yes, but review the output. dsh explains its trade-offs (e.g. "median imputation creates a spike"), but you should verify the cleaning logic matches your business rules.
- **Q: What's the "artifact tracking" mentioned in the summary?** Tool returns carry `locations` (file paths). dsh uses these to build "artifact file lines" — the artifact chips at the end of the conversation. You can click to open each file.
- **Q: How do I handle failure recovery in production?** Pair dsh with guard timeouts (to prevent infinite loops) and human approval (for sensitive operations). The `guard/*` and `interaction/*` packages provide these capabilities.

---

**Appendix A**: [Glossary & Command Quick Reference](./appendix-glossary.md)
