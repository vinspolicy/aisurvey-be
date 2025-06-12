import json
import os
from Levenshtein import ratio

DB_PATH = "aisurvey-data.json"
MATCH_THRESHOLD_HIGH = 0.90
MATCH_THRESHOLD_LOW = 0.80

def load_database():
    # If the file doesn't exist, create it with an empty list
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    # Otherwise load and return its contents
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_matches(core_idea, database, threshold_high=MATCH_THRESHOLD_HIGH, threshold_mid=MATCH_THRESHOLD_LOW):
    best_match = None
    best_score = 0.0
    mid_matches = []

    # database is a list of dicts: [{"idea": ..., "count": ...}, ...]
    for entry in database:
        existing = entry["idea"]
        score = ratio(core_idea, existing) * 100
        if score > best_score:
            best_score = score
            best_match = existing
        if threshold_mid * 100 <= score < threshold_high * 100:
            mid_matches.append((existing, score))

    if best_score >= threshold_high * 100:
        return {"type": "match", "match": best_match}
    elif mid_matches:
        mid_matches.sort(key=lambda x: x[1], reverse=True)
        return {"type": "mid", "suggestions": [m[0] for m in mid_matches]}
    else:
        return {"type": "new"}

def process_ideas(core_ideas):
    db = load_database()
    results = {}

    for idea in core_ideas:
        outcome = find_matches(idea, db)
        results[idea] = outcome

        if outcome["type"] == "match":
            # increment count
            for entry in db:
                if entry["idea"] == outcome["match"]:
                    entry["count"] += 1
                    break
        elif outcome["type"] == "new":
            # add new entry
            db.append({"idea": idea, "count": 1})
        # mid-suggestions are left for surveyor review

    save_database(db)
    return results