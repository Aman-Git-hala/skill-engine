import os
import shutil

# 1. DELETE OLD EMBEDDINGS (The "Nuclear" Option)
if os.path.exists("reference_embeddings"):
    shutil.rmtree("reference_embeddings")
    print("✅ DELETED old reference_embeddings folder.")

# 2. OVERWRITE seed_references.py with the CORRECT code
correct_seed_code = """import os
import torch
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModel

# FORCE SMALL MODEL
MODEL_NAME = "huggingface/CodeBERTa-small-v1" 
EMBEDDING_DIR = "reference_embeddings"

REFERENCE_CODE = {
    "Python": "def factorial(n): return 1 if n == 0 else n * factorial(n-1)",
    "C": "int factorial(int n) { return (n == 0) ? 1 : n * factorial(n - 1); }",
    "C++": "int factorial(int n) { return (n == 0) ? 1 : n * factorial(n - 1); }",
    "Java": "public int factorial(int n) { return (n == 0) ? 1 : n * factorial(n - 1); }",
    "JavaScript": "function factorial(n) { return (n === 0) ? 1 : n * factorial(n - 1); }",
    "Go": "func factorial(n int) int { if n == 0 { return 1 } return n * factorial(n-1) }",
    "Rust": "fn factorial(n: u32) -> u32 { if n == 0 { 1 } else { n * factorial(n - 1) } }",
    "PHP": "function factorial($n) { return ($n == 0) ? 1 : $n * factorial($n - 1); }",
    "Ruby": "def factorial(n) return 1 if n == 0; n * factorial(n - 1) end",
    "Swift": "func factorial(_ n: Int) -> Int { return (n == 0) ? 1 : n * factorial(n - 1) }",
    "Kotlin": "fun factorial(n: Int): Int { return if (n == 0) 1 else n * factorial(n - 1) }",
}

def generate_embeddings():
    print(f"Loading model: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    
    if not os.path.exists(EMBEDDING_DIR):
        os.makedirs(EMBEDDING_DIR)

    print("Generating reference embeddings...")
    for language, code in REFERENCE_CODE.items():
        inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Mean pooling to get 768 dimensions
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        file_path = os.path.join(EMBEDDING_DIR, f"{language}.pkl")
        with open(file_path, "wb") as f:
            pickle.dump(embedding, f)
        print(f"Saved {language} embedding (Shape: {embedding.shape}).")

if __name__ == "__main__":
    generate_embeddings()
"""

with open("seed_references.py", "w") as f:
    f.write(correct_seed_code)
    print("✅ OVERWROTE seed_references.py with correct Small Model code.")

# 3. RUN THE GENERATOR
print("🚀 RUNNING generation script now...")
os.system("python seed_references.py")
print("✅ DONE! You can now restart uvicorn.")