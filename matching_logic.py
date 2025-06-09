import json
import os
import Levenshtein

DB_FILE = "aisurvey-data.json"

def load_database():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_matches(core_idea, database, threshold_high=90, threshold_mid=80):
    best_match = None
    best_score = 0
    mid_matches = []

    for existing_idea in database:
        score = Levenshtein.ratio(core_idea, existing_idea) * 100
        if score > best_score:
            best_score = score
            best_match = existing_idea
        if threshold_mid <= score < threshold_high:
            mid_matches.append((existing_idea, score))

    if best_score >= threshold_high:
        return {"type": "match", "match": best_match}
    elif mid_matches:
        mid_matches.sort(key=lambda x: x[1], reverse=True)
        return {"type": "mid", "suggestions": [m[0] for m in mid_matches]}
    else:
        return {"type": "new"}

def process_core_ideas(core_ideas):
    db = load_database()
    result = {}

    for idea in core_ideas:
        match_result = find_matches(idea, db)
        result[idea] = match_result

        if match_result["type"] == "match":
            db[match_result["match"]] += 1
        elif match_result["type"] == "new":
            db[idea] = 1
        # 'mid' suggestions left to surveyor – no automatic update

    save_database(db)
    return result