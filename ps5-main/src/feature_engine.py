"""
feature_engine.py — Derives actionable metrics from cleaned data.
Covers Issues 10-11: Relationship scores and objection weights.

P2 RESPONSIBILITY — Core feature engineering logic.
"""


def compute_relationship_scores(relations):
    """
    Issue 10: Compute relationship scores.
    
    relationship_score = trust × (1 - betrayal_prob)
    
    A high trust score is meaningless if betrayal probability is also high.
    This metric reflects the TRUE reliability of a connection.
    
    Example:
        trust=90, betrayal_prob=0.9 → score = 90 × 0.1 = 9 (DANGEROUS)
        trust=85, betrayal_prob=0.05 → score = 85 × 0.95 = 80.75 (RELIABLE)
    
    Returns: list of relations enriched with 'relationship_score'
    """
    enriched = []
    for rel in relations:
        trust = rel['trust']
        betrayal = rel['betrayal_prob']
        score = trust * (1 - betrayal)
        enriched_rel = dict(rel)
        enriched_rel['relationship_score'] = round(score, 2)
        enriched.append(enriched_rel)
    return enriched


def compute_objection_weights(proposals, objections, rep_lookup):
    """
    Issue 11: Calculate objection weights per proposal.
    
    objection_weight = Σ(severity × objector_influence)
    
    A powerful representative's objection matters far more than a weak one.
    
    Also computes:
        max_possible_weight = max_severity(10) × total_influence_of_all_reps
        controversy = objection_weight / max_possible_weight (normalized 0-1)
        proposal_viability = priority × (1 - controversy)
    
    Returns: list of proposals enriched with objection metrics
    """
    total_influence = sum(r['influence'] for r in rep_lookup.values())
    max_severity = 10
    # Avoid division by zero
    max_possible_weight = max_severity * total_influence if total_influence > 0 else 1

    # Group objections by proposal
    proposal_objections = {}
    for obj in objections:
        pid = obj['proposal_id']
        if pid not in proposal_objections:
            proposal_objections[pid] = []
        proposal_objections[pid].append(obj)

    enriched = []
    for prop in proposals:
        pid = prop['id']
        objs = proposal_objections.get(pid, [])

        # Calculate objection weight
        obj_weight = 0.0
        objector_ids = []
        severity_sum = 0.0
        for obj in objs:
            rep = rep_lookup.get(obj['rep_id'])
            if rep:
                obj_weight += obj['severity'] * rep['influence']
                objector_ids.append(obj['rep_id'])
                severity_sum += obj['severity']

        # Normalize to get controversy score (0-1)
        controversy = obj_weight / max_possible_weight if max_possible_weight > 0 else 0
        controversy = min(1.0, controversy)  # Clamp

        # Calculate viability
        viability = prop['priority'] * (1 - controversy)

        enriched_prop = dict(prop)
        enriched_prop['objection_weight'] = round(obj_weight, 2)
        enriched_prop['controversy'] = round(controversy, 4)
        enriched_prop['viability'] = round(viability, 4)
        enriched_prop['objector_ids'] = objector_ids
        enriched_prop['num_objectors'] = len(objector_ids)
        enriched_prop['avg_objector_severity'] = round(
            severity_sum / len(objector_ids), 4
        ) if objector_ids else 0.0
        enriched.append(enriched_prop)

    return enriched


def build_relationship_graph(enriched_relations):
    """
    Build a directional relationship graph.
    
    Returns: dict of {(from_id, to_id): relationship_score}
             and {from_id: {to_id: full_relation_data}}
    """
    score_map = {}
    graph = {}

    for rel in enriched_relations:
        from_id = rel['from']
        to_id = rel['to']
        score_map[(from_id, to_id)] = rel['relationship_score']

        if from_id not in graph:
            graph[from_id] = {}
        graph[from_id][to_id] = rel

    return score_map, graph


def compute_rep_avg_betrayal(relations, rep_ids):
    """
    Compute average betrayal probability for each representative.
    Looks at all outgoing relations from each rep.
    
    Returns: dict of {rep_id: avg_betrayal_prob}
    """
    betrayal_sums = {}
    betrayal_counts = {}

    for rel in relations:
        from_id = rel['from']
        if from_id in rep_ids:
            betrayal_sums[from_id] = betrayal_sums.get(from_id, 0.0) + rel['betrayal_prob']
            betrayal_counts[from_id] = betrayal_counts.get(from_id, 0) + 1

    avg_betrayal = {}
    for rid in rep_ids:
        if rid in betrayal_sums and betrayal_counts[rid] > 0:
            avg_betrayal[rid] = betrayal_sums[rid] / betrayal_counts[rid]
        else:
            # No outgoing relations — assume moderate risk
            avg_betrayal[rid] = 0.3
    return avg_betrayal


def engineer_features(cleaned_data):
    """
    Run the full feature engineering pipeline.
    Returns enriched data with computed metrics.
    """
    reps = cleaned_data['representatives']
    proposals = cleaned_data['proposals']
    objections = cleaned_data['objections']
    relations = cleaned_data['relations']

    # Build lookup
    rep_lookup = {r['id']: r for r in reps}
    rep_ids = set(rep_lookup.keys())

    # Issue 10: Relationship scores
    enriched_relations = compute_relationship_scores(relations)
    score_map, rel_graph = build_relationship_graph(enriched_relations)

    # Issue 11: Objection weights
    enriched_proposals = compute_objection_weights(proposals, objections, rep_lookup)

    # Compute average betrayal per rep
    avg_betrayal = compute_rep_avg_betrayal(relations, rep_ids)

    return {
        'representatives': reps,
        'rep_lookup': rep_lookup,
        'proposals': enriched_proposals,
        'objections': objections,
        'relations': enriched_relations,
        'score_map': score_map,
        'rel_graph': rel_graph,
        'avg_betrayal': avg_betrayal,
    }
