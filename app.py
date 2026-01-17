from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import uvicorn

# Import our logic
from analyzer.scorer import analyze_user

app = FastAPI(title="Skill Evidence Engine")

# Define what the JSON input must look like
class AnalysisRequest(BaseModel):
    github_username: str
    skills: List[str]

@app.get("/")
def home():
    return {"status": "System is online. Use POST /analyze/github"}

@app.post("/analyze/github")
def analyze(request: AnalysisRequest):
    # Retrieve the token we "exported" earlier
    TOKEN = os.getenv("GITHUB_TOKEN") 
    
    if not TOKEN:
        raise HTTPException(
            status_code=500, 
            detail="Server missing GITHUB_TOKEN. Did you set the environment variable?"
        )

    try:
        results = analyze_user(request.github_username, request.skills, TOKEN)
        return results
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # This allows you to run it with 'python app.py' directly
    uvicorn.run(app, host="0.0.0.0", port=8000)