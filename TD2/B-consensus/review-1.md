While analyzing our traces, we identified a notable case of wrong agreement, the case C08, where two distinct models (`groq:openai/gpt-oss-20b` and `openrouter:dots-studio/dots-3-note-preview`) independently returned the exact same incorrect revenue value (`25,920` instead of `605,580`).

**Root Cause:** Both models used a `WHERE` clause that was far too restrictive. GPT-OSS-20B only selected customers born on September 23 or 24, 2001, while Dots 3 only selected customers born on September 24, 2001, instead of all customers who were exactly 25 years old on September 24, 2026 (born between September 25, 2000 and September 24, 2001).

**Impact:** Because both models agreed on the wrong figure, a naive quorum including these two models could treat it as valid, demonstrating that **agreement without independent verification can propagate systematic logic errors**.

**2-out-of-3 Quorum Result:** Correct consensus (accepted). The fixed panel contains GPT-OSS-120B, Cohere North Mini Code and Qwen 27B. Since GPT-OSS-120B and Qwen both returned the correct value (605580), the 2-out-of-3 quorum threshold was met, leading to the correct validation of this information. Cohere returned an invalid SQL query and did not contribute a vote.

**3-out-of-5 Quorum Result:** Abstention (rejected). With an expanded panel of 5 models, 2 agreed on the incorrect value (25920), 2 agreed on the correct value (605580), and 1 returned invalid SQL. Neither value reached the 3-out-of-5 threshold, thereby preventing the error from propagating.

**delta query on data/boutique.sqlite :**

```text
MODEL: GPT-OSS-20B
Reference: 605580 cents
Model result: 25920 cents
Difference: 579660 cents

Customers missed by GPT-OSS-20B:
C004 | 2000-09-25 | 150260 cents
C005 | 2000-09-26 | 150240 cents
C007 | 2000-11-30 | 118740 cents
C008 | 2001-05-15 | 99090 cents
C009 | 2001-03-10 | 61330 cents

Number of missed customers: 5
Total missed revenue: 579660 cents
Difference explained: True

MODEL: Dots 3
Reference: 605580 cents
Model result: 25920 cents
Difference: 579660 cents

Customers missed by Dots 3:
C004 | 2000-09-25 | 150260 cents
C005 | 2000-09-26 | 150240 cents
C007 | 2000-11-30 | 118740 cents
C008 | 2001-05-15 | 99090 cents
C009 | 2001-03-10 | 61330 cents

Number of missed customers: 5
Total missed revenue: 579660 cents
Difference explained: True

Same wrong value: True
```
