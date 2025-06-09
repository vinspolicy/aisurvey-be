import json
import os
from Levenshtein import ratio

DB_PATH = "aisurvey_data.json"
MATCH_THRESHOLD_HIGH = 0.90
MATCH_THRESHOLD_LOW = 0.80

def load_database():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_best_matches(idea, database):
    matches = []
    for entry in database:
        score = ratio(idea, entry["idea"])
        matches.append((entry["idea"], score))
    return sorted(matches, key=lambda x: x[1], reverse=True)

def process_ideas(incoming_ideas):
    database = load_database()
    results = []

    for idea in incoming_ideas:
        matches = find_best_matches(idea, database)
        if matches and matches[0][1] >= MATCH_THRESHOLD_HIGH:
            best_match = matches[0][0]
            for entry in database:
                if entry["idea"] == best_match:
                    entry["count"] += 1
                    results.append({"idea": idea, "matched_to": best_match, "status": "matched"})
                    break
        elif matches and matches[0][1] >= MATCH_THRESHOLD_LOW:
            close_matches = [m for m in matches if MATCH_THRESHOLD_LOW <= m[1] < MATCH_THRESHOLD_HIGH]
            results.append({
                "idea": idea,
                "status": "review",
                "suggestions": [match[0] for match in close_matches]
            })
        else:
            database.append({"idea": idea, "count": 1})
            results.append({"idea": idea, "status": "new"})

    save_database(database)
    return results