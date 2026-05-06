"""
test_hidden.py — 18 Hidden Scenario Tests (Organizer Only)

Each test runs the participant's engine on a crafted scenario
and checks whether the output reflects correct strategic decisions.

Scoring per test: Full (max pts) / Partial (half) / Zero (0)
Total: 100 points across all 18 tests.
"""

import json
import os


def load_output(path):
    """Load consensus output JSON."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def norm(s):
    """Normalize an ID for comparison."""
    return str(s).strip().lower()


def get_output_data(output):
    """Extract proposals, supporters, alliances from output."""
    if not output:
        return set(), set(), []
    fa = output.get('final_agreement', {})
    props = set(norm(p) for p in fa.get('proposals', []))
    reps = set(norm(r) for r in fa.get('supporting_reps', []))
    alliances = [
        tuple(sorted(norm(x) for x in pair))
        for pair in output.get('alliances', [])
        if isinstance(pair, list) and len(pair) == 2
    ]
    return props, reps, alliances


# =====================================================================
# SCENARIO CHECK FUNCTIONS
# Each returns: (score_fraction, message)
#   score_fraction: 1.0 = full, 0.5 = partial, 0.0 = zero
# =====================================================================

def check_01_trojan_horse(output):
    """rep_002 (betrayal=0.95) must NOT be in supporters."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'rep_002' not in reps:
        return 1.0, "Correctly excluded Trojan Horse rep_002"
    else:
        return 0.0, "FAIL: Trojan Horse rep_002 is in supporters"


def check_02_poison_pill(output):
    """prop_001 (universally objected) must NOT be selected."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'prop_001' not in props and 'prop_002' in props:
        return 1.0, "Correctly avoided Poison Pill prop_001 and selected prop_002"
    elif 'prop_001' not in props:
        return 0.5, "Avoided Poison Pill but didn't select safe alternative"
    else:
        return 0.0, "FAIL: Selected Poison Pill prop_001"


def check_03_false_friend(output):
    """rep_001 and rep_002 must NOT be allied (asymmetric trust)."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    pair = tuple(sorted(['rep_001', 'rep_002']))
    if pair not in alliances:
        return 1.0, "Correctly detected False Friend — no alliance"
    else:
        return 0.0, "FAIL: Allied False Friends rep_001-rep_002"


def check_04_clear_alliance(output):
    """rep_001 and rep_002 MUST be detected as allies."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    pair = tuple(sorted(['rep_001', 'rep_002']))
    if pair in alliances:
        return 1.0, "Correctly detected genuine alliance"
    else:
        return 0.0, "FAIL: Missed clear alliance rep_001-rep_002"


def check_05_faction_war(output):
    """prop_002 (less objected) should be preferred over prop_001 (heavily objected)."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'prop_002' in props and 'prop_001' not in props:
        return 1.0, "Correctly picked least-objected proposal"
    elif 'prop_002' in props:
        return 0.5, "Selected correct proposal but also included controversial one"
    else:
        return 0.0, "FAIL: Did not select least-objected proposal"


def check_06_priority_vs_objection(output):
    """prop_002 (low priority, no objection) should be selected. prop_001 heavily objected despite priority=10."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'prop_002' in props:
        if 'prop_001' not in props:
            return 1.0, "Objection weight correctly beat raw priority"
        else:
            return 0.5, "Selected safe bill but also included controversial one"
    else:
        return 0.0, "FAIL: Did not select the safe low-priority proposal"


def check_07_supporter_coherence(output):
    """rep_001 objects to prop_001. If prop_001 selected, rep_001 must NOT be supporter."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'prop_001' in props and 'rep_001' in reps:
        return 0.0, "FAIL: Objector rep_001 is a supporter of prop_001"
    elif 'prop_001' in props and 'rep_001' not in reps:
        return 1.0, "Correctly excluded objector from supporters"
    elif 'prop_001' not in props:
        return 0.5, "Avoided the issue by not selecting prop_001"
    return 0.5, "Partial"


def check_08_faction_infiltrator(output):
    """rep_002 (Spy Steve, betrays fellow Progressives at 0.90+) must be excluded."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'rep_002' not in reps:
        return 1.0, "Correctly detected and excluded faction infiltrator"
    else:
        return 0.0, "FAIL: Faction infiltrator rep_002 is in supporters"


def check_09_cascading_betrayal(output):
    """rep_003 (betrays rep_001 at 0.88) should be excluded or flagged."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'rep_003' not in reps:
        return 1.0, "Correctly excluded high-risk end of betrayal chain"
    else:
        return 0.5, "Partial: Included rep_003 despite cascading betrayal risk"


def check_10_alliance_hijack(output):
    """rep_001-rep_002 alliance must survive despite rep_003 (disruptor)."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    pair = tuple(sorted(['rep_001', 'rep_002']))
    disruptor_pair_1 = tuple(sorted(['rep_001', 'rep_003']))
    disruptor_pair_2 = tuple(sorted(['rep_002', 'rep_003']))
    if pair in alliances and disruptor_pair_1 not in alliances and disruptor_pair_2 not in alliances:
        return 1.0, "Alliance preserved, disruptor excluded"
    elif pair in alliances:
        return 0.5, "Alliance detected but disruptor also included"
    else:
        return 0.0, "FAIL: Alliance not detected"


def check_11_complete_rivalry(output):
    """All reps are rivals. Alliances must be empty."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if len(alliances) == 0:
        return 1.0, "Correctly returned empty alliances"
    else:
        return 0.0, f"FAIL: Found {len(alliances)} alliances in complete rivalry"


def check_12_ghost_sponsor(output):
    """prop_002 (ghost sponsor rep_099) must NOT be selected."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if 'prop_002' not in props and 'prop_001' in props:
        return 1.0, "Correctly excluded ghost-sponsored proposal"
    elif 'prop_002' not in props:
        return 0.5, "Excluded ghost but didn't select valid proposal"
    else:
        return 0.0, "FAIL: Selected ghost-sponsored prop_002"


def check_13_minimum_viable(output):
    """Must work with only 1 valid rep and 1 valid proposal."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    if len(props) >= 1 and len(reps) >= 1:
        return 1.0, "Correctly handled minimum viable scenario"
    elif len(props) >= 1 or len(reps) >= 1:
        return 0.5, "Partial output in minimum viable scenario"
    else:
        return 0.0, "FAIL: Empty output for minimum viable scenario"


def check_14_id_normalization(output):
    """Mixed case IDs must be normalized. Output IDs must be lowercase/trimmed."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    fa = output.get('final_agreement', {})
    raw_props = fa.get('proposals', [])
    raw_reps = fa.get('supporting_reps', [])

    all_normalized = True
    for pid in raw_props:
        if pid != pid.strip().lower():
            all_normalized = False
    for rid in raw_reps:
        if rid != rid.strip().lower():
            all_normalized = False

    if all_normalized and len(props) >= 1:
        return 1.0, "IDs correctly normalized across files"
    elif len(props) >= 1:
        return 0.5, "Output exists but IDs not fully normalized"
    else:
        return 0.0, "FAIL: Could not handle mixed-case IDs"


def check_15_duplicate_proposals(output):
    """Duplicate prop_001 must be deduplicated. Only 2 unique proposals should exist."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    fa = output.get('final_agreement', {})
    raw_props = fa.get('proposals', [])
    if len(raw_props) == len(set(norm(p) for p in raw_props)) and len(props) >= 1:
        return 1.0, "Correctly deduplicated proposals"
    else:
        return 0.0, "FAIL: Duplicate proposals in output"


def check_16_null_influence(output):
    """Must not crash on null/string influence values."""
    if not output:
        return 0.0, "No output (likely crashed)"
    props, reps, alliances = get_output_data(output)
    if len(props) >= 1:
        return 1.0, "Handled null/invalid influence without crashing"
    else:
        return 0.5, "Didn't crash but produced empty output"


def check_17_scale_correctness(output):
    """50+ reps, 30+ proposals. Must produce valid output and exclude trojan/poison."""
    props, reps, alliances = get_output_data(output)
    if not output:
        return 0.0, "No output"
    score = 0.0
    msg_parts = []

    # Must have at least some proposals and supporters
    if len(props) >= 1:
        score += 0.25
        msg_parts.append("has proposals")
    if len(reps) >= 1:
        score += 0.25
        msg_parts.append("has supporters")

    # Trojan rep_099 should not be in supporters
    if 'rep_099' not in reps:
        score += 0.25
        msg_parts.append("excluded trojan")
    else:
        msg_parts.append("INCLUDED trojan")

    # Poison prop_099 should not be selected
    if 'prop_099' not in props:
        score += 0.25
        msg_parts.append("excluded poison")
    else:
        msg_parts.append("INCLUDED poison")

    return score, "; ".join(msg_parts)


def check_18_dirty_csv(output):
    """Must handle bad CSV rows without breaking. Clean rows should still produce valid relations."""
    if not output:
        return 0.0, "No output (likely crashed on dirty CSV)"
    props, reps, alliances = get_output_data(output)
    if len(props) >= 1 and len(reps) >= 1:
        return 1.0, "Handled dirty CSV gracefully"
    elif len(props) >= 1 or len(reps) >= 1:
        return 0.5, "Partial output from dirty CSV"
    else:
        return 0.0, "FAIL: Empty output from dirty CSV"


# =====================================================================
# SCENARIO REGISTRY
# =====================================================================

SCENARIOS = [
    {"id": "01", "name": "Trojan Horse",         "dir": "01_trojan_horse",         "check": check_01_trojan_horse,        "points": 6},
    {"id": "02", "name": "Poison Pill",           "dir": "02_poison_pill",          "check": check_02_poison_pill,         "points": 6},
    {"id": "03", "name": "False Friend",          "dir": "03_false_friend",         "check": check_03_false_friend,        "points": 6},
    {"id": "04", "name": "Clear Alliance",        "dir": "04_clear_alliance",       "check": check_04_clear_alliance,      "points": 6},
    {"id": "05", "name": "Faction War",           "dir": "05_faction_war",          "check": check_05_faction_war,         "points": 5},
    {"id": "06", "name": "Priority vs Objection", "dir": "06_priority_vs_objection","check": check_06_priority_vs_objection,"points": 5},
    {"id": "07", "name": "Supporter Coherence",   "dir": "07_supporter_coherence",  "check": check_07_supporter_coherence, "points": 6},
    {"id": "08", "name": "Faction Infiltrator",   "dir": "08_faction_infiltrator",  "check": check_08_faction_infiltrator, "points": 6},
    {"id": "09", "name": "Cascading Betrayal",    "dir": "09_cascading_betrayal",   "check": check_09_cascading_betrayal,  "points": 5},
    {"id": "10", "name": "Alliance Hijack",       "dir": "10_alliance_hijack",      "check": check_10_alliance_hijack,     "points": 6},
    {"id": "11", "name": "Complete Rivalry",       "dir": "11_complete_rivalry",      "check": check_11_complete_rivalry,    "points": 5},
    {"id": "12", "name": "Ghost Sponsor",          "dir": "12_ghost_sponsor",        "check": check_12_ghost_sponsor,       "points": 6},
    {"id": "13", "name": "Minimum Viable",         "dir": "13_minimum_viable",       "check": check_13_minimum_viable,      "points": 5},
    {"id": "14", "name": "ID Normalization",       "dir": "14_id_normalization",     "check": check_14_id_normalization,    "points": 6},
    {"id": "15", "name": "Duplicate Proposals",    "dir": "15_duplicate_proposals",  "check": check_15_duplicate_proposals, "points": 5},
    {"id": "16", "name": "Null Influence",          "dir": "16_null_influence",       "check": check_16_null_influence,      "points": 5},
    {"id": "17", "name": "Scale Correctness",      "dir": "17_scale_correctness",    "check": check_17_scale_correctness,   "points": 6},
    {"id": "18", "name": "Dirty CSV",              "dir": "18_dirty_csv",            "check": check_18_dirty_csv,           "points": 5},
]

# Verify total = 100
assert sum(s['points'] for s in SCENARIOS) == 100, \
    f"Point total must be 100, got {sum(s['points'] for s in SCENARIOS)}"
