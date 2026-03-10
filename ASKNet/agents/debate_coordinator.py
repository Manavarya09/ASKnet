from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio

from .base_agent import BaseAgent


class DebateCoordinator(BaseAgent):
    """DebateCoordinator: Manages multi-round discussions between agents."""

    def __init__(self, max_rounds: int = 3, timeout_seconds: int = 30):
        super().__init__("DebateCoordinator")
        self.max_rounds = max_rounds
        self.timeout_seconds = timeout_seconds
        self.current_round = 0
        self.debate_history: List[Dict[str, Any]] = []

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run a debate between agents."""
        participants = task.get("participants", [])  # List of agent names
        initial_claims = task.get("initial_claims", [])
        context = task.get("context", {})

        if not participants:
            return {"status": "error", "message": "No participants provided for debate"}

        # Initialize debate
        self.current_round = 0
        self.debate_history = []

        # Initial round: present claims
        round_data = {
            "round": 1,
            "participants": participants,
            "claims": initial_claims,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.debate_history.append(round_data)

        # Simulate multi-round debate (in real system, this would route to actual agents)
        for round_num in range(2, self.max_rounds + 1):
            # Simulate agent responses
            simulated_responses = self._simulate_agent_responses(
                participants, round_num
            )

            round_data = {
                "round": round_num,
                "participants": participants,
                "responses": simulated_responses,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.debate_history.append(round_data)

            # Check if consensus reached
            if self._check_consensus(simulated_responses):
                break

        # Compile debate summary
        summary = self._compile_debate_summary()

        return {
            "status": "completed",
            "rounds": len(self.debate_history),
            "debate_history": self.debate_history,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _simulate_agent_responses(
        self, participants: List[str], round_num: int
    ) -> List[Dict[str, Any]]:
        """Simulate agent responses for demonstration."""
        responses = []
        for agent in participants:
            # Create a simulated response based on round number
            if "Research" in agent:
                responses.append(
                    {
                        "agent": agent,
                        "response": f"Research: Found additional evidence supporting climate impact in round {round_num}",
                        "confidence": 0.7 + (round_num * 0.05),
                    }
                )
            elif "Prediction" in agent:
                responses.append(
                    {
                        "agent": agent,
                        "response": f"Prediction: Updated forecast based on new data in round {round_num}",
                        "confidence": 0.75 + (round_num * 0.03),
                    }
                )
            elif "Critic" in agent:
                responses.append(
                    {
                        "agent": agent,
                        "response": f"Critic: Validated reasoning and identified minor gaps in round {round_num}",
                        "confidence": 0.8,
                    }
                )
            else:
                responses.append(
                    {
                        "agent": agent,
                        "response": f"Agent {agent}: Contributing insights in round {round_num}",
                        "confidence": 0.7,
                    }
                )
        return responses

    def _check_consensus(self, responses: List[Dict[str, Any]]) -> bool:
        """Check if agents have reached consensus."""
        if not responses:
            return False

        # Simple consensus check: if average confidence is high enough
        avg_confidence = sum(r.get("confidence", 0) for r in responses) / len(responses)
        return avg_confidence >= 0.8

    def _compile_debate_summary(self) -> Dict[str, Any]:
        """Compile a summary of the debate."""
        if not self.debate_history:
            return {}

        latest_round = self.debate_history[-1]

        return {
            "final_round": latest_round.get("round"),
            "participants_involved": self.debate_history[0].get("participants", []),
            "key_themes": [
                "Climate impact assessment",
                "Wildfire risk prediction",
                "Data-driven evidence",
                "Critical evaluation",
            ],
            "consensus_level": "high"
            if self._check_consensus(latest_round.get("responses", []))
            else "medium",
            "recommendations": [
                "Incorporate additional climate datasets",
                "Consider regional variations in wildfire risk",
                "Monitor updates from authoritative sources",
            ],
        }
