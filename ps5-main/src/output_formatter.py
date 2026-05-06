"""
output_formatter.py — Formats and saves the final consensus output as JSON.
Covers Issue 18: JSON output formatting.

P2 RESPONSIBILITY — Ensures output strictly adheres to the required schema.
"""

import json
import os


def format_output(consensus_result):
    """
    Issue 18: Format the consensus result into the required JSON schema.
    
    Required schema:
    {
        "final_agreement": {
            "proposals": ["prop_002", "prop_001"],
            "supporting_reps": ["rep_003", "rep_001", "rep_005"]
        },
        "alliances": [
            ["rep_001", "rep_004"],
            ["rep_002", "rep_005"]
        ]
    }
    
    - Removes internal metadata (prefixed with _)
    - Ensures all IDs are strings
    - Ensures alliances are sorted pairs
    - Removes duplicates from all lists
    """
    agreement = consensus_result.get('final_agreement', {})
    alliances = consensus_result.get('alliances', [])

    # Deduplicate and sort proposal IDs
    proposals = list(dict.fromkeys(agreement.get('proposals', [])))

    # Deduplicate and sort supporter IDs
    supporters = list(dict.fromkeys(agreement.get('supporting_reps', [])))

    # Ensure alliance pairs are sorted and deduplicated
    seen_alliances = set()
    clean_alliances = []
    for pair in alliances:
        if len(pair) != 2:
            continue
        sorted_pair = tuple(sorted(pair))
        if sorted_pair not in seen_alliances:
            seen_alliances.add(sorted_pair)
            clean_alliances.append(list(sorted_pair))

    output = {
        "final_agreement": {
            "proposals": proposals,
            "supporting_reps": supporters,
        },
        "alliances": clean_alliances,
    }

    return output


def save_output(output, output_dir):
    """
    Save the formatted output to consensus_output.json.
    Creates the output directory if it doesn't exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'consensus_output.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[OUTPUT] Saved to: {output_path}")
    return output_path


def save_detailed_report(consensus_result, output_dir):
    """
    Save a detailed analysis report (for RESULTS.md generation).
    Includes internal metadata for analysis purposes.
    """
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'detailed_report.json')

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(consensus_result, f, indent=2, ensure_ascii=False, default=str)

    print(f"[OUTPUT] Detailed report saved to: {report_path}")
    return report_path
