# aisurvey-be/server.py

import logging
import json
import os
import traceback

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from matching_logic import load_database, save_database, process_ideas

DB_PATH = "aisurvey-data.json"
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI()

# CORS – allow your GitHub Pages host (or use ["*"] during testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vinspolicy.github.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Explicitly accept OPTIONS on both variants
@app.options("/update-database")
@app.options("/update-database/")
async def options_update_database():
    return JSONResponse(status_code=200, content={})

@app.on_event("startup")
async def ensure_db_exists():
    # Existence-only check
    load_database(parse=False)

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database")
@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    try:
        results, log_msgs = process_ideas(data.ideas)
        logging.info("\n".join(log_msgs))
        return JSONResponse(status_code=200, content={"results": results, "log": log_msgs})
    except Exception as e:
        # Print full traceback to Render logs
        tb = traceback.format_exc()
        logging.error(tb)
        # Return JSONError so CORS headers get applied
        return JSONResponse(status_code=500, content={"error": str(e), "trace": tb})

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}