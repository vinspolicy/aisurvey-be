import json
import logging
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from Levenshtein import ratio

# ——— Config & Logging ———
DB_PATH = "aisurvey_data.json"   # (in-container file; ephemeral on restart)
HIGH_THRESHOLD = 0.90
MID_THRESHOLD  = 0.80

logging.basicConfig(level=logging.INFO, format="%(message)s")
app = FastAPI()

# Allow all origins during demo; lock this down to your GH Pages URL in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_match_record(idea: str, db: list[dict]):
    best_score = 0.0
    best_match = None
    mid_matches = []

    for entry in db:
        score = ratio(idea, entry["idea"])
        if score > best_score:
            best_score, best_match = score, entry["idea"]
        if MID_THRESHOLD <= score < HIGH_THRESHOLD:
            mid_matches.append(entry["idea"])

    if best_score >= HIGH_THRESHOLD:
        return {"type": "match", "match": best_match}
    elif mid_matches:
        return {"type": "mid", "suggestions": mid_matches}
    else:
        return {"type": "new"}

@app.post("/process-db/")
async def process_database(file: UploadFile = File(...)):
    # 1) Read payload
    raw = await file.read()
    payload = json.loads(raw)
    incoming = payload.get("incoming_ideas", [])
    db       = payload.get("database", [])

    logging.info("Received incoming_ideas: %s", incoming)
    logging.info("Received database (pre-update): %s", db)

    # 2) Apply fuzzy logic
    for idea in incoming:
        outcome = find_match_record(idea, db)
        if outcome["type"] == "match":
            # increment existing
            for e in db:
                if e["idea"] == outcome["match"]:
                    e["count"] += 1
                    break
        elif outcome["type"] == "new":
            # add brand new
            db.append({"idea": idea, "count": 1})
        # mid --> no change (surveyor can review if you add that UI)

    logging.info("Updated database: %s", db)

    # 3) Return updated DB as JSON blob
    return Response(
        content=json.dumps({"database": db}, ensure_ascii=False, indent=2),
        media_type="application/json",
    )

@app.get("/")
async def root():
    return {"message": "Survey database backend is up!"}