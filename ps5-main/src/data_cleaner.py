"""
data_cleaner.py — Sanitizes, normalizes, deduplicates, and validates all data.
Covers Issues 6-9: ID normalization, invalid attributes, deduplication, ghost references.
"""


def normalize_id(raw_id):
    """
    Normalize a representative or proposal ID.
    Strips whitespace, converts to lowercase. (Issue 6)
    """
    if not isinstance(raw_id, str):
        return str(raw_id).strip().lower()
    return raw_id.strip().lower()


def safe_int(value, default=50, min_val=0, max_val=100):
    """
    Safely cast a value to int, clamping to [min_val, max_val].
    Handles strings, nulls, and out-of-range values. (Issue 7)
    """
    if value is None:
        return default
    try:
        num = int(float(value))
    except (ValueError, TypeError):
        return default
    return max(min_val, min(max_val, num))


def safe_float(value, default=0.0, min_val=0.0, max_val=1.0):
    """
    Safely cast a value to float, clamping to [min_val, max_val].
    """
    if value is None:
        return default
    try:
        num = float(value)
    except (ValueError, TypeError):
        return default
    return max(min_val, min(max_val, num))


def safe_severity(value, default=5, min_val=1, max_val=10):
    """
    Safely parse a severity value.
    Handles strings like 'high', 'medium', 'low', nulls, and out-of-range. (Issue 7)
    """
    if value is None:
        return default

    # Handle string labels
    if isinstance(value, str):
        label_map = {
            'high': 8, 'critical': 10, 'severe': 9,
            'medium': 5, 'moderate': 5,
            'low': 2, 'minor': 1, 'minimal': 1,
        }
        lower = value.strip().lower()
        if lower in label_map:
            return label_map[lower]
        try:
            num = int(float(lower))
        except (ValueError, TypeError):
            return default
        return max(min_val, min(max_val, num))

    try:
        num = int(float(value))
    except (ValueError, TypeError):
        return default
    return max(min_val, min(max_val, num))


def safe_priority(value, default=5, min_val=1, max_val=10):
    """Safely parse a priority value, clamp to [1, 10]."""
    if value is None:
        return default
    try:
        num = float(value)
    except (ValueError, TypeError):
        return default
    return max(min_val, min(max_val, num))


def clean_representatives(raw_reps):
    """
    Clean representative records:
    - Normalize IDs (Issue 6)
    - Fix influence types/values (Issue 7)
    - Deduplicate by normalized ID (keep first occurrence)
    """
    seen = {}
    for rep in raw_reps:
        if 'id' not in rep:
            continue
        norm_id = normalize_id(rep['id'])
        if norm_id in seen:
            continue  # Skip duplicate

        cleaned = {
            'id': norm_id,
            'name': rep.get('name', f'Unknown ({norm_id})'),
            'faction': rep.get('faction', 'Unknown'),
            'influence': safe_int(rep.get('influence'), default=50, min_val=0, max_val=100),
        }
        seen[norm_id] = cleaned

    return list(seen.values())


def clean_proposals(raw_proposals):
    """
    Clean proposal records:
    - Normalize IDs (Issue 6)
    - Normalize sponsor IDs
    - Fix priority values
    - Deduplicate by normalized ID, keep first occurrence (Issue 8)
    """
    seen = {}
    for prop in raw_proposals:
        if 'id' not in prop:
            continue
        norm_id = normalize_id(prop['id'])
        if norm_id in seen:
            continue  # Skip duplicate (Issue 8)

        cleaned = {
            'id': norm_id,
            'title': prop.get('title', f'Untitled ({norm_id})'),
            'sponsor': normalize_id(prop.get('sponsor', '')),
            'priority': safe_priority(prop.get('priority'), default=5),
        }
        seen[norm_id] = cleaned

    return list(seen.values())


def clean_objections(raw_objections):
    """
    Clean objection records:
    - Normalize rep_id and proposal_id (Issue 6)
    - Fix severity values (Issue 7)
    - Deduplicate (same rep + same proposal → keep highest severity)
    """
    obj_map = {}
    for obj in raw_objections:
        if 'rep_id' not in obj or 'proposal_id' not in obj:
            continue

        norm_rep = normalize_id(obj['rep_id'])
        norm_prop = normalize_id(obj['proposal_id'])
        severity = safe_severity(obj.get('severity'))

        key = (norm_rep, norm_prop)
        if key in obj_map:
            # Keep the higher severity objection
            if severity > obj_map[key]['severity']:
                obj_map[key]['severity'] = severity
        else:
            obj_map[key] = {
                'rep_id': norm_rep,
                'proposal_id': norm_prop,
                'severity': severity,
            }

    return list(obj_map.values())


def clean_relations(raw_relations):
    """
    Clean relation records:
    - Normalize from/to IDs (Issue 6)
    - Fix trust, rivalry, betrayal_prob types (Issue 7)
    - Deduplicate (same from→to → keep first)
    """
    seen = {}
    for rel in raw_relations:
        from_id = normalize_id(rel.get('from', ''))
        to_id = normalize_id(rel.get('to', ''))

        if not from_id or not to_id or from_id == to_id:
            continue

        key = (from_id, to_id)
        if key in seen:
            continue  # Skip duplicate row

        cleaned = {
            'from': from_id,
            'to': to_id,
            'trust': safe_int(rel.get('trust'), default=50, min_val=0, max_val=100),
            'rivalry': safe_int(rel.get('rivalry'), default=50, min_val=0, max_val=100),
            'betrayal_prob': safe_float(rel.get('betrayal_prob'), default=0.5, min_val=0.0, max_val=1.0),
        }
        seen[key] = cleaned

    return list(seen.values())


def validate_references(reps, proposals, objections, relations):
    """
    Remove orphaned/ghost references (Issue 9):
    - Objections referencing non-existent reps or proposals
    - Proposals with non-existent sponsors (ghost sponsors)
    - Relations referencing non-existent reps
    """
    rep_ids = {r['id'] for r in reps}
    prop_ids = {p['id'] for p in proposals}

    # Filter proposals with ghost sponsors
    valid_proposals = []
    for prop in proposals:
        if prop['sponsor'] in rep_ids:
            valid_proposals.append(prop)
        else:
            print(f"[CLEAN] Removing proposal '{prop['id']}' — ghost sponsor '{prop['sponsor']}'")

    valid_prop_ids = {p['id'] for p in valid_proposals}

    # Filter objections with ghost reps or proposals
    valid_objections = []
    for obj in objections:
        if obj['rep_id'] not in rep_ids:
            print(f"[CLEAN] Removing objection — ghost rep '{obj['rep_id']}'")
            continue
        if obj['proposal_id'] not in valid_prop_ids:
            print(f"[CLEAN] Removing objection — ghost proposal '{obj['proposal_id']}'")
            continue
        valid_objections.append(obj)

    # Filter relations with ghost reps
    valid_relations = []
    for rel in relations:
        if rel['from'] not in rep_ids or rel['to'] not in rep_ids:
            print(f"[CLEAN] Removing relation — ghost rep '{rel['from']}' or '{rel['to']}'")
            continue
        valid_relations.append(rel)

    return reps, valid_proposals, valid_objections, valid_relations


def clean_all(raw_data):
    """
    Run the full cleaning pipeline on all datasets.
    Returns cleaned, validated data.
    """
    reps = clean_representatives(raw_data['representatives'])
    proposals = clean_proposals(raw_data['proposals'])
    objections = clean_objections(raw_data['objections'])
    relations = clean_relations(raw_data['relations'])

    # Validate cross-references
    reps, proposals, objections, relations = validate_references(
        reps, proposals, objections, relations
    )

    return {
        'representatives': reps,
        'proposals': proposals,
        'objections': objections,
        'relations': relations,
    }
