import json
from typing import Any, Dict, Optional
from datetime import datetime

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asknet_dir = os.path.dirname(current_dir)
if asknet_dir not in sys.path:
    sys.path.insert(0, asknet_dir)

from agents.base_agent import BaseAgent
from memory.memory_store import MemoryStore


class MemoryAgent(BaseAgent):
    """Agent responsible for persistent memory storage and retrieval."""

    def __init__(self, memory_store: MemoryStore):
        super().__init__("MemoryAgent", memory_store=memory_store)
        self.memory_store = memory_store

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory storage/retrieval tasks."""
        operation = task.get("operation", "store")
        key = task.get("key")
        value = task.get("value")

        if operation == "store" and key and value is not None:
            await self.memory_store.store(key, value)
            return {"status": "stored", "key": key}

        elif operation == "retrieve" and key:
            result = await self.memory_store.retrieve(key)
            return {"status": "retrieved", "key": key, "value": result}

        elif operation == "search" and key:
            results = await self.memory_store.search(key)
            return {"status": "searched", "key": key, "results": results}

        return {"status": "error", "message": "Invalid memory operation"}

    async def store_interaction(self, task_id: str, interaction: Dict[str, Any]):
        """Store an interaction for later retrieval."""
        key = f"interaction_{task_id}_{interaction.get('sender')}_{interaction.get('receiver')}"
        await self.memory_store.store(key, json.dumps(interaction))

    async def store_feedback(self, task_id: str, rating: int, comments: str):
        """Store user feedback."""
        key = f"feedback_{task_id}"
        feedback = {
            "task_id": task_id,
            "rating": rating,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.memory_store.store(key, json.dumps(feedback))

    async def get_task_context(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context for a task."""
        interactions = await self.memory_store.search(f"interaction_{task_id}")
        feedback = await self.memory_store.retrieve(f"feedback_{task_id}")
        return {"interactions": interactions, "feedback": feedback}
