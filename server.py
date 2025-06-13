from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from matching_logic import load_database, save_database, process_ideas

DB_PATH = "aisurvey-data.json"
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = FastAPI()

# CORS middleware
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://vinspolicy.github.io"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.on_event("startup")
async def ensure_db_exists():
    # Existence-only check, no parse
    load_database(parse=False)

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    # Full load for processing
    db = load_database(parse=True)
    results, log = process_ideas(data.ideas, db)
    save_database(db)
    logging.info("\n".join(log))
    return {"results": results, "log": log}

@app.get("/")
async def root():
    return {"message": "Backend running"}