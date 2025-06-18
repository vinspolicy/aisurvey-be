# aisurvey-be/server.py

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from Levenshtein import ratio

app = FastAPI()

# CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # lock this down to your origin in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# matching thresholds
HIGH = 0.90
MID  = 0.80

class Payload(BaseModel):
    database: list[dict]        # e.g. [ { idea: "...", count: N }, ... ]
    incoming_ideas: list[str]   # new ideas from this survey

def find_match(idea: str, db: list[dict]):
    best_score = 0.0
    best_idx   = None
    # gather mid matches
    mids = []
    for i, entry in enumerate(db):
        s = ratio(idea, entry["idea"])
        if s > best_score:
            best_score, best_idx = s, i
        if MID <= s < HIGH:
            mids.append(i)
    if best_score >= HIGH:
        return ("match", best_idx)
    elif mids:
        return ("mid", mids)  # could pick highest, but return all for UI
    else:
        return ("new", None)

@app.post("/process-db/")
async def process_db(payload: Payload):
    db       = payload.database
    incoming = payload.incoming_ideas

    for idea in incoming:
        kind, idx_or_list = find_match(idea, db)
        if kind == "match":
            db[idx_or_list]["count"] += 1
        elif kind == "new":
            db.append({"idea": idea, "count": 1})
        # for "mid", we leave it to the client to review if you build that UI

    return JSONResponse({"database": db})