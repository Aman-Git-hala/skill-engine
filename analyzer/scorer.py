import pickle
import os
import numpy as np

# Import our logic modules
from .github_fetcher import fetch_user_data, fetch_file_content
from .graphcodebert import get_embedding, compute_similarity
from .heuristics import analyze_complexity, analyze_maturity, analyze_consistency, analyze_recency

# --- THE ULTIMATE SKILL MAP ---
SKILL_MAP = {
    "Python": [".py", ".ipynb"],
    "Java": [".java"],
    "C": [".c", ".h"],
    "C++": [".cpp", ".hpp", ".cc", ".cxx", ".h"],
    "C#": [".cs"],
    "Go": [".go"],
    "Rust": [".rs"],
    "JavaScript": [".js", ".jsx", ".mjs", ".html"],
    "TypeScript": [".ts", ".tsx"],
    "PHP": [".php"],
    "Ruby": [".rb"],
    "Swift": [".swift"],
    "Kotlin": [".kt", ".kts"],
    "HTML": [".html", ".htm", ".xhtml"],
    "CSS": [".css", ".scss", ".sass", ".less"],
    "React": [".jsx", ".tsx", ".js", ".ts"],
    "Vue": [".vue", ".js", ".ts"],
    "Angular": [".ts", ".html"],
    "Next.js": [".jsx", ".tsx", ".js", ".ts"],
    "Django": [".py"],
    "Flask": [".py"],
    "FastAPI": [".py"],
    "Node.js": [".js", ".ts", ".json"],
    "Pandas": [".py", ".ipynb"],
    "NumPy": [".py", ".ipynb"],
    "PyTorch": [".py", ".ipynb"],
    "TensorFlow": [".py", ".ipynb"],
    "Flutter": [".dart"],
    "React Native": [".jsx", ".tsx", ".js", ".ts"],
    "Solidity": [".sol"],
    "Docker": ["Dockerfile", ".dockerfile", "docker-compose.yml"],
    "SQL": [".sql", ".ddl"]
}

def generate_reference_if_missing(skill):
    if not os.path.exists("reference_embeddings"):
        os.makedirs("reference_embeddings")

    safe_name = skill.lower().replace("++", "plusplus").replace("#", "sharp").replace(" ", "")
    path = f"reference_embeddings/{safe_name}.pkl"
    
    if not os.path.exists(path):
        dummy_code = "def main(): print('hello world')"
        emb = get_embedding(dummy_code)
        with open(path, "wb") as f:
            pickle.dump(emb, f)
    
    with open(path, "rb") as f:
        return pickle.load(f)

def analyze_user(username, skills, github_token):
    results = {}
    
    # 1. Fetch Repos
    print(f"🔍 Fetching repos for {username}...")
    repos = fetch_user_data(username, github_token)
    
    if not repos:
        return {"error": "User not found or no public repos."}

    for skill in skills:
        print(f"  Analyzing skill: {skill}...")
        
        extensions = SKILL_MAP.get(skill, [".txt"])
        
        code_snippets = []
        relevant_repos = []

        # ⚡️ SPEED LIMIT: Only deep scan the top 6 repos
        max_repos_to_scan = 6
        
        for repo in repos[:max_repos_to_scan]:
            found_files = fetch_file_content(repo['object'], extensions)
            
            if found_files:
                code_snippets.extend(found_files)
                relevant_repos.append(repo)
            
            # ⚡️ EARLY EXIT: If we have > 3 snippets, STOP searching other repos.
            # We don't need to see ALL their code, just enough to judge.
            if len(code_snippets) >= 3:
                break
        
        # 3. AI Analysis
        ref_emb = generate_reference_if_missing(skill)
        user_embeddings = [get_embedding(code) for code in code_snippets]
        
        sim_score = 0.0
        evidence_label = "Weak"
        
        if user_embeddings:
            sim_score = compute_similarity(user_embeddings, ref_emb)
            
        # ⚖️ CALIBRATION: Stricter Thresholds
        # 0.75 means "Very similar to professional reference"
        # 0.45 means "Vaguely similar"
        if sim_score > 0.75: evidence_label = "Strong"
        elif sim_score > 0.45: evidence_label = "Moderate"
            
        results[skill] = {
            "semantic_similarity": { 
                "score": round(sim_score, 2), 
                "evidence": evidence_label 
            },
            "complexity": analyze_complexity(code_snippets),
            "project_maturity": analyze_maturity(relevant_repos),
            "consistency": analyze_consistency(repos, skill),
            "recency": analyze_recency(relevant_repos)
        }
        
    return results