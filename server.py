from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matching_logic import load_database, save_database, process_ideas

app = FastAPI()

# Allow all CORS origins (can restrict later for security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    # Load current database
    database = load_database()

    # Process incoming ideas
    updated_database = process_ideas(data.ideas, database)

    # Save back to disk
    save_database(updated_database)

    return {"message": "Database updated successfully", "updated_count": len(data.ideas)}

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}