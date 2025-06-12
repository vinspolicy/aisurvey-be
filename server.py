import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from matching_logic import process_ideas

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS middleware (allow your GitHub Pages origin or use ["*"] for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vinspolicy.github.io/aisurvey-fe"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    # Run your matching logic (loads, processes, saves, and logs)
    response = process_ideas(data.ideas)

    # Print the execution log to the server console
    logging.info("Execution log:\n%s", "\n".join(response["log"]))

    # Return both the match results and the log back to the client
    return {
        "message": "Database updated successfully",
        "results": response["results"],
        "log": response["log"]
    }

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}