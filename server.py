from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from matching_logic import load_database, save_database, process_ideas

app = FastAPI()

# Enable full CORS (for frontend testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vinspolicy.github.io/aisurvey-fe/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle OPTIONS requests for CORS preflight (needed in some deployments)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return JSONResponse(content={"message": "CORS preflight successful"})

class CoreIdeasRequest(BaseModel):
    ideas: list[str]

@app.post("/update-database/")
async def update_database(data: CoreIdeasRequest):
    database = load_database()
    updated_database = process_ideas(data.ideas, database)
    save_database(updated_database)
    return {"message": "Database updated successfully", "updated_count": len(data.ideas)}

@app.get("/")
async def root():
    return {"message": "Survey database backend is running!"}