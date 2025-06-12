import json
import os
from Levenshtein import ratio

DB_PATH = "aisurvey-data.json"
MATCH_THRESHOLD_HIGH = 0.90
MATCH_THRESHOLD_LOW  = 0.80

# A global list to collect execution steps
execution_log: list[str] = []

def log(message: str):
    execution_log.append(message)

def load_database() -> list[dict]:
    log("started: load_database")
    if not os.path.exists(DB_PATH):
        log(f"{DB_PATH} not found; creating new file")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    log("completed: load_database")
    return data

def save_database(data: list[dict]):
    log("started: save_database")
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log("completed: save_database")

def find_matches(core_idea: str, database: list[dict]) -> dict:
    log("started: find_matches")
    best_match = None
    best_score = 0.0
    mid_matches: list[tuple[str, float]] = []

    for entry in database:
        existing = entry["idea"]
        score = ratio(core_idea, existing) * 100
        if score > best_score:
            best_score = score
            best_match = existing
        if MATCH_THRESHOLD_LOW*100 <= score < MATCH_THRESHOLD_HIGH*100:
            mid_matches.append((existing, score))

    log(f"find_matches: best_score={best_score:.2f}, best_match={best_match}")
    if best_score >= MATCH_THRESHOLD_HIGH*100:
        result = {"type": "match", "match": best_match}
    elif mid_matches:
        mid_matches.sort(key=lambda x: x[1], reverse=True)
        suggestions = [m[0] for m in mid_matches]
        result = {"type": "mid", "suggestions": suggestions}
    else:
        result = {"type": "new"}

    log("completed: find_matches")
    return result

def process_ideas(core_ideas: list[str]) -> dict:
    # Reset the log at the start
    execution_log.clear()
    log("started: process_ideas")

    db = load_database()
    results: dict[str, dict] = {}

    for idea in core_ideas:
        log(f"processing idea: {idea}")
        outcome = find_matches(idea, db)
        results[idea] = outcome

        if outcome["type"] == "match":
            # increment count
            for entry in db:
                if entry["idea"] == outcome["match"]:
                    entry["count"] += 1
                    log(f"incremented count for '{entry['idea']}'")
                    break
        elif outcome["type"] == "new":
            db.append({"idea": idea, "count": 1})
            log(f"added new idea: '{idea}'")
        else:  # outcome["type"] == "mid"
            log(f"mid-suggestions for '{idea}': {outcome['suggestions']}")

    save_database(db)
    log("completed: process_ideas")

    # Return both the match results and a copy of the log
    return {
        "results": results,
        "log": execution_log.copy()
    }