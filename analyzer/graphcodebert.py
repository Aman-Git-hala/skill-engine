import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load the model GLOBALLY so we only do it once (saves RAM)
print("⏳ Loading GraphCodeBERT (CPU)... this may take a minute...")

# We use the specific Microsoft pre-trained model for code
tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")
model = AutoModel.from_pretrained("microsoft/graphcodebert-base")

# Force CPU usage (Safety Rule: No Overheating)
device = torch.device("cpu")
model.to(device)

print("✅ Model Loaded.")

def get_embedding(code_snippet):
    """
    Converts a string of code into a mathematical vector.
    """
    if not code_snippet or not isinstance(code_snippet, str):
        return np.zeros((768,)) # Return empty vector if code is bad
        
    # Truncate to 512 tokens. 
    # If we don't truncate, the model will crash on large files.
    inputs = tokenizer(code_snippet, return_tensors="pt", max_length=512, truncation=True, padding=True)
    
    # Move inputs to CPU
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad(): # Disable gradient calculation to save massive RAM
        outputs = model(**inputs)
        # We take the embedding of the [CLS] token (the first one) 
        # which represents the "whole meaning" of the code snippet.
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
    # Flatten to a simple 1D array
    return embedding.flatten()

def compute_similarity(user_code_embeddings, reference_embedding):
    """
    Compares the user's code vectors against the 'Gold Standard' reference.
    """
    if not user_code_embeddings:
        return 0.0
    
    # Ensure formats are correct for scikit-learn
    # We stack the user's multiple files into a matrix
    user_matrix = np.vstack(user_code_embeddings)
    
    # Reshape reference to be a 1-row matrix
    ref_matrix = reference_embedding.reshape(1, -1)
    
    # Calculate cosine similarity (0 to 1) for every file
    scores = cosine_similarity(user_matrix, ref_matrix)
    
    # We return the AVERAGE similarity. 
    # (You could also take max() if you want to be lenient)
    return float(np.mean(scores))