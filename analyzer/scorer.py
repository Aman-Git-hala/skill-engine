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

def get_reference_embedding(skill):
    """
    Smart loader that checks for dimension mismatches and auto-heals.
    """
    # Create folder if missing
    if not os.path.exists("reference_embeddings"):
        os.makedirs("reference_embeddings")

    # Normalize filename (e.g. "C++" -> "cpp.pkl")
    safe_name = skill.lower().replace("++", "plusplus").replace("#", "sharp").replace(" ", "")
    path = f"reference_embeddings/{safe_name}.pkl"
    
    embedding = None

    # 1. Try to load existing file
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                
            # --- CRITICAL FIX: CHECK DIMENSIONS ---
            # If it's the old "Big" model (2304) or corrupted, discard it.
            # We expect 768 dimensions for CodeBERTa-small.
            if hasattr(data, "shape") and (data.shape[0] == 768 or data.size == 768):
                embedding = data
            else:
                print(f"⚠️  CORRUPT/OLD EMBEDDING FOUND FOR {skill} (Shape: {getattr(data, 'shape', 'Unknown')}). Deleting...")
                os.remove(path)
        except Exception as e:
            print(f"⚠️  Error reading {path}: {e}. Deleting...")
            if os.path.exists(path):
                os.remove(path)

    # 2. If missing or deleted, generate a fresh fallback
    if embedding is None:
        print(f"🔄 Generating fresh fallback embedding for {skill}...")
        dummy_code = f"// Standard implementation reference for {skill}\nprint('Hello World');"
        embedding = get_embedding(dummy_code)
        
        # Save it so we don't calculate again
        with open(path, "wb") as f:
            pickle.dump(embedding, f)
    
    return embedding

def analyze_user(username, skills, github_token):
    # 1. Fetch Repos
    print(f"🔍 Fetching repos for {username}...")
    repos = fetch_user_data(username, github_token)
    
    if not repos:
        yield {"error": "User not found or no public repos."}
        return

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
            
            # ⚡️ EARLY EXIT: If we have > 3 snippets, STOP searching.
            if len(code_snippets) >= 3:
                break
        
        # 3. AI Analysis
        # Use our new Smart Loader
        ref_emb = get_reference_embedding(skill)
        
        user_embeddings = [get_embedding(code) for code in code_snippets]
        
        sim_score = 0.0
        evidence_label = "Weak"
        
        if user_embeddings:
            # Aggregate multiple code snippets into one user profile (Mean Pooling)
            user_agg = np.mean(user_embeddings, axis=0)
            sim_score = compute_similarity(user_agg, ref_emb)
            
        # ⚖️ CALIBRATION
        if sim_score > 0.75: evidence_label = "Strong"
        elif sim_score > 0.45: evidence_label = "Moderate"
            
        skill_result = {
            "semantic_similarity": { 
                "score": round(sim_score, 2), 
                "evidence": evidence_label 
            },
            "complexity": analyze_complexity(code_snippets),
            "project_maturity": analyze_maturity(relevant_repos),
            "consistency": analyze_consistency(repos, skill),
            "recency": analyze_recency(relevant_repos)
        }

        # Yield result for this skill immediately
        yield {skill: skill_result}