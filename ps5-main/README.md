# Phantom Consensus

## Team Information
- **Team Name**: Lazarus
- **Year**: 2028
- **All-Female Team**: No

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

We used a six-stage pipeline: load, clean, engineer features, apply strategic filters, build consensus, and format output. Cleaning normalizes IDs (trim + lowercase), safely casts malformed values, clamps outliers (influence/trust/rivalry to 0-100, betrayal to 0-1), maps non-numeric severities to defaults, removes duplicates, and drops ghost references (invalid sponsors, objections, or relations). Alliance logic uses bidirectional relationship score = trust × (1 - betrayal_prob), requires both directions above threshold, rejects asymmetric pairs via min/max ratio checks, and suppresses unstable pairs with strong policy conflict. Proposal priority is not taken at face value: objection_weight = sum(severity × objector_influence), controversy is normalized objection pressure, and viability = priority × (1 - controversy); proposals are ranked by viability and trimmed to a compact set. Stability is enforced by excluding high-risk reps (Trojan patterns from high betrayal/deceptive trust-betrayal signals), rejecting Poison Pill proposals with severe broad opposition, and selecting supporters via coherence plus risk-aware filtering so selected supporters are strategically reliable.

- How did you approach cleaning the raw data, including handling missing values, inconsistent formats, and outliers?
- What logic did you use to detect underlying alliances and evaluate the impact of asymmetric trust and betrayal probabilities?
- How did you prioritize proposals given varying objection severities and differing levels of influence among objectors?
- Describe the strategy used by your consensus engine to maintain a stable agreement while avoiding "Trojan Horse" candidates and "Poison Pill" proposals.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
