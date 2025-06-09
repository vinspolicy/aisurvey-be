import json
import os
from fuzzywuzzy import fuzz, process

DB_PATH = os.path.join(os.path.dirname(__file__), "aisurvey-data.json")

def load_database():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_database(core_ideas):
    db = load_database()
    db_ideas = [entry["idea"] for entry in db]

    updates = []

    for idea in core_ideas:
        matches = process.extract(idea, db_ideas, scorer=fuzz.ratio)
        top_match = max(matches, key=lambda x: x[1], default=(None, 0))

        if top_match[1] >= 90:
            for entry in db:
                if entry["idea"] == top_match[0]:
                    entry["count"] += 1
                    updates.append({"idea": entry["idea"], "match": "existing", "score": top_match[1]})
                    break
        elif 80 <= top_match[1] < 90:
            updates.append({"idea": idea, "match": "needs_manual_review", "suggestions": [
                {"idea": match[0], "score": match[1]} for match in matches if match[1] >= 80
            ]})
        else:
            db.append({"idea": idea, "count": 1})
            updates.append({"idea": idea, "match": "new"})

    save_database(db)
    return updates