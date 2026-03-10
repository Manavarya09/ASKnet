"""
Message broker for ASK-Net agent communication.

Manages message routing between agents with support for different transport modes.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid


class Message:
    """Represents a message between agents."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        content: Any,
        message_type: str = "general",
        priority: int = 0,
    ):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.priority = priority
        self.timestamp = datetime.utcnow()
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "message_type": self.message_type,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create message from dictionary."""
        msg = cls(
            sender=data["sender"],
            receiver=data["receiver"],
            content=data["content"],
            message_type=data.get("message_type", "general"),
            priority=data.get("priority", 0),
        )
        msg.id = data.get("id", str(uuid.uuid4()))
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        msg.metadata = data.get("metadata", {})
        return msg


class MessageBroker:
    """Manages message routing between agents."""

    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscriptions: Dict[str, List[str]] = {}
        self.history: List[Dict[str, Any]] = []
        self.max_history = 1000

    def register_handler(self, agent_name: str, handler: Callable):
        """Register a message handler for an agent."""
        self.routes[agent_name] = handler

    def subscribe(self, agent_name: str, message_type: str):
        """Subscribe an agent to receive messages of a type."""
        if message_type not in self.subscriptions:
            self.subscriptions[message_type] = []
        if agent_name not in self.subscriptions[message_type]:
            self.subscriptions[message_type].append(agent_name)

    async def send_message(self, message: Message) -> bool:
        """Send a message to the queue."""
        try:
            await self.message_queue.put(message)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    async def process_messages(self):
        """Process messages from the queue."""
        while True:
            try:
                message = await self.message_queue.get()
                await self._route_message(message)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing message: {e}")

    async def _route_message(self, message: Message):
        """Route a message to its destination."""
        # Add to history
        self.history.append(message.to_dict())
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        # Route to specific agent
        if message.receiver in self.routes:
            handler = self.routes[message.receiver]
            await handler(message)
        elif message.message_type in self.subscriptions:
            # Broadcast to subscribers
            for subscriber in self.subscriptions[message.message_type]:
                if subscriber in self.routes:
                    handler = self.routes[subscriber]
                    await handler(message)

    def get_message_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent message history."""
        return self.history[-limit:]

    def clear_history(self):
        """Clear message history."""
        self.history = []

    async def broadcast(self, message_type: str, content: Any, sender: str = "broker"):
        """Broadcast a message to all subscribers of a type."""
        if message_type in self.subscriptions:
            for subscriber in self.subscriptions[message_type]:
                msg = Message(
                    sender=sender,
                    receiver=subscriber,
                    content=content,
                    message_type=message_type,
                )
                await self.send_message(msg)

    def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics."""
        return {
            "queue_size": self.message_queue.qsize(),
            "total_messages": len(self.history),
            "active_routes": len(self.routes),
            "subscriptions": {k: len(v) for k, v in self.subscriptions.items()},
        }


# Global broker instance
broker = MessageBroker()
