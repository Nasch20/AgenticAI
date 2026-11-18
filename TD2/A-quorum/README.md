## Part A - The k-of-n vote

### Implementation

We completed the vote_k_sur_n method in
skeleton-multi-llm-en.py.

The function counts the number of models that return
the same value. If a value reaches the required number
of votes, it is selected. Otherwise, the function abstains.

Models with errors stay in the panel but do not vote.
Duplicate models are not allowed.

### Quorum policy

We defined a quorum policy to organise the voting
process and apply the same rules to all models.

We used two configurations:

- 2-of-3: at least 2 models must agree.
- 3-of-5: at least 3 models must agree.

Each model has a maximum of two attempts.
Temporary errors can lead to a retry, but invalid
SQL queries are not retried.

We use the last attempt of each model.
Unavailable models remain in the panel but do not vote.

If no value reaches the required majority, the system
abstains instead of returning an unreliable answer.

The policy is versioned to keep track of any changes.
No new API calls were made during TD2.

### Synthetic tests

| Test | Result | Status |
|---|---|---|
| Agreement | Consensus: 100 | Passed |
| Disagreement | Abstention | Passed |
| Unavailable | Abstention | Passed |
| Wrong consensus | Consensus: 0 instead of 100 | Passed |

The last test shows that a consensus can be incorrect.

### Results on the 20 questions

All values are in cents.

| Case | Reference | 2-of-3 value | Votes | Correct | 3-of-5 value | Votes | Correct |
|---|---:|---:|---:|---|---:|---:|---|
| C01 | 792800 | 792800 | 3 | Yes | 792800 | 5 | Yes |
| C02 | 590320 | 590320 | 2 | Yes | 590320 | 3 | Yes |
| C03 | 936350 | 936350 | 3 | Yes | 936350 | 5 | Yes |
| C04 | 2826250 | 2826250 | 3 | Yes | 2826250 | 5 | Yes |
| C05 | 38480 | 38480 | 3 | Yes | 38480 | 5 | Yes |
| C06 | 0 | 0 | 3 | Yes | 0 | 5 | Yes |
| C07 | 13970 | 13970 | 2 | Yes | 13970 | 4 | Yes |
| C08 | 605580 | 605580 | 2 | Yes | Abstention | 2 | N/A |
| C09 | 487980 | 487980 | 2 | Yes | 487980 | 4 | Yes |
| C10 | 558980 | 558980 | 2 | Yes | 558980 | 4 | Yes |
| C11 | 446690 | 446690 | 2 | Yes | 446690 | 3 | Yes |
| C12 | 1666490 | 1666490 | 3 | Yes | 1666490 | 5 | Yes |
| C13 | 107740 | 107740 | 3 | Yes | 107740 | 5 | Yes |
| C14 | 0 | 0 | 3 | Yes | 0 | 5 | Yes |
| C15 | 168680 | Abstention | 1 | N/A | Abstention | 2 | N/A |
| C16 | 376740 | 376740 | 2 | Yes | 376740 | 3 | Yes |
| C17 | 258180 | Abstention | 1 | N/A | Abstention | 1 | N/A |
| C18 | 62480 | 62480 | 2 | Yes | 62480 | 3 | Yes |
| C19 | 1990 | Abstention | 1 | N/A | 1990 | 3 | Yes |
| C20 | 1106090 | 1106090 | 3 | Yes | 1106090 | 5 | Yes |

### Comparison

| Metric | 2-of-3 | 3-of-5 |
|---|---:|---:|
| Correct consensuses | 17 | 17 |
| Incorrect consensuses | 0 | 0 |
| Abstentions | 3 | 3 |
| Coverage | 85% | 85% |
| Accuracy among consensuses | 100% | 100% |

### Analysis of the differences

#### C08

GPT-OSS 120B and Qwen returned the correct value
605580. GPT-OSS 20B and Dots returned the incorrect
value 25920. Cohere produced invalid SQL.

The 2-of-3 quorum returned the correct value, but the
3-of-5 quorum abstained because no value reached 3 votes.

#### C15

GPT-OSS 120B and GPT-OSS 20B returned the correct
value 168680.

Cohere returned 314020, Qwen returned 0 and Dots
returned 138920. These three values were incorrect.

Both configurations abstained. The number of votes
increased from 1 to 2, but the required threshold
also increased from 2 to 3.

#### C19

GPT-OSS 120B, GPT-OSS 20B and Dots returned the
correct value 1990.

Cohere returned 13930 and Qwen returned 83580.
Both values were incorrect.

The 2-of-3 quorum abstained, while the 3-of-5 quorum
returned the correct value with 3 votes.

### Conclusion

Both configurations obtained 17 correct consensuses
and 3 abstentions.

Adding more models did not improve the overall
results on our 20 questions. However, it changed
the decisions for C08 and C19.

We also observed that several models can return the
same incorrect value, as in C08.

These results are limited to our TD1 dataset and
do not guarantee the same performance on other questions.

### Files

- [Voting method](skeleton-multi-llm-en.py)
- [Voting script](atelier-vote.py)
- [2-of-3 results](vote-td2.csv)
- [3-of-5 results](vote-td2-5.csv)
- [TD1 traces](../../TD1/traces-td1.csv)