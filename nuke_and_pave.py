import os
import shutil
import torch
import pickle
import numpy as np
from transformers import AutoTokenizer, AutoModel

# --- CONFIG ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_SHAPE = 768  # We want "Small" embeddings
MODEL_NAME = "huggingface/CodeBERTa-small-v1"

def nuke_old_files():
    print(f"🔍 Scanning {ROOT_DIR} for rogue 'reference_embeddings' folders...")
    
    found_any = False
    # Walk through every folder in the project
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # If we find a 'venv' or '.git' folder, skip it to be safe
        if "venv" in dirnames: dirnames.remove("venv")
        if ".git" in dirnames: dirnames.remove(".git")
        
        if "reference_embeddings" in dirnames:
            full_path = os.path.join(dirpath, "reference_embeddings")
            print(f"⚠️  FOUND FOLDER: {full_path}")
            
            # Check the files inside
            for f in os.listdir(full_path):
                if f.endswith(".pkl"):
                    file_p = os.path.join(full_path, f)
                    try:
                        with open(file_p, "rb") as pkl:
                            data = pickle.load(pkl)
                            shape = data.shape[0] if len(data.shape) > 0 else 0
                            if shape == 2304:
                                print(f"   ❌ DETECTED BAD FILE (2304 dims): {f}")
                            elif shape == 768:
                                print(f"   ✅ File is correct (768 dims): {f}")
                            else:
                                print(f"   ❓ Unknown shape {shape}: {f}")
                    except:
                        pass

            print(f"💥 DESTROYING {full_path}...")
            shutil.rmtree(full_path)
            found_any = True

    if not found_any:
        print("✅ Clean! No old folders found during scan.")
    else:
        print("✅ All old folders deleted.")

def generate_new_files():
    print(f"\n🏗️  Generating FRESH 768-dim embeddings in {ROOT_DIR}/reference_embeddings...")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    
    save_dir = os.path.join(ROOT_DIR, "reference_embeddings")
    os.makedirs(save_dir, exist_ok=True)
    
    REFERENCE_CODE = {
        "C": "int factorial(int n) { return (n == 0) ? 1 : n * factorial(n - 1); }",
        "Python": "def factorial(n): return 1 if n == 0 else n * factorial(n-1)",
        "Java": "public int factorial(int n) { return (n == 0) ? 1 : n * factorial(n - 1); }",
    }
    
    for language, code in REFERENCE_CODE.items():
        inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        # Force 768 dimensions
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        with open(os.path.join(save_dir, f"{language}.pkl"), "wb") as f:
            pickle.dump(embedding, f)
        print(f"   ✅ Saved {language}.pkl (Shape: {embedding.shape})")

if __name__ == "__main__":
    nuke_old_files()
    generate_new_files()