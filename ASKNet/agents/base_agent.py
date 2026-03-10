import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Get a logger with a consistent format."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class BaseAgent(ABC):
    """Base class for all agents in the ASK-Net system."""

    def __init__(self, name: str, memory_store=None, embedder=None):
        self.name = name
        self.memory = memory_store
        self.embedder = embedder
        self.logger = get_logger(name)
        self.trust_score = 0.5  # Default trust score

    @abstractmethod
    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a task and return result."""
        pass

    async def log_interaction(
        self,
        task_id: str,
        sender: str,
        receiver: str,
        message: str,
        confidence: float = 0.5,
    ):
        """Log interaction to memory store."""
        if self.memory:
            interaction = {
                "task_id": task_id,
                "sender": sender,
                "receiver": receiver,
                "message": message,
                "confidence": confidence,
                "timestamp": self._get_timestamp(),
            }
            await self.memory.store(
                f"interaction_{task_id}_{self.name}", json.dumps(interaction)
            )

    def update_trust(self, reward: float):
        """Update agent trust score based on reward."""
        self.trust_score = max(0.0, min(1.0, self.trust_score + reward * 0.1))
        self.logger.info(f"Updated trust score for {self.name}: {self.trust_score:.3f}")

    def _get_timestamp(self):
        from datetime import datetime

        return datetime.utcnow().isoformat()
