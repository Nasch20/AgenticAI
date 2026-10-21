# TD1 — Comparing five AI models on SQL questions

**Course:** Next Generation AI     
**Date of experiment:** 21 October 2026  
**Repository:** https://github.com/Nasch20/AgenticAI

## 1. Work attempted and completed

We first checked that our Python environment, SQLite database and input CSV files were set up correctly. The environment check confirmed the expected dataset of 5 products, 59 customers and 397 order lines, with matching data fingerprints.

We then worked through the 20 questions (C01–C20) and prepared a SQL reference for each one. We checked our SQL totals using a second implementation that reads `orders.csv`, `customers.csv` and `product.csv`, so that we did not rely only on the SQL result. All 20 calculated SQL totals matched our CSV calculations. This matching result is a useful check, although we also need human review of the interpretation of each question.

We configured our Groq and OpenRouter API access. We initially encountered configuration issues (missing or incorrectly entered environment variables and failed API checks), which we corrected before running the evaluation. We also synchronized our shared project through GitHub, handling local trace files carefully to avoid overwriting results.

We tested five models against the same 20 questions, for **100 model-question evaluations**. We saved their generated SQL, the value returned when a query could be executed, the reference value, the evaluator verdict and the related request metadata. We then prepared two comparison tables to analyze the results.

## 2. Results and evidence

The 100 recorded evaluations contained **77 correct outputs** and **23 non-correct outputs** (19 incorrect values, 3 invalid SQL queries, and 1 SQL query rejected by the SQL safety/format check). Every recorded API request received HTTP 200, so the non-correct outcomes in this dataset were not HTTP access failures.

| Model | Tested | Correct | Incorrect value | Invalid SQL | SQL rejected | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| GPT-OSS 120B | 20 | 19 | 1 | 0 | 0 | 95% |
| GPT-OSS 20B | 20 | 17 | 3 | 0 | 0 | 85% |
| North Mini Code | 20 | 11 | 6 | 3 | 0 | 55% |
| Qwen 27B | 20 | 15 | 4 | 0 | 1 | 75% |
| Dots | 20 | 15 | 5 | 0 | 0 | 75% |

GPT-OSS 120B achieved the highest observed accuracy, **19/20 (95%)**, while North Mini Code achieved **11/20 (55%)**. These are results for this particular run and dataset, not general rankings of model quality.

**Files to consult (paths relative to this report):**

- [Reference SQL queries and verified values](../reference-td1.csv)
- [All evaluated model outputs and verdicts](../traces-td1.csv)
- [Detailed JSONL traces](../traces-td1.jsonl)
- [100-row model–question comparison](../model-question-comparison-en.csv)
- [Five-model summary](../five-model-summary-en.csv)
- [Evaluator/orchestration script](../skeleton-multi-llm-en.py)
- [Prompt record — add this file to the repository](../prompts-en.md)

The recorded prompt hash is the same across all five models for a given case (20 out of 20 cases). This supports the fact that we applied a consistent prompt configuration to each model for each question. The actual system message and user prompt template must also be copied into `prompts-en.md`, including any changes, so that this can be audited.

## 3. Successes, failures and possible explanations

**What worked.** We successfully prepared 20 reference answers, collected all 100 expected model/question cells and preserved a trace for each evaluation. All 100 rows were marked as real evaluations, and all recorded HTTP statuses were 200. The prompt hashes were also consistent between models for each case.

**Age calculation was a recurring source of mistakes.** For C02, GPT-OSS 20B generated a birth-date interval in 2025–2026, which corresponds to much younger customers, instead of people aged 25 on 25 September 2026. Its answer was 0 cents while the reference was 590,320 cents. We therefore think that some models misinterpreted "exactly 25 years old" as a simple or incorrect date comparison rather than computing the completed age at a particular date.

**C17 combined several filters and was especially difficult.** Four of the five models failed this case. GPT-OSS 120B selected people born on a single date (`birth_date = DATE('2026-09-25', '-25 years')`) instead of the entire range of birth dates for people aged 25 on that date. It returned 80,190 cents instead of the reference 258,180 cents. This is a directly observed cause for that response. Our broader hypothesis is that combining an age condition with product and time filters increases the chances of mistakes in boundary logic.

**Some models produced invalid or improperly formatted SQL.** North Mini Code generated three queries that SQLite could not parse (C02, C08 and C10). Qwen's C07 response included a Markdown SQL code fence, which the evaluator rejected because it was not a bare `SELECT` statement. This illustrates that formatting compliance matters in addition to logical correctness.

These observations are based on the saved generated SQL and evaluator verdicts; they are not proof of the models' internal reasoning processes.

## 4. Limitations

We evaluated only 20 questions on one small, fixed, seeded dataset. We therefore cannot generalize the scores to other SQL tasks or databases. We ran **one recorded attempt per model–question cell**, so our results do not measure run-to-run variability or reliability across repeated calls. A different sampling configuration or a repeated run could change the outcomes.

Our evaluation mainly measures whether the generated query produces the expected revenue in cents on this database. A query could theoretically return the correct total for the wrong reason, so equality with the reference value is not a complete proof of semantic correctness. We also compared models across two providers, where latency, quotas, and hosting conditions may differ. We should be careful not to interpret latency or publicly listed prices as controlled comparisons unless we normalize these conditions.


## 5. Real, replayed and synthetic material

All **100 rows in `traces-td1.csv` are explicitly labeled `nature=real`**. We found no row marked as replayed or synthetic in this submitted comparison dataset. The recorded attempts field is 1 for each cell. Any separate demo, simulated, or replayed material should be labeled as such and kept out of these real-evaluation statistics unless reported separately. If we add screenshots or examples that were reconstructed for presentation, we will identify them as reconstructed rather than real runs.

## 6. Next steps

For TD2, we plan to use the mistakes observed in TD1 to improve our approach: validate SQL syntax before execution, check date and age boundaries more systematically, and preserve complete traces for reproducibility. We also want to keep the same reference data, use clear, consistent prompts, and distinguish model reasoning errors from SQL formatting errors. Before final submission, we will check the prompt record, obtain the team's contribution details, complete the README, and verify that all linked files are accessible in the GitHub repository.
