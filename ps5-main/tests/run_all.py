"""
run_all.py — Main Test Runner & Scorer for Phantom Consensus
=============================================================

Usage (as organizer):
    python tests/run_all.py <path_to_participant_src>

This script:
  1. Generates hidden test scenario data (if not already generated)
  2. Runs the participant's consensus_engine.py on EACH scenario
  3. Runs 13 public format tests on each output
  4. Runs 18 hidden strategic correctness tests
  5. Computes a total score out of 100
  6. Assigns a tier (S/A/B/C/D/F)
  7. Outputs a detailed scorecard

Example:
    python tests/run_all.py ../submissions/team_alpha/src
"""

import sys
import os
import json
import subprocess
import tempfile
import shutil
import time

# Add project root to path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)
sys.path.insert(0, TESTS_DIR)

from test_public import run_public_tests
from test_hidden import SCENARIOS, load_output
from generate_scenarios import generate_all, BASE_DIR


def get_tier(score):
    """Assign tier based on score."""
    if score >= 90: return 'S', 'Exceptional - handles everything'
    if score >= 75: return 'A', 'Strong - handles most cases'
    if score >= 60: return 'B', 'Competent - basic strategy works'
    if score >= 45: return 'C', 'Acceptable - passes format, naive logic'
    if score >= 30: return 'D', 'Weak - barely functional'
    return 'F', 'Failing'


def run_participant_engine(engine_path, data_dir, output_dir, timeout=30):
    """
    Run a participant's consensus_engine.py against a data directory.
    Returns: (success: bool, error_message: str, elapsed: float)
    """
    if not os.path.exists(engine_path):
        return False, f"Engine not found: {engine_path}", 0

    os.makedirs(output_dir, exist_ok=True)
    start = time.time()

    try:
        result = subprocess.run(
            [sys.executable, engine_path, data_dir, output_dir],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(engine_path),
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            return False, f"Exit code {result.returncode}: {result.stderr[:300]}", elapsed

        return True, "", elapsed

    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s", timeout
    except Exception as e:
        return False, str(e), time.time() - start


def find_engine(src_dir):
    """Find the consensus_engine.py file in the src directory."""
    # Direct path
    direct = os.path.join(src_dir, 'consensus_engine.py')
    if os.path.exists(direct):
        return direct

    # Search recursively
    for root, dirs, files in os.walk(src_dir):
        if 'consensus_engine.py' in files:
            return os.path.join(root, 'consensus_engine.py')

    return None


def run_full_evaluation(src_dir, verbose=True):
    """
    Run the complete evaluation pipeline.
    Returns: (total_score, tier, tier_desc, detailed_results)
    """
    # Find engine
    engine_path = find_engine(src_dir)
    if not engine_path:
        print(f"[ERROR] consensus_engine.py not found in {src_dir}")
        return 0, 'F', 'Failing', {}

    if verbose:
        print("=" * 70)
        print("  PHANTOM CONSENSUS — EVALUATION ENGINE")
        print("=" * 70)
        print(f"  Participant source: {src_dir}")
        print(f"  Engine file: {engine_path}")
        print("=" * 70)

    # Generate scenario data if needed
    if not os.path.exists(BASE_DIR) or len(os.listdir(BASE_DIR)) < 18:
        if verbose:
            print("\n[SETUP] Generating test scenario data...")
        generate_all()

    # ─── PUBLIC TESTS (on default data) ───
    if verbose:
        print("\n" + "=" * 70)
        print("  PHASE 1: PUBLIC FORMAT TESTS (13 tests)")
        print("=" * 70)

    default_data = os.path.join(PROJECT_ROOT, 'data', 'raw')
    default_output = tempfile.mkdtemp(prefix='phantom_public_')
    pub_success, pub_err, pub_time = run_participant_engine(
        engine_path, default_data, default_output
    )

    output_file = os.path.join(default_output, 'consensus_output.json')
    pub_results = run_public_tests(output_file, default_data)

    pub_passed = sum(1 for _, passed, _ in pub_results if passed)
    pub_total = len(pub_results)

    if verbose:
        for name, passed, msg in pub_results:
            status = "PASS" if passed else "FAIL"
            icon = "[+]" if passed else "[-]"
            print(f"  {icon} {name}: {msg}")
        print(f"\n  Public tests: {pub_passed}/{pub_total} passed ({pub_time:.2f}s)")

    shutil.rmtree(default_output, ignore_errors=True)

    # ─── HIDDEN TESTS (18 scenarios) ───
    if verbose:
        print("\n" + "=" * 70)
        print("  PHASE 2: HIDDEN SCENARIO TESTS (18 tests, 100 points)")
        print("=" * 70)

    total_score = 0.0
    scenario_results = []

    for scenario in SCENARIOS:
        sid = scenario['id']
        name = scenario['name']
        data_dir = os.path.join(BASE_DIR, scenario['dir'])
        max_pts = scenario['points']

        # Create temp output dir
        tmp_out = tempfile.mkdtemp(prefix=f'phantom_{sid}_')

        # Run engine on scenario data
        success, err, elapsed = run_participant_engine(engine_path, data_dir, tmp_out)

        if success:
            output = load_output(os.path.join(tmp_out, 'consensus_output.json'))
            fraction, msg = scenario['check'](output)
        else:
            fraction = 0.0
            msg = f"Engine failed: {err[:100]}"

        earned = round(max_pts * fraction, 1)
        total_score += earned

        scenario_results.append({
            'id': sid,
            'name': name,
            'max': max_pts,
            'earned': earned,
            'fraction': fraction,
            'message': msg,
            'time': elapsed,
        })

        if verbose:
            if fraction >= 1.0:
                icon = "[+]"
            elif fraction > 0:
                icon = "[~]"
            else:
                icon = "[-]"
            print(f"  {icon} S{sid} {name:.<30s} {earned:>5.1f}/{max_pts} pts  ({msg})")

        shutil.rmtree(tmp_out, ignore_errors=True)

    # ─── FINAL SCORE ───
    total_score = round(total_score, 1)
    tier, tier_desc = get_tier(total_score)

    if verbose:
        print("\n" + "=" * 70)
        print(f"  FINAL SCORE: {total_score}/100")
        print(f"  TIER: {tier} — {tier_desc}")
        print(f"  Public Tests: {pub_passed}/{pub_total}")
        print("=" * 70)

        # Score breakdown
        print("\n  Score Distribution:")
        print(f"  {'Scenario':<30s} {'Earned':>7s} {'Max':>5s} {'%':>6s}")
        print(f"  {'-'*30} {'-'*7} {'-'*5} {'-'*6}")
        for r in scenario_results:
            pct = f"{r['fraction']*100:.0f}%"
            print(f"  {r['name']:<30s} {r['earned']:>7.1f} {r['max']:>5d} {pct:>6s}")
        print(f"  {'TOTAL':<30s} {total_score:>7.1f} {'100':>5s}")

    return total_score, tier, tier_desc, {
        'public': {'passed': pub_passed, 'total': pub_total},
        'hidden': scenario_results,
        'total_score': total_score,
        'tier': tier,
    }


def main():
    if len(sys.argv) < 2:
        # Default: test our own solution
        src_dir = os.path.join(PROJECT_ROOT, 'src')
        print(f"[INFO] No source dir specified. Testing own solution: {src_dir}")
    else:
        src_dir = os.path.abspath(sys.argv[1])

    score, tier, desc, details = run_full_evaluation(src_dir)

    # Save results to JSON
    results_path = os.path.join(TESTS_DIR, 'last_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2)
    print(f"\n[INFO] Detailed results saved to: {results_path}")

    return score


if __name__ == '__main__':
    main()
