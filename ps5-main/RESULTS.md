# Results — Phantom Consensus Engine

## Input Summary

| Dataset | Raw Records | After Cleaning | Notes |
|---|---|---|---|
| Representatives | 8 | 6 | 2 duplicates removed (REP_001, " rep_004") |
| Proposals | 6 | 4 | 1 duplicate (prop_003), 1 ghost sponsor (prop_005→rep_099) |
| Objections | 8 | 6 | 1 ghost objector (rep_099), 1 duplicate merged |
| Relations | 16 | 15 | 1 duplicate row removed |

## Cleaned Representatives

| ID | Name | Faction | Influence (raw → clean) |
|---|---|---|---|
| rep_001 | Senator Aria | Progressives | 85 |
| rep_002 | Councilor Blake | Moderates | "70" → 70 |
| rep_003 | Minister Chen | Conservatives | 95 |
| rep_004 | Delegate Davis | Progressives | null → 50 |
| rep_005 | Ambassador Ellis | Moderates | 150 → 100 (clamped) |
| rep_006 | Director Fox | Independents | 92 |

## Strategic Findings

### Trojan Horses Detected
- **rep_005** (Ambassador Ellis): Has relation to rep_006 with betrayal_prob=1.0 (clamped from 1.5). Despite high influence (100), including them destabilizes the agreement.
- **rep_006** (Director Fox): Average betrayal probability 0.78 across outgoing relations. High influence (92) is a trap.

### Poison Pill Proposals
- **prop_004** (Emergency Response Protocol): 3 out of 4 safe reps object (75%). controversy=0.29, but majority objection makes it unviable.

### Alliances Detected
- **rep_001 ↔ rep_004**: Bidirectional scores 80.8 / 88.2. Both Progressives, low betrayal in both directions (0.05, 0.02). Genuine alliance.

### Ghost References Removed
- **prop_005** ("Orphaned Proposal"): Sponsor rep_099 does not exist.
- **Objection from rep_099**: Ghost objector removed.

## Final Output

```json
{
  "final_agreement": {
    "proposals": ["prop_003", "prop_002"],
    "supporting_reps": ["rep_003", "rep_002", "rep_004"]
  },
  "alliances": [["rep_001", "rep_004"]]
}
```

### Why These Proposals?
1. **prop_003** (Environmental Protection Initiative): Highest viability (8.82). Only 1 objector.
2. **prop_002** (Budget Reconciliation Framework): High viability (8.62). Priority 10 with low controversy.
3. **prop_001** (Infrastructure Modernization Act): Viability 6.76 but not selected in the final compact agreement after strategic trimming.

### Why These Supporters?
- **rep_005**, **rep_006** are excluded as Trojan Horses.
- **rep_001** is excluded due to objection burden against selected proposals.
- **rep_002**, **rep_003**, and **rep_004** remain coherent with the selected proposal set and pass strategic risk filters.

## Performance
- Execution time: ~5ms on sample data.
- Algorithm complexity: O(n²) for relationship analysis, O(n×m) for objection weights.
