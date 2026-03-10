from typing import Any, Dict, List
from datetime import datetime

from .base_agent import BaseAgent


class SynthesizerAgent(BaseAgent):
    """Synthesizer agent for combining outputs into the final answer."""

    def __init__(self):
        super().__init__("SynthesizerAgent")

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final answer from multiple agent outputs."""
        agent_outputs = task.get("agent_outputs", [])
        critique_results = task.get("critique_results", {})
        context = task.get("context", {})

        # Extract key information from outputs
        claims = self._extract_claims(agent_outputs)

        # Apply critiques
        refined_claims = self._apply_critiques(claims, critique_results)

        # Generate final synthesis
        final_answer = self._generate_synthesis(refined_claims, context)

        # Create citations
        citations = self._generate_citations(agent_outputs)

        return {
            "status": "synthesized",
            "final_answer": final_answer,
            "refined_claims": refined_claims,
            "citations": citations,
            "summary_of_reasoning": self._create_summary(agent_outputs),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _extract_claims(
        self, agent_outputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract key claims from agent outputs."""
        claims = []

        for output in agent_outputs:
            agent_name = output.get("agent", "Unknown")
            content = output.get("content", "")

            if "prediction" in agent_name.lower() or "forecast" in agent_name.lower():
                # Extract numerical predictions
                if "wildfire_risk" in content:
                    claims.append(
                        {
                            "type": "prediction",
                            "content": content,
                            "agent": agent_name,
                            "confidence": output.get("confidence", 0.5),
                        }
                    )
            elif "research" in agent_name.lower():
                # Extract evidence claims
                claims.append(
                    {
                        "type": "evidence",
                        "content": content,
                        "agent": agent_name,
                        "confidence": output.get("confidence", 0.5),
                    }
                )
            elif "data" in agent_name.lower():
                # Extract data insights
                claims.append(
                    {
                        "type": "data_insight",
                        "content": content,
                        "agent": agent_name,
                        "confidence": output.get("confidence", 0.5),
                    }
                )

        return claims

    def _apply_critiques(
        self, claims: List[Dict[str, Any]], critique_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply critiques to refine claims."""
        critiques = critique_results.get("critiques", [])

        for claim in claims:
            # Find critiques for this claim
            for critique in critiques:
                if claim.get("content") == critique.get("claim"):
                    # Apply suggestions
                    if critique.get("verdict") == "needs_refinement":
                        claim["refined"] = True
                        claim["suggestions"] = critique.get("suggestions", [])
                    elif critique.get("verdict") == "needs_reconsideration":
                        claim["needs_reconsideration"] = True
                        claim["issues"] = critique.get("issues", [])

        return claims

    def _generate_synthesis(
        self, claims: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> str:
        """Generate the final synthesized answer."""
        # Extract key information from claims
        predictions = [c for c in claims if c.get("type") == "prediction"]
        evidence = [c for c in claims if c.get("type") == "evidence"]
        data_insights = [c for c in claims if c.get("type") == "data_insight"]

        # Build synthesis
        synthesis_parts = []

        # Introduction
        synthesis_parts.append(
            "Based on a comprehensive analysis of climate data and predictive modeling:"
        )

        # Key findings
        if data_insights:
            synthesis_parts.append("\nKey Data Insights:")
            for insight in data_insights[:2]:  # Limit to top 2
                synthesis_parts.append(f"- {insight['content']}")

        # Predictions
        if predictions:
            synthesis_parts.append("\nPredictive Analysis:")
            for pred in predictions:
                synthesis_parts.append(f"- {pred['content']}")

        # Evidence
        if evidence:
            synthesis_parts.append("\nSupporting Evidence:")
            for ev in evidence[:2]:
                synthesis_parts.append(f"- {ev['content']}")

        # Recommendations
        synthesis_parts.append("\nRecommendations:")
        synthesis_parts.append("- Monitor regional climate conditions regularly")
        synthesis_parts.append("- Implement early warning systems for wildfire risk")
        synthesis_parts.append("- Develop adaptive mitigation strategies")

        return "\n".join(synthesis_parts)

    def _generate_citations(
        self, agent_outputs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate citations for the synthesis."""
        citations = []

        for i, output in enumerate(agent_outputs):
            citations.append(
                {
                    "source": output.get("agent", "Unknown"),
                    "content_preview": output.get("content", "")[:100] + "..."
                    if len(output.get("content", "")) > 100
                    else output.get("content", ""),
                    "timestamp": output.get("timestamp", datetime.utcnow().isoformat()),
                }
            )

        return citations

    def _create_summary(self, agent_outputs: List[Dict[str, Any]]) -> str:
        """Create a summary of the reasoning process."""
        agents = [o.get("agent", "Unknown") for o in agent_outputs]

        summary_parts = [
            f"Analysis conducted by {len(agents)} specialized agents:",
            f"- Research Agent: Gathered climate evidence",
            f"- Data Agent: Processed climate datasets",
            f"- Prediction Agent: Generated forecasts using ML models",
            f"- Critic Agent: Evaluated reasoning and identified gaps",
            f"- Debate Coordinator: Managed multi-round discussions",
            f"Final synthesis combined insights from all agents with proper validation.",
        ]

        return "\n".join(summary_parts)
