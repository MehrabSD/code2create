import json, os, sys, csv

BASE = "/home/claude/phantom_tests"

SCENARIOS = {
    1:  ("Trojan Horse Detection",       10),
    2:  ("Poison Pill Rejection",        10),
    3:  ("Asymmetric Trust",             8),
    4:  ("Ghost Sponsor",                5),
    5:  ("ID Normalisation",             5),
    6:  ("Dirty CSV Handling",           5),
    7:  ("Faction Infiltrator",          8),
    8:  ("Supporter Coherence",          8),
    9:  ("Clear Alliance",               6),
    10: ("Minimum Viable",               3),
    11: ("Complete Rivalry",             5),
    12: ("Duplicate Proposals",          4),
    13: ("Null Influence",               4),
    14: ("Scale Correctness",            5),
    15: ("Priority vs Objection Weight", 8),
    16: ("Cascading Betrayal",           6),
    17: ("Alliance Hijack",              6),
    18: ("Faction War",                  4),
    19: ("Decoy Alliance", 8),
    20: ("Shadow Sponsor", 7),
    21: ("Self-Objecting Sponsor", 7),
    22: ("All-Null Influence", 5),
    23: ("The Kingmaker", 8),
    24: ("Proposal Laundering", 5),
    25: ("Thin Margin", 8),
    26: ("Zombie Alliance", 7),
    27: ("Influence Cliff", 6),
    28: ("Trust Vacuum", 6),
    29: ("Faction of One", 6),
    30: ("The Grand Illusion", 12),
}
# Total = 110 but normalised to 100

def load_meta(n):
    path = f"{BASE}/scenario_{n:02d}/meta.json"
    if not os.path.exists(path): return None
    with open(path) as f: return json.load(f)

def score_output(n, output):
    meta = load_meta(n)
    if not meta: return 0, "No meta found"
    exp = meta.get("expected_output", {})
    scoring = meta.get("scoring", {})

    if "note" in exp:
        # Scale scenario — validate structural correctness only
        fa = output.get("final_agreement", {})
        proposals = fa.get("proposals", [])
        supporters = fa.get("supporting_reps", [])
        alliances = output.get("alliances", [])
        issues = []
        if len(proposals) == 0: issues.append("no proposals")
        if len(supporters) == 0: issues.append("no supporters")
        if len(set(proposals)) != len(proposals): issues.append("duplicate proposals")
        if len(set(supporters)) != len(supporters): issues.append("duplicate supporters")
        for pair in alliances:
            if len(pair) == 2 and pair[0] == pair[1]: issues.append("self-alliance")
        return (1.0 if not issues else 0.5), ("OK" if not issues else "; ".join(issues))

    exp_proposals = set(exp.get("final_agreement", {}).get("proposals", []))
    exp_supporters = set(exp.get("final_agreement", {}).get("supporting_reps", []))
    exp_alliances = [set(a) for a in exp.get("alliances", [])]

    out_proposals = set(output.get("final_agreement", {}).get("proposals", []))
    out_supporters = set(output.get("final_agreement", {}).get("supporting_reps", []))
    out_alliances = [set(a) for a in output.get("alliances", [])]

    prop_correct = exp_proposals == out_proposals
    sup_correct = exp_supporters == out_supporters
    alliance_correct = sorted([sorted(a) for a in exp_alliances]) == sorted([sorted(a) for a in out_alliances])

    if prop_correct and sup_correct and alliance_correct:
        return 1.0, "Full credit — all correct"
    elif prop_correct and (sup_correct or alliance_correct):
        return 0.6, f"Partial — proposals correct, {'supporters' if sup_correct else 'alliances'} correct"
    elif prop_correct:
        return 0.4, "Partial — proposals correct only"
    elif sup_correct:
        return 0.3, "Partial — supporters correct only"
    else:
        return 0.0, f"Zero — proposals expected {sorted(exp_proposals)} got {sorted(out_proposals)}"

def run_all(outputs_dir):
    """outputs_dir: folder containing scenario_XX_output.json files"""
    total_weight = sum(w for _, w in SCENARIOS.values())
    total_score = 0
    results = []

    for n, (name, weight) in SCENARIOS.items():
        fname = os.path.join(outputs_dir, f"scenario_{n:02d}_output.json")
        if not os.path.exists(fname):
            results.append({"scenario": n, "name": name, "weight": weight,
                            "ratio": 0.0, "earned": 0.0, "verdict": "MISSING — no output file"})
            continue
        try:
            with open(fname) as f:
                output = json.load(f)
            ratio, verdict = score_output(n, output)
        except Exception as e:
            ratio, verdict = 0.0, f"ERROR — {e}"
        earned = round(ratio * weight, 2)
        total_score += earned
        results.append({"scenario": n, "name": name, "weight": weight,
                        "ratio": ratio, "earned": earned, "verdict": verdict})

    final = round((total_score / total_weight) * 100, 1)
    return results, final, total_score, total_weight

if __name__ == "__main__":
    outputs_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    results, final, earned, total = run_all(outputs_dir)
    print(f"\n{'─'*70}")
    print(f"{'PHANTOM CONSENSUS ENGINE — SCORING REPORT':^70}")
    print(f"{'─'*70}")
    print(f"{'#':<4} {'Scenario':<35} {'Wt':>3} {'Ratio':>6} {'Pts':>6}  Verdict")
    print(f"{'─'*70}")
    for r in results:
        bar = "✅" if r['ratio'] == 1.0 else ("🟡" if r['ratio'] > 0 else "❌")
        print(f"{r['scenario']:<4} {r['name']:<35} {r['weight']:>3} {r['ratio']:>5.0%} {r['earned']:>6.2f}  {bar} {r['verdict']}")
    print(f"{'─'*70}")
    print(f"{'TOTAL SCORE':>44} {earned:>6.2f} / {total}")
    print(f"{'FINAL SCORE (out of 100)':>44} {final:>6.1f}")
    tier = "S" if final>=90 else "A" if final>=75 else "B" if final>=60 else "C" if final>=45 else "D" if final>=30 else "F"
    print(f"{'TIER':>44} {'':>6} {tier}")
    print(f"{'─'*70}\n")

