from typing import Any, Dict, List
from datetime import datetime

from .base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """Critic agent for evaluating logic, identifying inconsistencies, and challenging claims."""

    def __init__(self):
        super().__init__("CriticAgent")

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate claims and produce critiques."""
        claims = task.get("claims", [])
        context = task.get("context", {})

        critiques = []
        for claim in claims:
            critique = self._critique_claim(claim, context)
            critiques.append(critique)

        overall_evaluation = self._evaluate_overall(critiques, context)

        return {
            "status": "evaluated",
            "critiques": critiques,
            "overall_evaluation": overall_evaluation,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _critique_claim(
        self, claim: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Critique a single claim."""
        content = claim.get("content", "")
        confidence = claim.get("confidence", 0.5)
        source = claim.get("source", "unknown")

        # Simple critique rules
        issues = []
        suggestions = []

        # Check confidence level
        if confidence < 0.3:
            issues.append("Low confidence level")
            suggestions.append("Increase confidence by verifying sources")

        # Check if claim contains specific numbers
        if any(char.isdigit() for char in content):
            if "wildfire risk" in content.lower() and confidence < 0.6:
                issues.append("Numerical claim with low confidence")
                suggestions.append("Consider cross-referencing with multiple sources")
        else:
            issues.append("Vague claim without specific data")
            suggestions.append("Consider adding specific metrics or numbers")

        # Check source credibility
        if source in ["general_knowledge", "unknown"]:
            issues.append("Source credibility is limited")
            suggestions.append("Try to find peer-reviewed or authoritative sources")

        # Determine overall verdict
        if not issues:
            verdict = "acceptable"
            severity = "low"
        elif len(issues) == 1:
            verdict = "needs_refinement"
            severity = "medium"
        else:
            verdict = "needs_reconsideration"
            severity = "high"

        return {
            "claim": content,
            "source": source,
            "issues": issues,
            "suggestions": suggestions,
            "verdict": verdict,
            "severity": severity,
        }

    def _evaluate_overall(
        self, critiques: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate overall reasoning quality."""
        issues_count = sum(len(c.get("issues", [])) for c in critiques)
        high_severity = sum(1 for c in critiques if c.get("severity") == "high")

        if high_severity > 0:
            rating = 2  # Poor
            feedback = "Major issues detected. Please review all claims carefully."
        elif issues_count > 3:
            rating = 3  # Fair
            feedback = "Multiple issues detected. Consider refining claims and sources."
        elif issues_count > 0:
            rating = 4  # Good
            feedback = "Minor issues detected. Acceptable for most purposes."
        else:
            rating = 5  # Excellent
            feedback = "High-quality reasoning with strong claims."

        return {
            "rating": rating,
            "issues_count": issues_count,
            "high_severity_issues": high_severity,
            "feedback": feedback,
            "suggested_next_steps": [
                "Review high-severity critiques first",
                "Consider additional data sources",
                "Validate numerical claims with multiple methods",
            ],
        }
