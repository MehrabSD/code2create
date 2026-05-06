# Limitations — Phantom Consensus Engine

## Known Limitations

### 1. Fixed Thresholds
The engine uses hardcoded thresholds (betrayal ≥ 0.7 for Trojan Horse, controversy ≥ 0.4 for Poison Pill, etc.). These work well for the provided data but may need tuning for different datasets. A more adaptive approach would calculate thresholds relative to the data distribution.

### 2. Supporter Coherence is Heuristic
Supporter selection balances objection burden, betrayal risk, and influence. This is stronger than a hard yes/no objector rule, but still heuristic and may over- or under-filter in edge political configurations.

### 3. Single-Pass Deduplication
Duplicate proposals keep the first occurrence. If the second occurrence has better data (e.g., corrected priority), it is lost. A merge strategy could be more appropriate.

### 4. No Weighted Alliance Scoring
Alliances are binary (above threshold = allied, below = not). A graduated alliance strength metric could provide more nuanced results.

### 5. No Iterative Optimization
The consensus is built in a single pass. An iterative approach (e.g., removing a proposal to gain more supporters, then recalculating) could find globally better solutions.

### 6. Faction Infiltrator Detection Requires Relations Data
If a suspected infiltrator has no outgoing relations to same-faction members in the CSV, they cannot be detected. The engine relies on explicit relationship data.

### 7. No Temporal Analysis
The relations.csv includes `last_interaction` dates, but these are not used. Older relationships may be less relevant than recent ones.

### 8. Default Values for Missing Data
Null influence defaults to 50 (midpoint). This is arbitrary and may over- or under-represent the rep's true power. Similarly, missing trust defaults to 50.
