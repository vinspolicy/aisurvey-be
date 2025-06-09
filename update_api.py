from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from matching_logic import process_core_ideas

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.post("/update-database/")
async def update_database(req: Request):
    data = await req.json()
    core_ideas = data.get("core_ideas", [])
    
    if not core_ideas:
        return {"error": "Missing core_ideas"}

    result = process_core_ideas(core_ideas)
    return {"status": "processed", "results": result}