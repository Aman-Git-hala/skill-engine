import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

class GraphCodeBERT:
    def __init__(self):
        # Using "Small" model to fit in Render Free Tier (512MB RAM)
        self.model_name = "huggingface/CodeBERTa-small-v1"
        
        print(f"Loading Analyzer Model: {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.eval() # Set to evaluation mode

    def get_embedding(self, code_snippet):
        """
        Converts a string of code into a dense vector (embedding).
        """
        if not code_snippet or not isinstance(code_snippet, str):
            return np.zeros(768) # Return empty vector if code is invalid

        try:
            inputs = self.tokenizer(
                code_snippet, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Mean pooling to capture the overall semantic meaning
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return np.zeros(768)

# --- EXPORTED FUNCTIONS (To fix the ImportError) ---

# 1. Create a global instance of the model
_bert_instance = GraphCodeBERT()

# 2. Expose the function so scorer.py can import it
def get_embedding(code_snippet):
    return _bert_instance.get_embedding(code_snippet)

# 3. Expose the similarity function
def compute_similarity(embedding1, embedding2):
    """
    Calculates cosine similarity between two embeddings.
    """
    if embedding1 is None or embedding2 is None:
        return 0.0
        
    # Ensure they are numpy arrays
    e1 = np.array(embedding1).reshape(1, -1)
    e2 = np.array(embedding2).reshape(1, -1)
    
    return float(cosine_similarity(e1, e2)[0][0])