# Approach — Phantom Consensus Engine

## Architecture Overview

Our engine follows a **6-stage pipeline**: Load → Clean → Engineer Features → Strategic Analysis → Build Consensus → Output.

### Data Cleaning (Issues 6-9)
- **ID Normalization**: All representative IDs are stripped of whitespace and lowercased across all 4 files before any cross-referencing.
- **Type Casting**: Influence values cast from strings/null to integers, clamped to [0, 100]. Null influence defaults to 50. Severity strings like "high" mapped to numeric equivalents.
- **Deduplication**: First-occurrence-wins for duplicate proposal IDs and representative IDs. Duplicate objections (same rep + proposal) keep highest severity. Duplicate CSV rows are dropped.
- **Ghost Reference Removal**: Objections referencing non-existent reps/proposals are removed. Proposals with non-existent sponsors are excluded.

### Feature Engineering (Issues 10-11)
- **Relationship Score**: `trust × (1 - betrayal_prob)` — captures true reliability. A rep with trust=90 but betrayal=0.9 scores only 9 (dangerous), while trust=85, betrayal=0.05 scores 80.75 (reliable).
- **Objection Weight**: `Σ(severity × objector_influence)` per proposal — a powerful rep's objection matters more.
- **Proposal Viability**: `priority × (1 - controversy)` where controversy is normalized objection weight.

### Strategic Logic (Issues 12-16)
- **Trojan Horse Detection**: Reps are excluded when high influence combines with high betrayal risk, or when they show deceptive high-trust/high-betrayal behavior.
- **Poison Pill Rejection**: Proposals are rejected when controversy is high, or when majority objection is both broad and severe.
- **Alliance Detection**: Alliances require strong bidirectional relationship scores, asymmetry checks, and partner-ranking consistency to avoid false positives.
- **Faction Infiltrators**: Reps are flagged when betrayal toward same-faction peers is structurally high.
- **Cascading Betrayal**: 2-hop betrayal chains are detected and used as risk context for final supporter selection.

### Consensus Building (Issue 17)
- Proposals are ranked by viability and trimmed to a compact high-quality set.
- Supporters are selected by coherence, objection burden, betrayal risk, and influence.
- Excluded strategic risks (Trojan Horse/Infiltrator) are never included as supporters.

### Edge Cases (Issue 19)
- Empty data → empty output. Single valid rep/proposal → still works. Complete rivalry → empty alliances.

### Performance (Issue 20)
- All algorithms are O(n²) at worst (relationship pairs). No nested triple loops over full datasets. Processes 50+ reps and 30+ proposals within milliseconds.
