from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matching_logic import update_database

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IdeasPayload(BaseModel):
    core_ideas: list[str]

@app.post("/update/")
async def update_core_ideas(payload: IdeasPayload):
    if not payload.core_ideas:
        raise HTTPException(status_code=400, detail="No core ideas provided.")
    
    result = update_database(payload.core_ideas)
    return {"update_summary": result}