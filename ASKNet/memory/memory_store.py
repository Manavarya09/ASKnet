import json
import os
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime


class MemoryStore:
    """Simple file-based memory store for the MVP. Can be swapped with PostgreSQL."""

    def __init__(self, filepath: str = "memory_store.json"):
        self.filepath = filepath
        self.data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._load()

    def _load(self):
        """Load data from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}
        else:
            self.data = {}

    async def store(self, key: str, value: Any):
        """Store a key-value pair."""
        async with self._lock:
            self.data[key] = {
                "value": value,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self._save()

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        async with self._lock:
            entry = self.data.get(key)
            return entry.get("value") if entry else None

    async def search(self, prefix: str) -> Dict[str, Any]:
        """Search for keys with a given prefix."""
        async with self._lock:
            return {k: v for k, v in self.data.items() if k.startswith(prefix)}

    async def delete(self, key: str):
        """Delete a key-value pair."""
        async with self._lock:
            if key in self.data:
                del self.data[key]
                self._save()

    def _save(self):
        """Save data to file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving memory store: {e}")

    async def clear(self):
        """Clear all data."""
        async with self._lock:
            self.data = {}
            self._save()
