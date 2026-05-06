"""
generate_scenarios.py — Generates all 18 hidden test scenario datasets.

Each scenario creates its own directory with 4 input files:
  representatives.json, proposals.json, objections.json, relations.csv

Run once to populate tests/hidden/scenarios/
"""

import json
import csv
import os


BASE_DIR = os.path.join(os.path.dirname(__file__), 'hidden', 'scenarios')


def write_scenario(name, reps, proposals, objections, relations):
    """Write a scenario's 4 data files."""
    d = os.path.join(BASE_DIR, name)
    os.makedirs(d, exist_ok=True)

    with open(os.path.join(d, 'representatives.json'), 'w') as f:
        json.dump(reps, f, indent=2)
    with open(os.path.join(d, 'proposals.json'), 'w') as f:
        json.dump(proposals, f, indent=2)
    with open(os.path.join(d, 'objections.json'), 'w') as f:
        json.dump(objections, f, indent=2)
    with open(os.path.join(d, 'relations.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['from', 'to', 'trust', 'rivalry', 'betrayal_prob'])
        for r in relations:
            w.writerow(r)


def gen_01_trojan_horse():
    """Scenario: rep_002 has influence=98 but betrayal=0.95. Must NOT be a supporter."""
    reps = [
        {"id": "rep_001", "name": "Safe Alice", "faction": "A", "influence": 70},
        {"id": "rep_002", "name": "Trojan Bob", "faction": "B", "influence": 98},
        {"id": "rep_003", "name": "Safe Carol", "faction": "A", "influence": 60},
    ]
    proposals = [
        {"id": "prop_001", "title": "Good Bill", "sponsor": "rep_001", "priority": 8},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 50, 30, 0.10],
        ["rep_002", "rep_001", 40, 40, 0.95],
        ["rep_001", "rep_003", 80, 10, 0.05],
        ["rep_003", "rep_001", 85, 8, 0.03],
        ["rep_002", "rep_003", 30, 60, 0.90],
        ["rep_003", "rep_002", 20, 70, 0.10],
    ]
    write_scenario('01_trojan_horse', reps, proposals, objections, relations)


def gen_02_poison_pill():
    """Scenario: prop_001 has priority=10 but every rep objects with severity=9+."""
    reps = [
        {"id": "rep_001", "name": "Alpha", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Beta", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Gamma", "faction": "B", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "Poison Bill", "sponsor": "rep_001", "priority": 10},
        {"id": "prop_002", "title": "Safe Bill", "sponsor": "rep_002", "priority": 6},
    ]
    objections = [
        {"rep_id": "rep_001", "proposal_id": "prop_001", "severity": 9},
        {"rep_id": "rep_002", "proposal_id": "prop_001", "severity": 10},
        {"rep_id": "rep_003", "proposal_id": "prop_001", "severity": 9},
    ]
    relations = [
        ["rep_001", "rep_002", 70, 20, 0.10],
        ["rep_002", "rep_001", 65, 25, 0.12],
        ["rep_001", "rep_003", 50, 30, 0.20],
        ["rep_003", "rep_001", 55, 28, 0.18],
    ]
    write_scenario('02_poison_pill', reps, proposals, objections, relations)


def gen_03_false_friend():
    """Scenario: rep_001 trusts rep_002 (95) but rep_002 does NOT trust rep_001 (25, betrayal=0.85)."""
    reps = [
        {"id": "rep_001", "name": "Trusting Tom", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Deceptive Dan", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Neutral Nancy", "faction": "B", "influence": 60},
    ]
    proposals = [
        {"id": "prop_001", "title": "Test Bill", "sponsor": "rep_001", "priority": 7},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 95, 5, 0.05],
        ["rep_002", "rep_001", 25, 60, 0.85],
        ["rep_001", "rep_003", 50, 30, 0.15],
        ["rep_003", "rep_001", 55, 25, 0.12],
    ]
    write_scenario('03_false_friend', reps, proposals, objections, relations)


def gen_04_clear_alliance():
    """Scenario: rep_001 and rep_002 have high bidirectional trust and low betrayal."""
    reps = [
        {"id": "rep_001", "name": "Ally Alpha", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Ally Beta", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Loner Carl", "faction": "B", "influence": 60},
    ]
    proposals = [
        {"id": "prop_001", "title": "Unity Bill", "sponsor": "rep_001", "priority": 8},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 90, 5, 0.03],
        ["rep_002", "rep_001", 88, 8, 0.05],
        ["rep_001", "rep_003", 40, 40, 0.30],
        ["rep_003", "rep_001", 35, 45, 0.35],
    ]
    write_scenario('04_clear_alliance', reps, proposals, objections, relations)


def gen_05_faction_war():
    """Two proposals: prop_001 heavily objected, prop_002 lightly objected. Pick least-objected."""
    reps = [
        {"id": "rep_001", "name": "Hawk", "faction": "Hawks", "influence": 85},
        {"id": "rep_002", "name": "Dove", "faction": "Doves", "influence": 80},
        {"id": "rep_003", "name": "Owl", "faction": "Doves", "influence": 70},
        {"id": "rep_004", "name": "Eagle", "faction": "Hawks", "influence": 75},
    ]
    proposals = [
        {"id": "prop_001", "title": "War Bill", "sponsor": "rep_001", "priority": 8},
        {"id": "prop_002", "title": "Peace Bill", "sponsor": "rep_002", "priority": 7},
    ]
    objections = [
        {"rep_id": "rep_002", "proposal_id": "prop_001", "severity": 9},
        {"rep_id": "rep_003", "proposal_id": "prop_001", "severity": 8},
        {"rep_id": "rep_004", "proposal_id": "prop_002", "severity": 3},
    ]
    relations = [
        ["rep_001", "rep_004", 80, 10, 0.05],
        ["rep_004", "rep_001", 75, 15, 0.08],
        ["rep_002", "rep_003", 85, 5, 0.04],
        ["rep_003", "rep_002", 82, 8, 0.06],
    ]
    write_scenario('05_faction_war', reps, proposals, objections, relations)


def gen_06_priority_vs_objection():
    """prop_001: priority=10, heavy objection. prop_002: priority=5, zero objection. Objection weight must beat raw priority."""
    reps = [
        {"id": "rep_001", "name": "Power", "faction": "A", "influence": 90},
        {"id": "rep_002", "name": "Quiet", "faction": "A", "influence": 60},
    ]
    proposals = [
        {"id": "prop_001", "title": "High Priority Controversial", "sponsor": "rep_002", "priority": 10},
        {"id": "prop_002", "title": "Low Priority Safe", "sponsor": "rep_002", "priority": 5},
    ]
    objections = [
        {"rep_id": "rep_001", "proposal_id": "prop_001", "severity": 10},
    ]
    relations = [
        ["rep_001", "rep_002", 70, 20, 0.10],
        ["rep_002", "rep_001", 65, 25, 0.12],
    ]
    write_scenario('06_priority_vs_objection', reps, proposals, objections, relations)


def gen_07_supporter_coherence():
    """rep_001 objects to prop_001. rep_001 must NOT be a supporter if prop_001 is selected."""
    reps = [
        {"id": "rep_001", "name": "Objector", "faction": "A", "influence": 90},
        {"id": "rep_002", "name": "Supporter", "faction": "A", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "Contested Bill", "sponsor": "rep_002", "priority": 8},
    ]
    objections = [
        {"rep_id": "rep_001", "proposal_id": "prop_001", "severity": 7},
    ]
    relations = [
        ["rep_001", "rep_002", 60, 30, 0.15],
        ["rep_002", "rep_001", 65, 25, 0.10],
    ]
    write_scenario('07_supporter_coherence', reps, proposals, objections, relations)


def gen_08_faction_infiltrator():
    """rep_002 claims faction 'Progressives' but betrays other Progressives with prob 0.90."""
    reps = [
        {"id": "rep_001", "name": "True Progressive", "faction": "Progressives", "influence": 80},
        {"id": "rep_002", "name": "Spy Steve", "faction": "Progressives", "influence": 85},
        {"id": "rep_003", "name": "True Progressive 2", "faction": "Progressives", "influence": 70},
        {"id": "rep_004", "name": "Outsider", "faction": "Others", "influence": 60},
    ]
    proposals = [
        {"id": "prop_001", "title": "Progressive Bill", "sponsor": "rep_001", "priority": 8},
    ]
    objections = []
    relations = [
        ["rep_002", "rep_001", 40, 50, 0.90],
        ["rep_002", "rep_003", 35, 55, 0.92],
        ["rep_001", "rep_003", 85, 5, 0.04],
        ["rep_003", "rep_001", 80, 10, 0.06],
        ["rep_001", "rep_002", 70, 20, 0.08],
        ["rep_004", "rep_001", 50, 30, 0.20],
        ["rep_001", "rep_004", 55, 25, 0.15],
    ]
    write_scenario('08_faction_infiltrator', reps, proposals, objections, relations)


def gen_09_cascading_betrayal():
    """A trusts B, B trusts C, but C has high betrayal toward A. C should be excluded."""
    reps = [
        {"id": "rep_001", "name": "Start", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Middle", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Betrayer", "faction": "A", "influence": 90},
    ]
    proposals = [
        {"id": "prop_001", "title": "Chain Bill", "sponsor": "rep_001", "priority": 7},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 85, 10, 0.05],
        ["rep_002", "rep_001", 80, 12, 0.08],
        ["rep_002", "rep_003", 80, 10, 0.10],
        ["rep_003", "rep_002", 75, 15, 0.12],
        ["rep_003", "rep_001", 30, 60, 0.88],
        ["rep_001", "rep_003", 70, 20, 0.15],
    ]
    write_scenario('09_cascading_betrayal', reps, proposals, objections, relations)


def gen_10_alliance_hijack():
    """rep_001+rep_002 are strong allies. rep_003 tries to disrupt. Alliance must survive."""
    reps = [
        {"id": "rep_001", "name": "Ally1", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Ally2", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Disruptor", "faction": "B", "influence": 95},
    ]
    proposals = [
        {"id": "prop_001", "title": "Alliance Bill", "sponsor": "rep_001", "priority": 8},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 92, 3, 0.02],
        ["rep_002", "rep_001", 90, 5, 0.04],
        ["rep_003", "rep_001", 20, 70, 0.85],
        ["rep_003", "rep_002", 25, 65, 0.80],
        ["rep_001", "rep_003", 30, 60, 0.10],
        ["rep_002", "rep_003", 28, 62, 0.12],
    ]
    write_scenario('10_alliance_hijack', reps, proposals, objections, relations)


def gen_11_complete_rivalry():
    """Every rep is a rival of every other. Alliances should be empty."""
    reps = [
        {"id": "rep_001", "name": "Rival1", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Rival2", "faction": "B", "influence": 75},
        {"id": "rep_003", "name": "Rival3", "faction": "C", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "Rivalry Bill", "sponsor": "rep_001", "priority": 7},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 10, 90, 0.85],
        ["rep_002", "rep_001", 15, 85, 0.80],
        ["rep_001", "rep_003", 12, 88, 0.82],
        ["rep_003", "rep_001", 8, 92, 0.90],
        ["rep_002", "rep_003", 5, 95, 0.88],
        ["rep_003", "rep_002", 10, 90, 0.85],
    ]
    write_scenario('11_complete_rivalry', reps, proposals, objections, relations)


def gen_12_ghost_sponsor():
    """prop_002 sponsored by rep_099 who doesn't exist. Must be excluded."""
    reps = [
        {"id": "rep_001", "name": "Real Rep", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Another Rep", "faction": "A", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "Real Bill", "sponsor": "rep_001", "priority": 7},
        {"id": "prop_002", "title": "Ghost Bill", "sponsor": "rep_099", "priority": 9},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 70, 20, 0.10],
        ["rep_002", "rep_001", 65, 25, 0.12],
    ]
    write_scenario('12_ghost_sponsor', reps, proposals, objections, relations)


def gen_13_minimum_viable():
    """After cleaning, only 1 valid rep and 1 valid proposal remain."""
    reps = [
        {"id": "rep_001", "name": "Solo Rep", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Ghost Rep Ref", "faction": "B", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "Solo Bill", "sponsor": "rep_001", "priority": 7},
        {"id": "prop_002", "title": "Ghost Sponsor Bill", "sponsor": "rep_099", "priority": 9},
    ]
    objections = []
    relations = []
    write_scenario('13_minimum_viable', reps, proposals, objections, relations)


def gen_14_id_normalization():
    """IDs have mixed case and whitespace across files."""
    reps = [
        {"id": "rep_001", "name": "Normal", "faction": "A", "influence": 80},
        {"id": "REP_002", "name": "Upper", "faction": "A", "influence": 75},
        {"id": " rep_003", "name": "Spaced", "faction": "B", "influence": 70},
    ]
    proposals = [
        {"id": "PROP_001", "title": "Mixed Case Bill", "sponsor": "REP_001", "priority": 8},
        {"id": "prop_002", "title": "Normal Bill", "sponsor": "rep_002", "priority": 7},
    ]
    objections = [
        {"rep_id": " REP_003 ", "proposal_id": "PROP_001", "severity": 5},
    ]
    relations = [
        ["REP_001", " rep_002", 80, 10, 0.05],
        ["rep_002", "rep_001", 75, 15, 0.08],
        ["rep_003", "REP_001", 60, 25, 0.15],
    ]
    write_scenario('14_id_normalization', reps, proposals, objections, relations)


def gen_15_duplicate_proposals():
    """Same proposal ID appears twice with different data."""
    reps = [
        {"id": "rep_001", "name": "Alpha", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Beta", "faction": "A", "influence": 75},
    ]
    proposals = [
        {"id": "prop_001", "title": "Original Bill", "sponsor": "rep_001", "priority": 8},
        {"id": "prop_001", "title": "Duplicate Bill", "sponsor": "rep_002", "priority": 5},
        {"id": "prop_002", "title": "Unique Bill", "sponsor": "rep_002", "priority": 7},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 70, 20, 0.10],
        ["rep_002", "rep_001", 65, 25, 0.12],
    ]
    write_scenario('15_duplicate_proposals', reps, proposals, objections, relations)


def gen_16_null_influence():
    """Some reps have null or string influence values. Must not crash."""
    reps = [
        {"id": "rep_001", "name": "Normal", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Null Influence", "faction": "A", "influence": None},
        {"id": "rep_003", "name": "String Influence", "faction": "B", "influence": "sixty"},
        {"id": "rep_004", "name": "High Influence", "faction": "B", "influence": 200},
    ]
    proposals = [
        {"id": "prop_001", "title": "Test Bill", "sponsor": "rep_001", "priority": 7},
    ]
    objections = []
    relations = [
        ["rep_001", "rep_002", 70, 20, 0.10],
        ["rep_002", "rep_001", 65, 25, 0.12],
    ]
    write_scenario('16_null_influence', reps, proposals, objections, relations)


def gen_17_scale_correctness():
    """50 reps, 30 proposals. Must produce correct output at scale."""
    import random
    random.seed(42)

    reps = []
    for i in range(1, 51):
        reps.append({
            "id": f"rep_{i:03d}",
            "name": f"Rep {i}",
            "faction": random.choice(["Alpha", "Beta", "Gamma", "Delta"]),
            "influence": random.randint(30, 95),
        })
    # Add one trojan horse
    reps.append({
        "id": "rep_099",
        "name": "Hidden Trojan",
        "faction": "Alpha",
        "influence": 98,
    })

    proposals = []
    for i in range(1, 31):
        proposals.append({
            "id": f"prop_{i:03d}",
            "title": f"Proposal {i}",
            "sponsor": f"rep_{random.randint(1, 50):03d}",
            "priority": random.randint(3, 10),
        })
    # Add a poison pill
    proposals.append({
        "id": "prop_099",
        "title": "Poison Proposal",
        "sponsor": "rep_001",
        "priority": 10,
    })

    objections = []
    # Add heavy objections to poison pill
    for i in range(1, 40):
        objections.append({
            "rep_id": f"rep_{random.randint(1, 50):03d}",
            "proposal_id": "prop_099",
            "severity": random.randint(8, 10),
        })
    # Add normal objections
    for _ in range(30):
        objections.append({
            "rep_id": f"rep_{random.randint(1, 50):03d}",
            "proposal_id": f"prop_{random.randint(1, 30):03d}",
            "severity": random.randint(1, 8),
        })

    relations = []
    # Trojan horse relations
    for i in range(1, 10):
        relations.append([
            "rep_099", f"rep_{i:03d}", random.randint(20, 50), random.randint(40, 80), round(random.uniform(0.85, 0.98), 2)
        ])
    # Normal relations
    for _ in range(100):
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        if a != b:
            relations.append([
                f"rep_{a:03d}", f"rep_{b:03d}",
                random.randint(20, 90), random.randint(10, 80),
                round(random.uniform(0.02, 0.50), 2)
            ])

    write_scenario('17_scale_correctness', reps, proposals, objections, relations)


def gen_18_dirty_csv():
    """CSV with bad rows (missing fields, extra commas). Must handle without breaking clean rows."""
    reps = [
        {"id": "rep_001", "name": "Alpha", "faction": "A", "influence": 80},
        {"id": "rep_002", "name": "Beta", "faction": "A", "influence": 75},
        {"id": "rep_003", "name": "Gamma", "faction": "B", "influence": 70},
    ]
    proposals = [
        {"id": "prop_001", "title": "CSV Bill", "sponsor": "rep_001", "priority": 7},
    ]
    objections = []

    # Write CSV manually to include bad rows
    d = os.path.join(BASE_DIR, '18_dirty_csv')
    os.makedirs(d, exist_ok=True)

    with open(os.path.join(d, 'representatives.json'), 'w') as f:
        json.dump(reps, f, indent=2)
    with open(os.path.join(d, 'proposals.json'), 'w') as f:
        json.dump(proposals, f, indent=2)
    with open(os.path.join(d, 'objections.json'), 'w') as f:
        json.dump(objections, f, indent=2)

    with open(os.path.join(d, 'relations.csv'), 'w', newline='') as f:
        f.write("from,to,trust,rivalry,betrayal_prob\n")
        f.write("rep_001,rep_002,80,10,0.05\n")       # Good row
        f.write("rep_002,rep_001,75,15,0.08\n")        # Good row
        f.write("rep_001,rep_003,,high,abc\n")          # Bad: missing trust, string rivalry, string betrayal
        f.write("rep_003,rep_001,60,25,0.15\n")        # Good row
        f.write("bad_row_only_two_fields,rep_002\n")   # Bad: missing fields
        f.write("rep_002,rep_003,70,20,0.12\n")        # Good row


def generate_all():
    """Generate all 18 hidden test scenarios."""
    print("Generating 18 hidden test scenarios...")
    gen_01_trojan_horse()
    gen_02_poison_pill()
    gen_03_false_friend()
    gen_04_clear_alliance()
    gen_05_faction_war()
    gen_06_priority_vs_objection()
    gen_07_supporter_coherence()
    gen_08_faction_infiltrator()
    gen_09_cascading_betrayal()
    gen_10_alliance_hijack()
    gen_11_complete_rivalry()
    gen_12_ghost_sponsor()
    gen_13_minimum_viable()
    gen_14_id_normalization()
    gen_15_duplicate_proposals()
    gen_16_null_influence()
    gen_17_scale_correctness()
    gen_18_dirty_csv()
    print(f"Done! Scenarios saved to: {BASE_DIR}")


if __name__ == '__main__':
    generate_all()
