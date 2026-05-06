"""
test_public.py — 13 Public Format Tests (Visible to Participants)

These tests validate output FORMAT only — not strategic correctness.
Even a naive solution should pass all 13.

Tests:
  1. Output file exists
  2. Output is valid JSON
  3. Has 'final_agreement' key
  4. Has 'alliances' key
  5. final_agreement has 'proposals' key
  6. final_agreement has 'supporting_reps' key
  7. proposals is a list
  8. supporting_reps is a list
  9. alliances is a list of lists
  10. At least 1 proposal selected
  11. At least 1 supporter selected
  12. No duplicate proposals
  13. All proposal/rep IDs exist in input data
"""

import json
import os


def load_output(output_path):
    """Load and return the consensus output JSON."""
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "Output file not found"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


def load_input_ids(data_dir):
    """Load all valid IDs from input data for cross-referencing."""
    rep_ids = set()
    prop_ids = set()

    reps_path = os.path.join(data_dir, 'representatives.json')
    if os.path.exists(reps_path):
        with open(reps_path, 'r', encoding='utf-8') as f:
            for r in json.load(f):
                rid = str(r.get('id', '')).strip().lower()
                if rid:
                    rep_ids.add(rid)

    props_path = os.path.join(data_dir, 'proposals.json')
    if os.path.exists(props_path):
        with open(props_path, 'r', encoding='utf-8') as f:
            for p in json.load(f):
                pid = str(p.get('id', '')).strip().lower()
                if pid:
                    prop_ids.add(pid)

    return rep_ids, prop_ids


def run_public_tests(output_path, data_dir):
    """
    Run all 13 public format tests.
    Returns: list of (test_name, passed: bool, message: str)
    """
    results = []

    # Test 1: Output file exists
    exists = os.path.exists(output_path)
    results.append(("T01: Output file exists", exists,
                     "PASS" if exists else f"File not found: {output_path}"))
    if not exists:
        for i in range(2, 14):
            results.append((f"T{i:02d}: Skipped", False, "No output file"))
        return results

    # Test 2: Valid JSON
    data, err = load_output(output_path)
    valid_json = data is not None
    results.append(("T02: Valid JSON", valid_json,
                     "PASS" if valid_json else err))
    if not valid_json:
        for i in range(3, 14):
            results.append((f"T{i:02d}: Skipped", False, "Invalid JSON"))
        return results

    # Test 3: Has 'final_agreement'
    has_fa = 'final_agreement' in data
    results.append(("T03: Has 'final_agreement' key", has_fa,
                     "PASS" if has_fa else "Missing 'final_agreement' key"))

    # Test 4: Has 'alliances'
    has_al = 'alliances' in data
    results.append(("T04: Has 'alliances' key", has_al,
                     "PASS" if has_al else "Missing 'alliances' key"))

    fa = data.get('final_agreement', {})

    # Test 5: Has 'proposals'
    has_props = 'proposals' in fa
    results.append(("T05: Has 'proposals' in final_agreement", has_props,
                     "PASS" if has_props else "Missing 'proposals'"))

    # Test 6: Has 'supporting_reps'
    has_reps = 'supporting_reps' in fa
    results.append(("T06: Has 'supporting_reps' in final_agreement", has_reps,
                     "PASS" if has_reps else "Missing 'supporting_reps'"))

    proposals = fa.get('proposals', [])
    supporters = fa.get('supporting_reps', [])
    alliances = data.get('alliances', [])

    # Test 7: proposals is a list
    is_list_p = isinstance(proposals, list)
    results.append(("T07: 'proposals' is a list", is_list_p,
                     "PASS" if is_list_p else f"Got {type(proposals).__name__}"))

    # Test 8: supporting_reps is a list
    is_list_r = isinstance(supporters, list)
    results.append(("T08: 'supporting_reps' is a list", is_list_r,
                     "PASS" if is_list_r else f"Got {type(supporters).__name__}"))

    # Test 9: alliances is a list of lists
    is_list_al = isinstance(alliances, list) and all(isinstance(a, list) for a in alliances)
    results.append(("T09: 'alliances' is list of lists", is_list_al,
                     "PASS" if is_list_al else "alliances must be list of [rep_a, rep_b] pairs"))

    # Test 10: At least 1 proposal
    has_one_prop = isinstance(proposals, list) and len(proposals) >= 1
    results.append(("T10: At least 1 proposal selected", has_one_prop,
                     "PASS" if has_one_prop else f"Got {len(proposals) if isinstance(proposals, list) else 0}"))

    # Test 11: At least 1 supporter
    has_one_sup = isinstance(supporters, list) and len(supporters) >= 1
    results.append(("T11: At least 1 supporter selected", has_one_sup,
                     "PASS" if has_one_sup else f"Got {len(supporters) if isinstance(supporters, list) else 0}"))

    # Test 12: No duplicate proposals
    no_dup = isinstance(proposals, list) and len(proposals) == len(set(proposals))
    results.append(("T12: No duplicate proposals", no_dup,
                     "PASS" if no_dup else "Duplicate proposal IDs found"))

    # Test 13: All IDs exist in input
    rep_ids, prop_ids = load_input_ids(data_dir)
    all_valid = True
    bad_ids = []
    if isinstance(proposals, list):
        for pid in proposals:
            if str(pid).strip().lower() not in prop_ids:
                all_valid = False
                bad_ids.append(f"proposal '{pid}'")
    if isinstance(supporters, list):
        for rid in supporters:
            if str(rid).strip().lower() not in rep_ids:
                all_valid = False
                bad_ids.append(f"rep '{rid}'")
    msg = "PASS" if all_valid else f"Unknown IDs: {', '.join(bad_ids)}"
    results.append(("T13: All IDs exist in input", all_valid, msg))

    return results
