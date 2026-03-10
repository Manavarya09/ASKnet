"""
Trust scoring system for ASK-Net agents.

Tracks agent reliability and influences decision-making.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class TrustScorer:
    """Manages trust scores for agents based on performance."""

    def __init__(self, decay_rate: float = 0.95, update_factor: float = 0.1):
        self.scores: Dict[str, float] = {}
        self.history: Dict[str, List[Dict]] = {}
        self.decay_rate = decay_rate
        self.update_factor = update_factor
        self.last_updated: Dict[str, datetime] = {}

    def get_score(self, agent_name: str, domain: Optional[str] = None) -> float:
        """Get current trust score for an agent."""
        key = agent_name if domain is None else f"{agent_name}:{domain}"
        return self.scores.get(key, 0.5)  # Default to neutral trust

    def update_score(
        self, agent_name: str, reward: float, domain: Optional[str] = None
    ):
        """Update trust score based on performance reward."""
        key = agent_name if domain is None else f"{agent_name}:{domain}"

        # Apply decay
        current_score = self.scores.get(key, 0.5)
        decayed_score = current_score * self.decay_rate

        # Apply update
        new_score = decayed_score + (reward * self.update_factor)

        # Clamp to valid range
        new_score = max(0.0, min(1.0, new_score))

        # Update
        self.scores[key] = new_score
        self.last_updated[key] = datetime.utcnow()

        # Record in history
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "old_score": current_score,
                "new_score": new_score,
                "reward": reward,
            }
        )

        # Keep history manageable
        if len(self.history[key]) > 100:
            self.history[key] = self.history[key][-100:]

        return new_score

    def apply_feedback(
        self, agent_name: str, rating: int, domain: Optional[str] = None
    ):
        """Apply user feedback to trust score."""
        # Convert 1-5 rating to -0.5 to +0.5 reward
        reward = (rating - 3) / 5.0
        return self.update_score(agent_name, reward, domain)

    def get_top_agents(
        self, domain: Optional[str] = None, limit: int = 3
    ) -> List[Dict[str, float]]:
        """Get top performing agents for a domain."""
        scores = []
        for key, score in self.scores.items():
            if domain is None or key.startswith(f"{domain}:"):
                agent_name = key.split(":")[0]
                scores.append({"agent": agent_name, "score": score})

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:limit]

    def get_agent_history(
        self, agent_name: str, domain: Optional[str] = None
    ) -> List[Dict]:
        """Get trust score history for an agent."""
        key = agent_name if domain is None else f"{agent_name}:{domain}"
        return self.history.get(key, [])

    def save_to_file(self, filepath: str):
        """Save trust scores to file."""
        data = {
            "scores": self.scores,
            "history": self.history,
            "last_updated": {k: v.isoformat() for k, v in self.last_updated.items()},
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str):
        """Load trust scores from file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            self.scores = data.get("scores", {})
            self.history = data.get("history", {})
            self.last_updated = {
                k: datetime.fromisoformat(v)
                for k, v in data.get("last_updated", {}).items()
            }
        except FileNotFoundError:
            pass  # Use defaults if file not found


class LearningCoordinator:
    """Coordinates learning across agents based on feedback and performance."""

    def __init__(self, trust_scorer: Optional[TrustScorer] = None):
        self.trust_scorer = trust_scorer or TrustScorer()
        self.feedback_log: List[Dict] = []

    def process_feedback(
        self, task_id: str, agent_outputs: List[Dict], rating: int, comments: str
    ):
        """Process feedback and update agent trust scores."""
        feedback_entry = {
            "task_id": task_id,
            "rating": rating,
            "comments": comments,
            "agent_outputs": agent_outputs,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.feedback_log.append(feedback_entry)

        # Update trust scores for each agent based on feedback
        for output in agent_outputs:
            agent_name = output.get("agent")
            if agent_name:
                self.trust_scorer.apply_feedback(agent_name, rating)

        return feedback_entry

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in feedback to identify improvement areas."""
        if not self.feedback_log:
            return {}

        recent_feedback = self.feedback_log[-100:]  # Last 100 entries

        avg_rating = sum(f["rating"] for f in recent_feedback) / len(recent_feedback)

        # Count agent mentions
        agent_counts = {}
        for feedback in recent_feedback:
            for output in feedback.get("agent_outputs", []):
                agent_name = output.get("agent")
                if agent_name:
                    agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1

        return {
            "average_rating": avg_rating,
            "total_feedback_entries": len(self.feedback_log),
            "agent_activity": agent_counts,
            "recent_entries": len(recent_feedback),
        }

    def get_recommendations(self) -> List[str]:
        """Get recommendations for improving agent performance."""
        analysis = self.analyze_patterns()
        recommendations = []

        if analysis.get("average_rating", 0) < 3.5:
            recommendations.append(
                "Consider adjusting agent reasoning strategies for better quality"
            )

        if len(self.feedback_log) > 10:
            recommendations.append(
                "Continue collecting feedback to improve agent trust scores"
            )

        return recommendations
