"""
data_loader.py — Loads raw data from the 4 input files.
Handles: representatives.json, proposals.json, objections.json, relations.csv
"""

import json
import csv
import os


def load_json(filepath):
    """Load and return data from a JSON file."""
    if not os.path.exists(filepath):
        print(f"[WARNING] File not found: {filepath}")
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"[WARNING] Expected list in {filepath}, got {type(data).__name__}")
            return []
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] Failed to parse {filepath}: {e}")
        return []


def load_csv(filepath):
    """
    Load and return data from a CSV file.
    Handles bad rows gracefully without breaking clean ones (Issue 20 — Dirty CSV).
    """
    if not os.path.exists(filepath):
        print(f"[WARNING] File not found: {filepath}")
        return []

    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            expected_fields = {'from', 'to', 'trust', 'rivalry', 'betrayal_prob'}

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                # Check that required fields exist
                if not expected_fields.issubset(row.keys()):
                    print(f"[WARNING] Row {row_num} missing required fields, skipping")
                    continue
                records.append(dict(row))
    except (IOError, csv.Error) as e:
        print(f"[ERROR] Failed to parse {filepath}: {e}")
        return []

    return records


def load_representatives(data_dir):
    """Load representatives from JSON."""
    return load_json(os.path.join(data_dir, 'representatives.json'))


def load_proposals(data_dir):
    """Load proposals from JSON."""
    return load_json(os.path.join(data_dir, 'proposals.json'))


def load_objections(data_dir):
    """Load objections from JSON."""
    return load_json(os.path.join(data_dir, 'objections.json'))


def load_relations(data_dir):
    """Load relations from CSV."""
    return load_csv(os.path.join(data_dir, 'relations.csv'))


def load_all(data_dir):
    """Load all datasets and return them as a dictionary."""
    return {
        'representatives': load_representatives(data_dir),
        'proposals': load_proposals(data_dir),
        'objections': load_objections(data_dir),
        'relations': load_relations(data_dir),
    }
