# Phantom Consensus Engine — Test Suite

## Structure

```
phantom_tests/
├── README.md               ← This file
├── scorer.py               ← Run this to score your engine
├── scenario_01/            ← Trojan Horse Detection
│   ├── data/
│   │   ├── representatives.json
│   │   ├── proposals.json
│   │   ├── objections.json
│   │   └── relations.csv
│   └── meta.json           ← Expected output + scoring rubric
├── scenario_02/ ...
│   ...
└── scenario_18/
```

## How to Use

### Step 1 — Run your engine on each scenario
For each scenario, point your `consensus_engine.py` at `scenario_XX/data/` as the input folder.
Save the output as `scenario_XX_output.json` in a single folder (e.g., `my_outputs/`).

### Step 2 — Run the scorer
```bash
python3 scorer.py my_outputs/
```

### Step 3 — Read your score
The scorer prints a full breakdown and a final score out of 100.

---

## Scenario Overview

| # | Name | Weight | What It Tests |
|---|------|--------|---------------|
| 01 | Trojan Horse Detection | 10 | Exclude high-influence but high-betrayal reps |
| 02 | Poison Pill Rejection | 10 | Reject priority-10 proposals with universal objections |
| 03 | Asymmetric Trust | 8 | False Friend — one-sided trust ≠ alliance |
| 04 | Ghost Sponsor | 5 | Drop proposals from non-existent sponsors |
| 05 | ID Normalisation | 5 | Handle REP_001, " rep_002" → rep_001, rep_002 |
| 06 | Dirty CSV Handling | 5 | trust="", rivalry="high", betrayal_prob=1.5 |
| 07 | Faction Infiltrator | 8 | Rep betrays >60% of own faction peers |
| 08 | Supporter Coherence | 8 | Objectors cannot be supporters |
| 09 | Clear Alliance | 6 | Detect strong bidirectional trust pair |
| 10 | Minimum Viable | 3 | 1 rep, 1 proposal — still works |
| 11 | Complete Rivalry | 5 | All rivalries → alliances = [] |
| 12 | Duplicate Proposals | 4 | Higher priority wins deduplication |
| 13 | Null Influence | 4 | null/string/out-of-range influence values |
| 14 | Scale Correctness | 5 | 15 reps, 10 proposals — structural validity |
| 15 | Priority vs Objection Weight | 8 | Objection weight beats raw priority |
| 16 | Cascading Betrayal | 6 | Max betrayal excludes rep from supporters |
| 17 | Alliance Hijack | 6 | Infiltrator can't break stable alliance |
| 18 | Faction War | 4 | Compromise proposal beats faction proposals |

**Total weight: 110 → normalised to 100**

---

## Scoring Rubric (per scenario)

| Ratio | Meaning |
|-------|---------|
| 1.0 (100%) | Full credit — proposals, supporters, alliances all correct |
| 0.6 (60%) | Partial — proposals correct + one of supporters/alliances |
| 0.4 (40%) | Partial — proposals correct only |
| 0.3 (30%) | Partial — supporters correct only |
| 0.0 (0%) | Zero — wrong core decision |

## Tier Table

| Score | Tier | Meaning |
|-------|------|---------|
| 90–100 | S | Exceptional — handles everything |
| 75–89 | A | Strong — handles most cases |
| 60–74 | B | Competent — basic strategy works |
| 45–59 | C | Acceptable — passes format, naive logic |
| 30–44 | D | Weak — barely functional |
| 0–29 | F | Failing |

## Output Format Expected

Each `scenario_XX_output.json` must follow this schema:
```json
{
  "final_agreement": {
    "proposals": ["prop_001", "prop_002"],
    "supporting_reps": ["rep_001", "rep_003"]
  },
  "alliances": [
    ["rep_001", "rep_002"]
  ]
}
```

---

## New Scenarios (19–30)

| # | Name | Weight | Core Trap |
|---|------|--------|-----------|
| 19 | Decoy Alliance | 8 | trust=95 but rel_score<40 → no alliance |
| 20 | Shadow Sponsor | 7 | Trojan Horse can sponsor valid proposals but can't be supporter |
| 21 | Self-Objecting Sponsor | 7 | A rep objects to their own proposal — both viability and coherence apply |
| 22 | All-Null Influence | 5 | Every rep has influence=null — defaults must fire uniformly |
| 23 | The Kingmaker | 8 | Highest-reliability rep objected to a selected proposal — must be excluded |
| 24 | Proposal Laundering | 5 | Same proposal ID appears 3× with different priorities — highest wins |
| 25 | Thin Margin | 8 | Near-identical viability; objection weight (severity×influence) is the true tiebreaker |
| 26 | Zombie Alliance | 7 | Trojan Horse poisons one alliance but sibling alliances survive |
| 27 | Influence Cliff | 6 | Objector with influence=-50 clamped to 0 → zero-weight objection |
| 28 | Trust Vacuum | 6 | All trust=0 (not missing) → rel_score=0 everywhere → alliances=[] |
| 29 | Faction of One | 6 | Solo-faction reps cannot be infiltrators (no peers to betray) |
| 30 | The Grand Illusion | 12 | All four traps simultaneously: Trojan Horse + Poison Pill + False Friend + Ghost Sponsor |

