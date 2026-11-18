# TD2 — Quorum and Routing Rule

This report provides an overview of our TD2 work. Detailed explanations, implementations and results are available in the folders linked below.

### Part A — K-of-N Voting

**Location:** [TD2/A-quorum](../TD2/A-quorum/README.md)

- Implemented `vote_k_sur_n` in `skeleton-multi-llm-en.py`.
- Tested the voting method using `atelier-vote.py`.
- Compared 2-of-3 and 3-of-5 quorums across all 20 TD1 questions.
- Results are available in `vote-td2.csv` and `vote-td2-5.csv`.

### Part B — Wrong Consensus

**Location:** [TD2/B-consensus](../TD2/B-consensus/README.md)

- Identified a shared incorrect answer from two models on question C08.
- Analyzed the faulty SQL conditions.
- Created `diagnostic_c08.py` to identify the missing customers and verify the revenue difference using SQLite.
- Documented the quorum decisions and the diagnostic results.

### Part C — Routing Rule

**Location:** [TD2/C-routing](../TD2/C-routing/README.md)

- Defined a routing rule based on TD1 model performance, cost and verification requirements.
- Adapted `atelier-routage.py` with our models and selection criteria.
- Tested the routing decisions on simulated scenarios.
- Results after adaptation are available in `simu-apres.txt`.

### Source Data

All three parts reuse the TD1 traces and reference values stored in `TD1/`. No new API calls were required for TD2.