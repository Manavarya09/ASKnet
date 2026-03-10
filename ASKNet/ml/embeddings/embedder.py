from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using fallback embeddings.")


class Embedder:
    """Embedding generator for text. Uses SentenceTransformers if available, otherwise fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                print(f"Loaded SentenceTransformer model: {model_name}")
            except Exception as e:
                print(f"Error loading SentenceTransformer: {e}")
                self.model = None
        else:
            print(
                "Using fallback embedding (hash-based) - install sentence-transformers for better quality."
            )

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        if self.model is not None:
            return self.model.encode(texts)
        else:
            # Fallback: simple hash-based embedding
            embeddings = []
            for text in texts:
                # Create a simple deterministic embedding based on character ord values
                emb = []
                for char in text[:100]:  # Use first 100 chars
                    emb.append(ord(char) % 256 / 255.0)
                # Pad to fixed size
                while len(emb) < 100:
                    emb.append(0.0)
                embeddings.append(emb)
            return np.array(embeddings, dtype=np.float32)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text."""
        return self.encode([text])[0]
