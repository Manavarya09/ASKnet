import json
from typing import Any, Dict, List
from datetime import datetime

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asknet_dir = os.path.dirname(current_dir)
if asknet_dir not in sys.path:
    sys.path.insert(0, asknet_dir)

from agents.base_agent import BaseAgent
from vector_store.interface import VectorStore
from ml.embeddings.embedder import Embedder


class ResearchAgent(BaseAgent):
    """Research agent for retrieving knowledge from documents and web sources."""

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        super().__init__("ResearchAgent", embedder=embedder)
        self.vector_store = vector_store

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve knowledge based on the task query."""
        query = task.get("query", "")
        sources = task.get("sources", ["climate_data", "public_docs"])
        k = task.get("k", 5)

        # Search the vector store
        results = []
        if self.embedder:
            search_results = self.vector_store.search_by_text(query, self.embedder, k=k)
            for doc, score in search_results:
                results.append(
                    {"content": doc, "score": score, "source": "vector_store"}
                )

        # If no results from vector store, return general knowledge
        if not results:
            results = self._get_general_knowledge(query, sources)

        return {
            "status": "retrieved",
            "query": query,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_general_knowledge(
        self, query: str, sources: List[str]
    ) -> List[Dict[str, Any]]:
        """Return general knowledge based on query (fallback)."""
        # This is a simple fallback; in production, this would query external APIs or documents
        if "climate" in query.lower():
            return [
                {
                    "content": "Climate change is causing increased temperatures and drought in many regions.",
                    "score": 0.8,
                    "source": "general_knowledge",
                },
                {
                    "content": "Wildfire risk increases with higher temperatures and drought conditions.",
                    "score": 0.85,
                    "source": "general_knowledge",
                },
            ]
        return [
            {
                "content": "No specific information found. Consider refining your query.",
                "score": 0.1,
                "source": "general_knowledge",
            }
        ]

    async def add_documents_to_store(self, documents: List[str]):
        """Add documents to the vector store."""
        if self.embedder:
            embeddings = self.embedder.encode(documents)
            self.vector_store.add_documents(documents, embeddings)
