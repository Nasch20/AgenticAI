# TD 2 - Step 3: Routing Rule (Pair C)

**Source:** `traces-td1.csv` (100 cells, 5 models × 20 questions, batch of 2026-10-21) and `reference-td1.csv`. No new network calls.  
**Status:** TD 1 rates computed from traces, prices from `portefeuille-modeles-en` (snapshot of 28 September 2026), and simulator run before and after adaptation.

---

## 1. Question Families

Family assignments determined from the wording of each question:

| Family | Cells |
| :--- | :--- |
| **F1** (Period) | C01, C04, C05, C06, C07, C20 |
| **F2** (Completed age at a date) | C02, C08, C09, C11 |
| **F2b** (Age at the order) | C10 |
| **F3** (Product list) | C12 |
| **F1 + F3** | C03, C13, C14 |
| **F1 + F2** | C15 |
| **F2 + F3** | C16 |
| **F1 + F2 + F3** | C17, C19 |
| **F1 + F2b** | C18 |

---

## 2. Exact TD 1 Rates (Correct / Cases)

### Performance Matrix
| Family | gpt-oss-120b | gpt-oss-20b | north-mini-code:free | qwen3.8-27b | dots-3-note-preview:free |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **F1** | 6/6 | 6/6 | 6/6 | 5/6 | 6/6 |
| **F2** | 4/4 | 1/4 | 0/4 | 4/4 | 3/4 |
| **F2b** | 1/1 | 1/1 | 0/1 | 1/1 | 1/1 |
| **F3** | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 |
| **F1+F3** | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| **F1+F2** | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| **F2+F3** | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| **F1+F2+F3** | 1/2 | 2/2 | 0/2 | 0/2 | 1/2 |
| **F1+F2b** | 1/1 | 1/1 | 0/1 | 1/1 | 0/1 |
| **Total** | **19/20** | **17/20** | **11/20** | **15/20** | **15/20** |

### Detailed Trace Failures
| Cell | Reference | 120b | 20b | north | qwen | dots |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C02** | 590320 | ok | 0 | sql_invalid | ok | ok |
| **C07** | 13970 | ok | ok | ok | sql_rejected | ok |
| **C08** | 605580 | ok | 25920 | sql_invalid | ok | 25920 |
| **C09** | 487980 | ok | ok | 0 | ok | ok |
| **C10** | 558980 | ok | ok | sql_invalid | ok | ok |
| **C11** | 446690 | ok | 322160 | 0 | ok | ok |
| **C15** | 168680 | ok | ok | 314020 | 0 | 138920 |
| **C16** | 376740 | ok | ok | ok | 367050 | 218760 |
| **C17** | 258180 | 80190 | ok | 197080 | 248490 | 152730 |
| **C18** | 62480 | ok | ok | 157610 | ok | 39580 |
| **C19** | 1990 | ok | ok | 13930 | 83580 | ok |

### Trace Observations
* **Without age conditions** (F1, F3, F1+F3: 10 questions), all models are correct except Qwen on C07, which was a markdown formatting failure (`sql_rejected`) rather than a logic error.
* **With age conditions** (10 questions), performance drops significantly for free models: North 1/10, Dots 5/10.
* **Model 20b** scored 1/4 on F2 alone but 5/5 on combinations containing age conditions. (Note: 20 questions support a batch-specific hypothesis, not a general error ranking).
* **C17 anomaly:** Only 20b is correct; the other four models return four different incorrect values. No free model alone is sufficient, and no quorum can decide.

### Quorum Behavior on Traces
* **2-of-3 fixed panel** (120b, North, Qwen): Abstains on C15, C17, C19; correct on the remaining 17.
* **3-of-5 panel**: Abstains on C08, C15, C17; correct on the remaining 17.
* Neither quorum returns an incorrect value on this batch. The shared wrong value `25920` on C08 (20b and Dots) receives 2 out of 5 votes, blocking the 3-of-5 quorum, while the 2-of-3 panel retains the correct value.

---

## 3. Routing Rule

### Pricing (Portfolio Snapshot: 28 September 2026)
* **`openai/gpt-oss-20b` (Groq, free):** 0 USD
* **`qwen/qwen3.8-27b` (Groq, free):** 0 USD
* **`openai/gpt-oss-120b` (Groq, free):** 0 USD
* **`cohere/north-mini-code:free` (OpenRouter, free):** Free by identifier (not in snapshot)
* **`dots-studio/dots-3-note-preview:free` (OpenRouter, free):** Free by identifier (not in snapshot)
* **`openai/gpt-oss-120b` (OpenRouter, paid route):** 0.15 USD/M input, 0.60 USD/M output (~0.000242 USD per request based on mean TD 1 token counts).

### Tie-Break Logic for Free Routes
Since all five models operate on free routes, price does not differentiate them. 
* **Tie-break rule:** Among models with 100% accuracy on a family, call first the one with the **lowest TD 1 total** (North: 11, Dots: 15, Qwen: 15, 20b: 17, 120b: 19). This preserves the quotas of stronger models for families only they can handle. 
* The paid 120b route acts as a fallback when free routes are exhausted and requests cannot wait.

### Routing Table

| Family | First Model | Justifying TD 1 Cells | Internal Dashboard | Customer-Facing Figure | Payout Amount | Fallback Sequence if Unavailable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F1** | `north:free` | 6/6 on C01, C04, C05, C06, C07, C20 | None | 2-of-3 quorum | 3-of-5 quorum | dots, then 20b, then 120b (6/6 each) |
| **F3** | `north:free` | 1/1 on C12 | None | 2-of-3 quorum | 3-of-5 quorum | dots, qwen, 20b, 120b (1/1 each) |
| **F1+F3** | `north:free` | 3/3 on C03, C13, C14 | None | 2-of-3 quorum | 3-of-5 quorum | dots, qwen, 20b, 120b (3/3 each) |
| **F2** | `qwen` | 4/4 on C02, C08, C09, C11 | 2-of-3 quorum | 3-of-5 quorum | 3-of-5 + reference | 120b (4/4); if Groq exhausted: wait for refill, paid 120b if urgent, else abstain |
| **F2b** | `dots:free` | 1/1 on C10 | 2-of-3 quorum | 3-of-5 quorum | 3-of-5 + reference | qwen, 20b, 120b (1/1 each) |
| **F1+F2b** | `qwen` | 1/1 on C18 | 2-of-3 quorum | 3-of-5 quorum | 3-of-5 + reference | 20b, 120b (1/1 each) |
| **F1+F2** | `20b` | 1/1 on C15 | 2-of-3 quorum (abstain expected) | Reference | Reference | 120b (1/1), else abstain |
| **F2+F3** | `north:free` | 1/1 on C16 | 2-of-3 quorum | 3-of-5 quorum | Reference | 20b, 120b (1/1 each) |
| **F1+F2+F3**| `20b` | 2/2 on C17, C19 | 2-of-3 quorum (abstain expected) | Reference or review | Review | Wait for refill if able to wait, else abstain |

* **Fallback behavior:** If no eligible free model is available, wait for the refill if the request can wait; otherwise, use the paid 120b route if eligible and within budget; otherwise, abstain.

### Error Cost Justifications
* **Internal Dashboard:** Errors are caught internally. "None" is permitted only when a free model achieved 100% accuracy on that family (F1, F3, F1+F3).
* **Customer-Facing Figure:** Errors impact external trust. Requires at least a quorum.
* **Payout Amount:** Errors incur financial loss. Requires maximum quorum plus deterministic reference checks on any family involving age conditions.
* **Abstention Handling:** When quorums abstain, requests escalate to reference verification or human review rather than relying on a single model.

---

## 4. Simulator

**Files:** `atelier-routage-original.py` (supplied), `atelier-routage.py` (adapted), `simu-avant.txt`, `simu-apres.txt`.

### Before Adaptation (`simu-avant.txt`)
| Scenario | Action | Resource | Cash | Checks | Reason |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **simple** | run | small-free | 0.00 | read-only execution and value check | eligible included capacity |
| **complex** | run | senior-subscription | 0.00 | read-only execution and value check | eligible included capacity |
| **deferrable** | defer (60 min) | senior-subscription | 0.00 | read-only execution and value check | recheck availability at wake-up |
| **urgent** | run | senior-api | 0.30 | read-only execution and value check | available route within authorised budget |
| **budget exhausted** | abstain | none | 0.00 | read-only execution and value check | no eligible resource within deadline and budget |
| **high impact** | run | senior-subscription | 0.00 | source verification and human review | eligible included capacity |
| **unknown capability**| abstain | none | 0.00 | read-only execution and value check | no eligible resource within deadline and budget |

### Summary of Adaptations
* **`RESOURCES`:** Replaced fictitious resources with our 5 TD 1 models on free routes (cash 0) plus the paid OpenRouter route for `gpt-oss-120b` (0.000242 USD/request).
* **Eligibility:** Capability levels (1/2/3) replaced by TD 1 accuracy per family (`td1`). Models are eligible only if 100% correct on the requested family.
* **Tie-break:** `level` replaced by TD 1 total score, prioritizing weaker eligible free models first.
* **Requests & Checks:** `difficulty` mapped to `family`, `high_impact` mapped to `use` (dashboard, customer, payout), and checks derived from Section 3.
* **Reasons:** Appended TD 1 performance ratios and cell references to decision reasons.
* **Scenarios:** Added an 8th scenario ("included before deferral") where an exhausted free route can wait, but an alternative free resource is immediately available.

### After Adaptation (`simu-apres.txt`)
| Scenario | Family, Use, Situation | Action | Resource | Cash | Checks | Reason |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **simple** | F1, dashboard | run | `north:free` | 0.00 | none | eligible included capacity; TD1 6/6 on C01 C04 C05 C06 C07 C20 |
| **complex** | F2, dashboard | run | `qwen` | 0.00 | 2-of-3 quorum | eligible included capacity; TD1 4/4 on C02 C08 C09 C11 |
| **deferrable** | F2, dashboard, Groq exhausted, can wait | defer (60 min) | `qwen` | 0.00 | 2-of-3 quorum | recheck availability at wake-up; TD1 4/4 on C02 C08 C09 C11 |
| **urgent** | F2, dashboard, Groq exhausted, 5 min | run | `120b paid` | 0.000242 | 2-of-3 quorum | available route within authorised budget; TD1 4/4 on C02 C08 C09 C11 |
| **budget exhausted** | F2, dashboard, Groq exhausted, budget 0 | abstain | none | 0.00 | 2-of-3 quorum | no model with 100% in TD1 on F2 reachable within deadline/budget |
| **high impact** | F2, payout | run | `qwen` | 0.00 | 3-of-5 + ref | eligible included capacity; TD1 4/4 on C02 C08 C09 C11 |
| **unknown capability**| F4 (non-existent family) | abstain | none | 0.00 | review | no TD1 cell for family F4: eligibility unknown |
| **included before deferral**| F1, dashboard, OpenRouter exhausted, can wait | run | `20b` | 0.00 | none | eligible included capacity; TD1 6/6 on C01 C04 C05 C06 C07 C20 |

---

## 5. Priority Order in the Supplied `choose` Function

The supplied function evaluates four conditional branches in order:
1. `included`: eligible, available, `cash == 0` $\rightarrow$ **run**.
2. `waiting`: eligible, unavailable, `cash == 0`, reset before `deadline_minutes`, and `can_wait` $\rightarrow$ **defer**.
3. `paid`: eligible, available, `cash <= budget` $\rightarrow$ **run**.
4. Otherwise $\rightarrow$ **abstain**.

### Rationale & Inversion Conditions
* **Why available subscription wins over waiting for exhausted free resources:** A subscription with `allocation > 0` has `cash == 0` and `available == True`, entering branch 1 immediately. Exhausted free resources (`available == False`) fall into branch 2, which is never evaluated if branch 1 is populated. This aligns with the principle that pre-paid capacity should be used before new spending, and reset times do not guarantee immediate post-reset availability. Executing immediately on the subscription incurs zero cash cost while eliminating latency and availability risks.
* **Tie-break within branch 1:** Sorting by `allocation` ensures that available free resources (allocation 0) are chosen before subscription quotas (allocation 0.04).
* **When to reverse priority:** Priority should reverse when subscription quotas are strictly rationed and must be reserved for complex/urgent requests that only senior models can handle. If the current request can tolerate waiting for a free-tier refill well before its deadline, deferring preserves subscription quota. Operational safeguards must ensure sufficient deadline buffer to fall back on paid options if free capacity fails to materialize at wake-up.

---

## 6. Limits

* Data is based on 20 questions from a single batch with one attempt per cell (batch-specific hypothesis).
* Several families contain only one or two questions.
* Family categorizations were determined independently by the sub-group.
* North and Dots models are absent from the official snapshot; treated as free routes based on their identifiers.
* Prices reflect the 28 September 2026 snapshot; paid route per-request costs utilize mean token counts from TD 1 traces.
* Free model tie-break logic (lowest TD 1 total first) is an internal sub-group heuristic rather than an official module rule.