"""
validate_dataset.py

Validates the synthetic dataset produced by generate_synthetic_data.py.
Fails loudly (non-zero exit code) if the dataset is invalid.

Usage:
    python validate_dataset.py [--data-dir ../data]
"""

import argparse
import csv
import os
import sys

FAILS = []
WARNINGS = []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def load_csv(path):
    if not os.path.exists(path):
        fail(f"Missing required file: {path}")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_duplicate_ids(rows, id_field, name):
    ids = [r[id_field] for r in rows if id_field in r]
    if len(ids) != len(set(ids)):
        fail(f"{name}: duplicate {id_field} values found ({len(ids) - len(set(ids))} dupes)")


def check_missing_values(rows, name, allowed_empty_fields=()):
    missing = 0
    for r in rows:
        for k, v in r.items():
            if k in allowed_empty_fields:
                continue
            if v is None or v == "":
                missing += 1
    if missing:
        warn(f"{name}: {missing} empty non-exempt cells found (some may be legitimate, e.g. no OCR text)")


def check_score_range(rows, field, name, lo=0.0, hi=1.0):
    bad = 0
    for r in rows:
        try:
            val = float(r[field])
            if not (lo - 1e-6 <= val <= hi + 1e-6):
                bad += 1
        except (ValueError, KeyError):
            bad += 1
    if bad:
        fail(f"{name}: {bad} rows have {field} outside [{lo}, {hi}]")


def check_foreign_key(child_rows, child_field, parent_ids, name):
    bad = sum(1 for r in child_rows if r.get(child_field, "") not in parent_ids)
    if bad:
        fail(f"{name}: {bad} rows reference unknown {child_field}")


def main():
    parser = argparse.ArgumentParser()
    default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    parser.add_argument("--data-dir", default=default_dir)
    args = parser.parse_args()
    d = args.data_dir

    users = load_csv(os.path.join(d, "users.csv"))
    reels = load_csv(os.path.join(d, "reels.csv"))
    candidates = load_csv(os.path.join(d, "candidate_reels.csv"))
    interactions = load_csv(os.path.join(d, "interactions.csv"))
    sessions = load_csv(os.path.join(d, "sessions.csv"))
    creators = load_csv(os.path.join(d, "creators.csv"))
    technologies = load_csv(os.path.join(d, "technologies.csv"))
    relationships = load_csv(os.path.join(d, "technology_relationships.csv"))
    ground_truth = load_csv(os.path.join(d, "ground_truth.csv"))

    # --- duplicate IDs ---
    check_duplicate_ids(users, "user_id", "users.csv")
    check_duplicate_ids(reels, "reel_id", "reels.csv")
    check_duplicate_ids(candidates, "reel_id", "candidate_reels.csv")
    check_duplicate_ids(interactions, "interaction_id", "interactions.csv")
    check_duplicate_ids(sessions, "session_id", "sessions.csv")
    check_duplicate_ids(creators, "creator_id", "creators.csv")
    check_duplicate_ids(technologies, "entity_id", "technologies.csv")
    check_duplicate_ids(relationships, "rel_id", "technology_relationships.csv")

    # --- missing values (OCR/technologies/frameworks can legitimately be empty) ---
    check_missing_values(reels, "reels.csv", allowed_empty_fields={
        "ocr_text", "programming_languages", "technologies", "frameworks"})
    check_missing_values(users, "users.csv")
    check_missing_values(interactions, "interactions.csv")

    # --- score ranges ---
    check_score_range(reels, "quality_score", "reels.csv")
    check_score_range(reels, "hype_score", "reels.csv")
    check_score_range(reels, "learning_value", "reels.csv")
    check_score_range(reels, "career_value", "reels.csv")
    check_score_range(reels, "practical_value", "reels.csv")
    check_score_range(reels, "entertainment_value", "reels.csv")
    check_score_range(interactions, "watch_percentage", "interactions.csv", lo=0, hi=100)
    check_score_range(creators, "technical_quality", "creators.csv")
    check_score_range(creators, "credibility_score", "creators.csv")

    # --- foreign keys ---
    user_ids = {u["user_id"] for u in users}
    reel_ids = {r["reel_id"] for r in reels} | {r["reel_id"] for r in candidates}
    creator_ids = {c["creator_id"] for c in creators}
    check_foreign_key(interactions, "user_id", user_ids, "interactions.csv")
    check_foreign_key(interactions, "reel_id", reel_ids, "interactions.csv")
    check_foreign_key(sessions, "user_id", user_ids, "sessions.csv")
    check_foreign_key(reels, "creator_id", creator_ids, "reels.csv")
    check_foreign_key(ground_truth, "user_id", user_ids, "ground_truth.csv")

    # --- language consistency: content_language must be a known language or mixed variant ---
    known_langs = {"English", "Telugu", "Hindi", "Tamil", "Kannada", "Malayalam", "Bengali",
                   "Telugu-English", "Hindi-English", "Tamil-English", "Kannada-English"}
    bad_lang = sum(1 for r in reels if r["content_language"] not in known_langs)
    if bad_lang:
        fail(f"reels.csv: {bad_lang} rows have an unrecognized content_language value")

    # --- interaction validity: engagement flags must be 0/1 ---
    for r in interactions[:5000]:  # sample check for speed on very large datasets
        for flag in ("liked", "saved", "shared", "replayed", "skipped", "followed_creator"):
            if r.get(flag) not in ("0", "1"):
                fail(f"interactions.csv: non-binary value for {flag} in {r.get('interaction_id')}")
                break

    # --- category distribution sanity ---
    if reels:
        from collections import Counter
        cat_counts = Counter(r["category"] for r in reels)
        if len(cat_counts) < 4:
            warn(f"reels.csv: only {len(cat_counts)} distinct categories present — expected a realistic mixture")
        if "entertainment" not in cat_counts:
            fail("reels.csv: no entertainment content found — required for entertainment/tech separation testing")
        if "hype" not in cat_counts:
            fail("reels.csv: no hype content found — required to test the hype-penalty trap")

    # --- user diversity ---
    personas = {u.get("persona") for u in users}
    if len(personas) < 4:
        warn(f"users.csv: only {len(personas)} distinct personas present — expected diverse user behavior")

    # --- required trap users present ---
    for trap_id in ("TRAP_JAVA_BACKEND", "TRAP_MULTILINGUAL", "TRAP_ENTERTAINMENT_HEAVY"):
        if trap_id not in user_ids:
            fail(f"users.csv: required trap user '{trap_id}' is missing")

    # --- report ---
    print("=" * 60)
    print("DATASET VALIDATION REPORT")
    print("=" * 60)
    if WARNINGS:
        print(f"\n{len(WARNINGS)} WARNING(S):")
        for w in WARNINGS:
            print(f"  ⚠ {w}")
    if FAILS:
        print(f"\n{len(FAILS)} FAILURE(S):")
        for f in FAILS:
            print(f"  ✗ {f}")
        print("\nVALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n[OK] All checks passed. Dataset is structurally valid.")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
