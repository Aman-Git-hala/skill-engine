import os
import shutil
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from analyzer.scorer import analyze_user

# --- NUCLEAR FIX: Clean environment on startup ---
# This ensures no old, bad files exist.
if os.path.exists("reference_embeddings"):
    print("☢️  NUCLEAR FIX: Deleting old reference_embeddings folder...")
    shutil.rmtree("reference_embeddings")

# Check inside analyzer folder too, just in case
if os.path.exists("analyzer/reference_embeddings"):
    print("☢️  NUCLEAR FIX: Deleting old analyzer/reference_embeddings folder...")
    shutil.rmtree("analyzer/reference_embeddings")
# ------------------------------------------------

app = FastAPI()

# Enable CORS (allows your frontend/friends to talk to the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Skill Engine is Active 🚀. Go to /docs to test it."}

@app.post("/analyze/github")
async def analyze_github_user(payload: dict = Body(...)):
    """
    Analyzes a GitHub user's code quality vs professional standards.
    Input: { "github_username": "torvalds", "skills": ["C", "Python"] }
    Streamed Response (NDJSON): Each line is a JSON object for a skill.
    """
    username = payload.get("github_username")
    skills = payload.get("skills", [])
    
    # Get token from environment variable (Secure)
    github_token = os.getenv("GITHUB_TOKEN")

    if not username or not skills:
        raise HTTPException(status_code=400, detail="Missing username or skills")

    if not github_token:
        print("⚠️ Warning: GITHUB_TOKEN not set. Rate limits will be tight.")
    
    async def generate_results():
        try:
            # Yield user info first (optional, but helpful key)
            yield json.dumps({"user": username, "status": "processing"}) + "\n"
            
            # Iterate over the generator from scorer
            for result in analyze_user(username, skills, github_token):
                yield json.dumps(result) + "\n"
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(generate_results(), media_type="application/x-ndjson")