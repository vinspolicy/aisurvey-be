from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from matching_logic import update_database

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.post("/update/")
async def update_core_ideas(data: Request):
    body = await data.json()
    core_ideas = body.get("core_ideas", [])
    result = update_database(core_ideas)
    return result