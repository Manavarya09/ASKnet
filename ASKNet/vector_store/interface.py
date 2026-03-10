import os
import pickle
from typing import List, Optional, Tuple
import numpy as np

FAISS_AVAILABLE = False
try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    pass


class VectorStore:
    """Vector store for semantic search. Uses FAISS if available, otherwise in-memory."""

    def __init__(self, dimension: int = 384, index_path: str = "faiss_index.bin"):
        self.dimension = dimension
        self.index_path = index_path
        self.documents: List[str] = []
        self.embeddings: np.ndarray = np.zeros((0, dimension), dtype=np.float32)

        if FAISS_AVAILABLE:
            try:
                import faiss

                self.index = faiss.IndexFlatL2(dimension)
                self._load_index()
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                self.index = None
        else:
            self.index = None  # Will use in-memory search

    def _load_index(self):
        """Load FAISS index from disk if exists."""
        if os.path.exists(self.index_path) and FAISS_AVAILABLE:
            try:
                import faiss

                self.index = faiss.read_index(self.index_path)
                # Load documents
                doc_path = self.index_path + ".docs"
                if os.path.exists(doc_path):
                    with open(doc_path, "rb") as f:
                        self.documents = pickle.load(f)
            except Exception as e:
                print(f"Error loading FAISS index: {e}")

    def _save_index(self):
        """Save FAISS index to disk."""
        if FAISS_AVAILABLE and hasattr(self, "index") and self.index is not None:
            try:
                import faiss

                faiss.write_index(self.index, self.index_path)
                doc_path = self.index_path + ".docs"
                with open(doc_path, "wb") as f:
                    pickle.dump(self.documents, f)
            except Exception as e:
                print(f"Error saving FAISS index: {e}")

    def add_documents(self, documents: List[str], embeddings: np.ndarray):
        """Add documents with their embeddings."""
        if len(documents) != len(embeddings):
            raise ValueError("Documents and embeddings must have the same length")

        self.documents.extend(documents)

        if FAISS_AVAILABLE and self.index is not None:
            try:
                import faiss

                self.index.add(embeddings.astype(np.float32))
                self._save_index()
            except Exception as e:
                print(f"Error adding to FAISS index: {e}")
                # Fall back to in-memory
                if self.embeddings.size == 0:
                    self.embeddings = embeddings.astype(np.float32)
                else:
                    self.embeddings = np.vstack(
                        [self.embeddings, embeddings.astype(np.float32)]
                    )
        else:
            # In-memory fallback
            if self.embeddings.size == 0:
                self.embeddings = embeddings.astype(np.float32)
            else:
                self.embeddings = np.vstack(
                    [self.embeddings, embeddings.astype(np.float32)]
                )

    def search(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> List[Tuple[str, float]]:
        """Search for similar documents."""
        query_embedding = np.array([query_embedding], dtype=np.float32)

        if FAISS_AVAILABLE and self.index is not None:
            try:
                import faiss

                distances, indices = self.index.search(query_embedding, k)
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx >= 0 and idx < len(self.documents):
                        results.append((self.documents[idx], float(distances[0][i])))
                return results
            except Exception as e:
                print(f"Error searching FAISS index: {e}")
                # Fall back to in-memory search
                return self._in_memory_search(query_embedding, k)
        else:
            # In-memory search
            return self._in_memory_search(query_embedding, k)

    def _in_memory_search(
        self, query_embedding: np.ndarray, k: int = 5
    ) -> List[Tuple[str, float]]:
        """In-memory L2 similarity search."""
        if self.embeddings.size == 0:
            return []
        # Calculate L2 distances
        distances = np.linalg.norm(self.embeddings - query_embedding, axis=1)
        # Get top-k
        indices = np.argsort(distances)[:k]
        results = [(self.documents[i], float(distances[i])) for i in indices]
        return results

    def search_by_text(
        self, text: str, embedder, k: int = 5
    ) -> List[Tuple[str, float]]:
        """Search for similar documents by text."""
        embedding = embedder.encode_single(text)
        return self.search(embedding, k)

    def clear(self):
        """Clear all documents."""
        self.documents = []
        if FAISS_AVAILABLE and hasattr(self, "index") and self.index is not None:
            try:
                import faiss

                self.index.reset()
            except Exception as e:
                print(f"Error clearing FAISS index: {e}")
        self.embeddings = np.zeros((0, self.dimension), dtype=np.float32)
