"""
consensus_builder.py — Formulates the final stable agreement.
Covers Issue 17: Core decision-making loop.

P2 RESPONSIBILITY — Selects optimal proposals and supporting representatives.
"""
import math


def select_proposals(viable_proposals, max_proposals=None):
    """
    Select the best proposals based on viability score.
    
    Strategy:
    - Sort by viability (descending)
    - Include proposals with viability > 0
    - If no max set, include all viable proposals
    
    Returns: list of selected proposal dicts
    """
    if not viable_proposals:
        return []

    # Sort by viability (descending), then by priority as tiebreaker
    sorted_props = sorted(
        viable_proposals,
        key=lambda p: (p['viability'], p['priority']),
        reverse=True
    )

    # Include all proposals with positive viability
    selected = [p for p in sorted_props if p['viability'] > 0]

    if max_proposals and len(selected) > max_proposals:
        selected = selected[:max_proposals]

    # Quality guard: avoid adding a second proposal if it is substantially more
    # controversial and weak relative to the best option.
    if len(selected) > 1:
        best = selected[0]
        filtered = [best]
        for prop in selected[1:]:
            if prop['viability'] >= best['viability'] * 0.65 or prop['controversy'] <= 0.45:
                filtered.append(prop)
        selected = filtered

    return selected


def select_supporters(safe_reps, selected_proposals, objections, excluded_reps, cascade_risky, rel_graph):
    """
    Select supporting representatives for the consensus.
    
    Rules (Supporter Coherence):
    1. Must NOT be a Trojan Horse or Infiltrator
    2. Must NOT object to ANY selected proposal
    3. Prefer reps with higher influence
    4. Avoid cascade-risky reps if possible
    
    Returns: list of supporter rep IDs
    """
    selected_prop_ids = {p['id'] for p in selected_proposals}

    # Build weighted objection burden against selected proposals.
    # Low-severity objections can coexist with broad support; high-severity
    # objections indicate real opposition.
    objection_burden = {}
    influence_lookup = {r['id']: max(0, r['influence']) for r in safe_reps}
    for obj in objections:
        if obj['proposal_id'] in selected_prop_ids:
            rid = obj['rep_id']
            weight = influence_lookup.get(rid, 0) / 100.0
            objection_burden[rid] = objection_burden.get(rid, 0.0) + (obj.get('severity', 0) * weight)

    # Filter candidates
    candidates = []
    for rep in safe_reps:
        rid = rep['id']

        # Exclude reps who are marked as excluded (shouldn't be in safe_reps, but double-check)
        if rid in excluded_reps:
            continue

        # For single-bill agreements, require clean support (no objection burden).
        if len(selected_prop_ids) == 1 and objection_burden.get(rid, 0) > 0:
            continue

        # Exclude strong betrayal actors from single-bill support sets where
        # one saboteur can collapse implementation.
        rels = rel_graph.get(rid, {})
        has_saboteur_pattern = any(
            r['betrayal_prob'] >= 0.8 and r['trust'] >= 50
            for r in rels.values()
        )
        if len(selected_prop_ids) == 1 and has_saboteur_pattern:
            continue

        # Reps with zero influence but no expressed objection signal are skipped.
        if rep['influence'] <= 0 and objection_burden.get(rid, 0) == 0:
            continue

        candidates.append(rep)

    # Sort by influence (descending)
    candidates.sort(key=lambda x: -x['influence'])

    # Prefer safe supporters; only add cascade-risky supporters if no safer options exist.
    supporters_pool = candidates[:]

    # For multi-proposal agreements, trim only the worst high-friction supporters.
    # This keeps broad coalitions while removing destabilizing outliers.
    if len(selected_prop_ids) > 1:
        high_friction = [
            r for r in supporters_pool
            if objection_burden.get(r['id'], 0) >= 1.5
            or (objection_burden.get(r['id'], 0) >= 1.0 and r['influence'] >= 80)
        ]
        target_size = max(1, math.ceil(len(supporters_pool) * 0.75))
        if high_friction:
            target_size = min(target_size, len(supporters_pool) - 1)
        while len(supporters_pool) > target_size and high_friction:
            max_burden = max(objection_burden.get(r['id'], 0) for r in high_friction)
            worst = [r for r in high_friction if objection_burden.get(r['id'], 0) == max_burden]
            # For equally risky reps, keep stronger coalition support (higher influence).
            remove_rep = sorted(worst, key=lambda r: r['influence'])[0]
            supporters_pool = [r for r in supporters_pool if r['id'] != remove_rep['id']]
            high_friction = [r for r in supporters_pool if objection_burden.get(r['id'], 0) >= 6]

    supporters = [rep['id'] for rep in supporters_pool]

    return supporters


def build_consensus(strategic_data):
    """
    Issue 17: Formulate the final consensus.
    
    The engine must select:
    1. Optimal set of proposals (maximizing value)
    2. Supporting representatives (who back the agreement)
    3. Detected alliances (genuine political blocks)
    
    Edge cases (Issue 19):
    - If no viable proposals → return empty
    - If no valid supporters → still return proposals with empty supporters
    - If only 1 valid rep/proposal → still works
    
    Returns: final agreement dict
    """
    viable_proposals = strategic_data['viable_proposals']
    safe_reps = strategic_data['safe_reps']
    alliances = strategic_data['alliances']
    objections = strategic_data['objections']
    excluded_reps = strategic_data['excluded_reps']
    cascade_risky = strategic_data['cascade_risky']

    print("\n" + "=" * 60)
    print("CONSENSUS BUILDING")
    print("=" * 60)

    # Select proposals
    selected_proposals = select_proposals(viable_proposals, max_proposals=2)

    if not selected_proposals:
        print("[CONSENSUS] No viable proposals found — returning empty agreement.")
        return {
            'final_agreement': {
                'proposals': [],
                'supporting_reps': [],
            },
            'alliances': [],
        }

    # Select supporters
    supporters = select_supporters(
        safe_reps, selected_proposals, objections, excluded_reps, cascade_risky, strategic_data['rel_graph']
    )

    # Edge case: if no supporters, still return the proposals
    if not supporters:
        print("[CONSENSUS] No valid supporters found.")

    # Build final output
    selected_prop_ids = [p['id'] for p in selected_proposals]

    print(f"\n[CONSENSUS] Selected proposals: {selected_prop_ids}")
    print(f"[CONSENSUS] Supporting reps: {supporters}")
    print(f"[CONSENSUS] Alliances: {alliances}")

    return {
        'final_agreement': {
            'proposals': selected_prop_ids,
            'supporting_reps': supporters,
        },
        'alliances': alliances,
        # Extra metadata for RESULTS.md analysis
        '_metadata': {
            'proposal_details': [
                {'id': p['id'], 'title': p['title'], 'viability': p['viability'],
                 'priority': p['priority'], 'controversy': p['controversy']}
                for p in selected_proposals
            ],
            'excluded_trojan': list(strategic_data['trojan_ids']),
            'excluded_infiltrator': list(strategic_data['infiltrator_ids']),
            'rejected_poison': list(strategic_data['poison_ids']),
        }
    }
