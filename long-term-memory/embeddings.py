from sentence_transformers import SentenceTransformer
import numpy as np
import config

class EmbeddingManager:
    """Manages embedding generation using sentence-transformers"""
    
    def __init__(self):
        print(f"📦 Loading embedding model: {config.EMBEDDING_MODEL}...")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        print(f"✅ Embedding model loaded! Dimension: {config.EMBEDDING_DIM}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of shape (384,)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: list) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            numpy array of shape (n, 384)
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Cosine similarity = dot product / (norm1 * norm2)
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        similarity = dot_product / (norm1 * norm2)
        
        # Convert to 0-1 range (cosine similarity is -1 to 1)
        similarity = (similarity + 1) / 2
        
        return float(similarity)

# Global instance
embedding_manager = EmbeddingManager()
