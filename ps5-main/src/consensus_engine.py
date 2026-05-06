"""
Phantom Consensus Engine — Main Entry Point
=============================================

A Strategic Consensus Engine that analyzes messy political data to determine:
1. Which proposals should be passed
2. Which politicians support the agreement
3. Which politicians are secretly allied

Pipeline:
    Load → Clean → Engineer Features → Strategic Analysis → Build Consensus → Output

Usage:
    python consensus_engine.py [data_dir]

If no data_dir is provided, defaults to ./data/raw/
Output is saved to ./data/output/consensus_output.json
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_all
from data_cleaner import clean_all
from feature_engine import engineer_features
from strategic_logic import apply_strategic_filters
from consensus_builder import build_consensus
from output_formatter import format_output, save_output, save_detailed_report


def run_engine(data_dir=None, output_dir=None):
    """
    Execute the full consensus engine pipeline.
    
    Issues covered:
    - Issue 1: Project structure (this file)
    - Issues 2-5: Data loading (data_loader.py)
    - Issues 6-9: Data cleaning (data_cleaner.py)
    - Issues 10-11: Feature engineering (feature_engine.py)
    - Issues 12-16: Strategic logic (strategic_logic.py)
    - Issue 17: Consensus building (consensus_builder.py)
    - Issue 18: Output formatting (output_formatter.py)
    - Issue 19: Edge case handling (throughout)
    - Issue 20: Performance (efficient algorithms)
    """
    start_time = time.time()

    # Resolve paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if data_dir is None:
        data_dir = os.path.join(base_dir, 'data', 'raw')
    if output_dir is None:
        output_dir = os.path.join(base_dir, 'data', 'output')

    print("=" * 60)
    print("  PHANTOM CONSENSUS ENGINE")
    print("=" * 60)
    print(f"  Data directory : {data_dir}")
    print(f"  Output directory: {output_dir}")
    print("=" * 60)

    # ─── STAGE 1: Load Raw Data (Issues 2-5) ───
    print("\n[STAGE 1] Loading raw data...")
    raw_data = load_all(data_dir)
    print(f"  Loaded: {len(raw_data['representatives'])} representatives, "
          f"{len(raw_data['proposals'])} proposals, "
          f"{len(raw_data['objections'])} objections, "
          f"{len(raw_data['relations'])} relations")

    # ─── Edge Case (Issue 19): Check for empty data ───
    if not raw_data['representatives']:
        print("[WARNING] No representatives found. Producing empty output.")
        empty_result = {
            'final_agreement': {'proposals': [], 'supporting_reps': []},
            'alliances': []
        }
        formatted = format_output(empty_result)
        save_output(formatted, output_dir)
        return formatted

    # ─── STAGE 2: Clean Data (Issues 6-9) ───
    print("\n[STAGE 2] Cleaning and sanitizing data...")
    cleaned_data = clean_all(raw_data)
    print(f"  After cleaning: {len(cleaned_data['representatives'])} representatives, "
          f"{len(cleaned_data['proposals'])} proposals, "
          f"{len(cleaned_data['objections'])} objections, "
          f"{len(cleaned_data['relations'])} relations")

    # ─── Edge Case (Issue 19): Check for no valid data after cleaning ───
    if not cleaned_data['representatives'] or not cleaned_data['proposals']:
        print("[WARNING] No valid representatives or proposals after cleaning.")
        empty_result = {
            'final_agreement': {'proposals': [], 'supporting_reps': []},
            'alliances': []
        }
        formatted = format_output(empty_result)
        save_output(formatted, output_dir)
        return formatted

    # ─── STAGE 3: Feature Engineering (Issues 10-11) ───
    print("\n[STAGE 3] Engineering features...")
    engineered_data = engineer_features(cleaned_data)
    print("  Computed: relationship scores, objection weights, viability scores")

    # Print proposal viability summary
    for p in engineered_data['proposals']:
        print(f"    {p['id']}: priority={p['priority']}, "
              f"controversy={p['controversy']:.3f}, "
              f"viability={p['viability']:.3f}, "
              f"objectors={p['num_objectors']}")

    # ─── STAGE 4: Strategic Analysis (Issues 12-16) ───
    print("\n[STAGE 4] Applying strategic filters...")
    strategic_data = apply_strategic_filters(engineered_data)

    # ─── STAGE 5: Build Consensus (Issue 17) ───
    print("\n[STAGE 5] Building consensus...")
    consensus_result = build_consensus(strategic_data)

    # ─── STAGE 6: Format and Save Output (Issue 18) ───
    print("\n[STAGE 6] Formatting output...")
    formatted = format_output(consensus_result)
    save_output(formatted, output_dir)

    # Save detailed report for analysis
    save_detailed_report(consensus_result, output_dir)

    # ─── Performance Summary (Issue 20) ───
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"  ENGINE COMPLETE — {elapsed:.3f} seconds")
    print(f"{'=' * 60}")

    return formatted


if __name__ == '__main__':
    # Accept optional data directory as argument
    data_dir = sys.argv[1] if len(sys.argv) > 1 else None
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    result = run_engine(data_dir, output_dir)
    print("\n[FINAL OUTPUT]")
    import json
    print(json.dumps(result, indent=2))
