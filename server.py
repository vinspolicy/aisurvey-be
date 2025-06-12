from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matching_logic import load_database, save_database, process_ideas

app = FastAPI()

# ✅ Set your allowed origins here
origins = [
    "https://vinspolicy.github.io",  # GitHub Pages
]

# ✅ CORS middleware must come before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    updated_database = process_ideas(data.ideas)
    return {"message": "Database updated successfully", "updated_count": len(data.ideas)}

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}