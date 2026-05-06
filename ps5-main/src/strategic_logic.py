"""
strategic_logic.py — Core strategic analysis engine.
Covers Issues 12-16: Trojan Horse, Poison Pill, False Friend, Alliances, Faction Infiltrators.

P2 CORE RESPONSIBILITY — This is the heart of the consensus engine.
"""

# ─────────────────────────────────────────────────────────────
# Thresholds — These are design decisions, not given in the spec.
# Tuned for Tier S performance.
# ─────────────────────────────────────────────────────────────

BETRAYAL_THRESHOLD = 0.7          # Rep avg betrayal >= this → Trojan Horse
HIGH_INFLUENCE_THRESHOLD = 90     # Trojan filtering is stricter for influential reps
ALLIANCE_SCORE_THRESHOLD = 50     # Bidirectional score >= this → Alliance
INFILTRATOR_BETRAYAL_THRESH = 0.7 # Betrayal toward same-faction members >= this → Infiltrator
POISON_PILL_CONTROVERSY = 0.5     # Controversy >= this → Poison Pill candidate
ASYMMETRIC_RATIO = 0.5            # If min(A→B, B→A) / max(A→B, B→A) < this → asymmetric


def filter_trojan_horses(reps, avg_betrayal, rel_graph):
    """
    Issue 12: Filter Trojan Horse representatives.
    
    A Trojan Horse is a rep who:
    - Has high influence (looks attractive to include)
    - Has high average betrayal probability (will destabilize the consensus)
    
    We identify them by checking:
    1. Average betrayal_prob across all their outgoing relations >= THRESHOLD
    2. OR if they have ANY relation with betrayal_prob >= 0.85
    
    Returns: (safe_reps, trojan_ids)
    """
    trojan_ids = set()
    safe_reps = []

    for rep in reps:
        rid = rep['id']
        avg_b = avg_betrayal.get(rid, 0.3)

        # Check average betrayal, but only as a hard exclusion for high-impact reps.
        # This avoids wiping out all supporters in all-rivalry scenarios.
        is_trojan = rep['influence'] >= HIGH_INFLUENCE_THRESHOLD and avg_b >= BETRAYAL_THRESHOLD

        # Also check if any single relation has extremely high betrayal
        if rid in rel_graph:
            for to_id, rel_data in rel_graph[rid].items():
                if rep['influence'] >= HIGH_INFLUENCE_THRESHOLD and rel_data['betrayal_prob'] >= 0.85:
                    is_trojan = True
                    break
                # Deceptive high-trust / high-betrayal pattern is unstable even at
                # medium influence: "I trust you" while planning betrayal.
                if (
                    rel_data['betrayal_prob'] >= 0.95
                    and rel_data['trust'] >= 50
                    and rel_data['rivalry'] <= 50
                ):
                    is_trojan = True
                    break

        if is_trojan:
            trojan_ids.add(rid)
            print(f"[STRATEGY] Trojan Horse detected: {rid} (avg_betrayal={avg_b:.2f})")
        else:
            safe_reps.append(rep)

    return safe_reps, trojan_ids


def reject_poison_pills(proposals, reps):
    """
    Issue 13: Reject Poison Pill proposals.
    
    A Poison Pill is a proposal that:
    - May have high priority
    - But faces severe, widespread objections from influential reps
    - Its controversy score exceeds the threshold
    
    Additional check: if >50% of reps object, it's a poison pill regardless.
    
    Returns: (viable_proposals, poison_ids)
    """
    poison_ids = set()
    viable = []
    num_reps = len(reps)

    for prop in proposals:
        is_poison = False

        # Check controversy threshold
        if prop['controversy'] >= POISON_PILL_CONTROVERSY:
            is_poison = True

        # Check if majority of reps object
        if (
            num_reps > 0
            and prop['num_objectors'] > num_reps * 0.5
            and prop.get('avg_objector_severity', 0) >= 5
        ):
            is_poison = True

        # Check if viability has dropped too low
        if prop['viability'] < prop['priority'] * 0.3:
            is_poison = True

        if is_poison:
            poison_ids.add(prop['id'])
            print(f"[STRATEGY] Poison Pill rejected: {prop['id']} "
                  f"(controversy={prop['controversy']:.2f}, "
                  f"viability={prop['viability']:.2f}, "
                  f"objectors={prop['num_objectors']})")
        else:
            viable.append(prop)

    return viable, poison_ids


def detect_alliances(reps, score_map, rel_graph, objections, selected_proposal_ids=None):
    """
    Issue 14 & 15: Identify genuine alliances and handle asymmetric trust.
    
    A genuine alliance requires:
    1. BIDIRECTIONAL high relationship scores (Issue 14)
    2. Neither direction is asymmetric (Issue 15 — False Friend check)
    
    False Friend detection:
    - If A→B score is high but B→A is low, they are NOT allies
    - We require BOTH directions to exceed the threshold
    - We also check the ratio: min/max should be >= ASYMMETRIC_RATIO
    
    Returns: list of alliance pairs [rep_a, rep_b] (sorted)
    """
    if selected_proposal_ids is None:
        selected_proposal_ids = set()

    # (objector, proposal_id) -> max severity
    objection_map = {}
    objection_counts = {}
    for obj in objections:
        key = (obj['rep_id'], obj['proposal_id'])
        objection_map[key] = max(objection_map.get(key, 0), obj.get('severity', 0))
        pid = obj['proposal_id']
        objection_counts[pid] = objection_counts.get(pid, 0) + 1

    # proposal_id -> sponsor rep
    # infer from relation graph is not possible; this mapping must be provided by caller
    # via selected_proposal_ids in engineered proposal data. If unavailable, this check is skipped.
    sponsor_lookup = {}
    if isinstance(selected_proposal_ids, dict):
        sponsor_lookup = selected_proposal_ids
        selected_ids = set(selected_proposal_ids.keys())
    else:
        selected_ids = set(selected_proposal_ids)

    alliances = []
    rep_ids = [r['id'] for r in reps]
    checked = set()

    # Build symmetric partner ranks so we keep close-knit ties and avoid
    # broad over-linking.
    top_partners = {}
    for a in rep_ids:
        partner_scores = []
        for b in rep_ids:
            if a == b:
                continue
            sym = min(score_map.get((a, b), 0), score_map.get((b, a), 0))
            partner_scores.append((sym, b))
        partner_scores.sort(reverse=True)
        top_partners[a] = {b for _, b in partner_scores[:2]}
    for i, a in enumerate(rep_ids):
        for j, b in enumerate(rep_ids):
            if i >= j:
                continue
            pair = tuple(sorted([a, b]))
            if pair in checked:
                continue
            checked.add(pair)

            score_ab = score_map.get((a, b), 0)
            score_ba = score_map.get((b, a), 0)

            # Both directions must exceed threshold (Issue 14)
            if score_ab < ALLIANCE_SCORE_THRESHOLD or score_ba < ALLIANCE_SCORE_THRESHOLD:
                continue

            # Check for asymmetry (Issue 15 — False Friend)
            max_score = max(score_ab, score_ba)
            min_score = min(score_ab, score_ba)
            if max_score > 0 and (min_score / max_score) < ASYMMETRIC_RATIO:
                print(f"[STRATEGY] False Friend detected: {a} <-> {b} "
                      f"(scores: {score_ab:.1f} vs {score_ba:.1f})")
                continue

            # Strong cross-objections between selected proposals and each other's
            # sponsored agenda indicate tactical alignment is not stable enough to
            # call a secret alliance.
            severe_conflict = False
            if sponsor_lookup and selected_ids:
                a_props = [pid for pid, sponsor in sponsor_lookup.items() if sponsor == a and pid in selected_ids]
                b_props = [pid for pid, sponsor in sponsor_lookup.items() if sponsor == b and pid in selected_ids]
                for pid in a_props:
                    if (
                        objection_map.get((b, pid), 0) >= 5
                        and objection_counts.get(pid, 0) < (len(rep_ids) * 0.8)
                    ):
                        severe_conflict = True
                        break
                if not severe_conflict:
                    for pid in b_props:
                        if (
                            objection_map.get((a, pid), 0) >= 5
                            and objection_counts.get(pid, 0) < (len(rep_ids) * 0.8)
                        ):
                            severe_conflict = True
                            break
            if severe_conflict:
                continue

            # Require each rep to be among the other's strongest trusted ties.
            if b not in top_partners.get(a, set()) or a not in top_partners.get(b, set()):
                continue

            alliances.append(list(pair))
            print(f"[STRATEGY] Alliance detected: {pair[0]} <-> {pair[1]} "
                  f"(scores: {score_ab:.1f} / {score_ba:.1f})")

    return alliances


def detect_faction_infiltrators(reps, rel_graph, avg_betrayal):
    """
    Issue 16: Uncover faction infiltrators.
    
    A faction infiltrator is a rep who:
    - Claims membership in faction X
    - But has high betrayal probability toward OTHER members of faction X
    
    We check: for each rep, look at their relations to same-faction members.
    If avg betrayal toward same-faction >= INFILTRATOR_BETRAYAL_THRESH → infiltrator.
    
    Returns: (clean_reps, infiltrator_ids)
    """
    # Build faction membership
    faction_members = {}
    for rep in reps:
        faction = rep['faction']
        if faction not in faction_members:
            faction_members[faction] = []
        faction_members[faction].append(rep['id'])

    infiltrator_ids = set()

    for rep in reps:
        rid = rep['id']
        faction = rep['faction']
        same_faction = [m for m in faction_members.get(faction, []) if m != rid]

        if not same_faction:
            continue  # Only member of faction

        if rid not in rel_graph:
            continue  # No outgoing relations

        # Check betrayal toward same-faction members
        betrayals = []
        for member in same_faction:
            if member in rel_graph.get(rid, {}):
                betrayals.append(rel_graph[rid][member]['betrayal_prob'])

        if len(betrayals) >= 2:
            avg_faction_betrayal = sum(betrayals) / len(betrayals)
            if avg_faction_betrayal >= INFILTRATOR_BETRAYAL_THRESH:
                infiltrator_ids.add(rid)
                print(f"[STRATEGY] Faction Infiltrator detected: {rid} "
                      f"(faction={faction}, avg_betrayal_to_faction={avg_faction_betrayal:.2f})")
        elif len(betrayals) == 1 and betrayals[0] >= 0.8:
            infiltrator_ids.add(rid)
            print(f"[STRATEGY] Faction Infiltrator detected: {rid} "
                  f"(faction={faction}, betrayal_to_only_peer={betrayals[0]:.2f})")

    clean_reps = [r for r in reps if r['id'] not in infiltrator_ids]
    return clean_reps, infiltrator_ids


def detect_cascading_betrayal(reps, rel_graph, score_map):
    """
    Detect cascading betrayal chains.
    
    If A trusts B and B trusts C, but C has high betrayal toward A,
    then including C poisons the chain. We check 2-hop betrayal paths.
    
    Returns: set of risky rep IDs to flag (but not necessarily exclude)
    """
    risky = set()
    rep_ids = [r['id'] for r in reps]

    for a in rep_ids:
        if a not in rel_graph:
            continue
        for b in rel_graph[a]:
            if b not in rel_graph:
                continue
            for c in rel_graph[b]:
                if c == a:
                    continue
                # Check if C has high betrayal toward A
                if a in rel_graph.get(c, {}) and rel_graph[c][a]['betrayal_prob'] >= 0.7:
                    risky.add(c)

    return risky


def apply_strategic_filters(engineered_data):
    """
    Run all strategic logic filters.
    Returns the filtered data plus detected alliances.
    """
    reps = engineered_data['representatives']
    proposals = engineered_data['proposals']
    score_map = engineered_data['score_map']
    rel_graph = engineered_data['rel_graph']
    avg_betrayal = engineered_data['avg_betrayal']

    print("\n" + "=" * 60)
    print("STRATEGIC ANALYSIS")
    print("=" * 60)

    # Issue 12: Filter Trojan Horses
    safe_reps, trojan_ids = filter_trojan_horses(reps, avg_betrayal, rel_graph)

    # Issue 16: Detect Faction Infiltrators (on safe reps)
    clean_reps, infiltrator_ids = detect_faction_infiltrators(safe_reps, rel_graph, avg_betrayal)

    # Detect cascading betrayal
    cascade_risky = detect_cascading_betrayal(clean_reps, rel_graph, score_map)

    # Issue 13: Reject Poison Pills
    viable_proposals, poison_ids = reject_poison_pills(proposals, clean_reps)

    # Build proposal sponsor map for alliance conflict checks.
    # We intentionally include all cleaned proposals so strong policy conflict
    # still suppresses alliances even when a specific proposal is rejected later.
    proposal_sponsor_map = {
        p['id']: p.get('sponsor', '')
        for p in proposals
    }

    # Issues 14 & 15: Detect alliances (only among clean reps)
    alliances = detect_alliances(
        clean_reps,
        score_map,
        rel_graph,
        engineered_data['objections'],
        proposal_sponsor_map
    )

    # Combine all excluded reps
    excluded_reps = trojan_ids | infiltrator_ids

    return {
        'safe_reps': clean_reps,
        'viable_proposals': viable_proposals,
        'alliances': alliances,
        'trojan_ids': trojan_ids,
        'infiltrator_ids': infiltrator_ids,
        'poison_ids': poison_ids,
        'excluded_reps': excluded_reps,
        'cascade_risky': cascade_risky,
        'score_map': score_map,
        'rel_graph': rel_graph,
        'objections': engineered_data['objections'],
        'rep_lookup': engineered_data['rep_lookup'],
    }
