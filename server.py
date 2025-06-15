import json
import os
import logging
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from Levenshtein import ratio

# === DB config ===
DB_PATH = "aisurvey_data.json"
MATCH_THRESHOLD_HIGH = 0.90
MATCH_THRESHOLD_LOW = 0.80

execution_log: list[str] = []

def log(msg: str):
    execution_log.append(msg)

def load_database() -> list[dict]:
    log("started: load_database")
    if not os.path.exists(DB_PATH):
        log(f"{DB_PATH} not found; creating new file")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                log("DB file was empty; initializing with []")
                return []
            data = json.loads(content)
            log("completed: load_database")
            return data
    except Exception as e:
        log(f"Error loading DB: {e}; resetting to []")
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

def save_database(data: list[dict]):
    log("started: save_database")
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log("completed: save_database")

def find_matches(core_idea: str, database: list[dict]) -> dict:
    log(f"started: find_matches for '{core_idea}'")
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

def process_ideas(core_ideas: list[str]) -> tuple[dict, list[str]]:
    execution_log.clear()
    log("started: process_ideas")
    log(f"received core_ideas: {core_ideas}")

    db = load_database()
    results: dict[str, dict] = {}

    for idea in core_ideas:
        log(f"processing idea: {idea}")
        outcome = find_matches(idea, db)
        results[idea] = outcome

        if outcome["type"] == "match":
            for entry in db:
                if entry["idea"] == outcome["match"]:
                    entry["count"] += 1
                    log(f"incremented count for '{entry['idea']}'")
                    break
        elif outcome["type"] == "new":
            db.append({"idea": idea, "count": 1})
            log(f"added new idea: '{idea}'")
        else:  # "mid"
            log(f"mid-suggestions for '{idea}': {outcome['suggestions']}")

    save_database(db)
    log("completed: process_ideas")
    return results, execution_log.copy()

# === FastAPI App ===

logging.basicConfig(level=logging.INFO, format="%(message)s")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vinspolicy.github.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/update-database")
@app.options("/update-database/")
async def options_update_database():
    return JSONResponse(status_code=200, content={})

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database")
@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    try:
        results, log_msgs = process_ideas(data.ideas)
        # log to both FastAPI logs and return to client
        logging.info("INPUT ideas: %s", data.ideas)
        for msg in log_msgs:
            logging.info(msg)
        return JSONResponse(status_code=200, content={"results": results, "log": log_msgs})
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(tb)
        return JSONResponse(status_code=500, content={"error": str(e), "trace": tb})

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}