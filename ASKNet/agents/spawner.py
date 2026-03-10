from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from .synthesizer_agent import SynthesizerAgent
from .critic_agent import CriticAgent
from .prediction_agent import PredictionAgent
from .research_agent import ResearchAgent
from .data_agent import DataAgent


class DomainSpawner:
    """Dynamic agent spawner for domain specialization."""

    def __init__(self):
        self.domain_templates = {
            "climate_science": {
                "description": "Specialized agent for climate science analysis",
                "required_capabilities": ["data_analysis", "research", "modeling"],
                "example_tasks": [
                    "Analyze temperature trends",
                    "Assess wildfire risk",
                    "Model climate impacts",
                ],
            },
            "cardiology": {
                "description": "Specialized agent for cardiology analysis",
                "required_capabilities": ["medical_analysis", "research", "diagnosis"],
                "example_tasks": [
                    "Analyze heart disease risk factors",
                    "Review cardiology literature",
                    "Assess treatment options",
                ],
            },
            "pharmacology": {
                "description": "Specialized agent for pharmacology analysis",
                "required_capabilities": [
                    "drug_analysis",
                    "interaction_research",
                    "dosage_calculation",
                ],
                "example_tasks": [
                    "Analyze drug interactions",
                    "Review pharmacology literature",
                    "Calculate dosage recommendations",
                ],
            },
        }

        self.active_agents: Dict[str, BaseAgent] = {}

    def spawn_domain_agent(self, domain: str, task: Dict[str, Any]) -> BaseAgent:
        """Spawn a new domain-specific agent based on the task."""
        domain_config = self.domain_templates.get(domain)

        if not domain_config:
            # Fall back to a generic synthesizer agent
            agent = SynthesizerAgent()
            agent.name = f"{domain.capitalize()}Agent"
            return agent

        # Create specialized agent based on domain
        if domain == "climate_science":
            # In a real system, this would create a specialized ClimateScienceAgent
            agent = SynthesizerAgent()
            agent.name = "ClimateScienceAgent"
        elif domain == "cardiology":
            agent = SynthesizerAgent()
            agent.name = "CardiologyAgent"
        elif domain == "pharmacology":
            agent = SynthesizerAgent()
            agent.name = "PharmacologyAgent"
        else:
            agent = SynthesizerAgent()
            agent.name = f"{domain.capitalize()}Agent"

        # Store in active agents
        agent_id = f"{domain}_{len(self.active_agents)}"
        self.active_agents[agent_id] = agent

        return agent

    def determine_domain_from_task(self, task: Dict[str, Any]) -> str:
        """Determine which domain is needed based on the task description."""
        query = task.get("query", "").lower()

        # Simple keyword-based domain detection
        climate_keywords = [
            "climate",
            "weather",
            "temperature",
            "drought",
            "wildfire",
            "rainfall",
        ]
        medical_keywords = [
            "heart",
            "cardio",
            "medical",
            "disease",
            "patient",
            "hospital",
        ]
        drug_keywords = ["drug", "pharmacy", "medication", "treatment", "prescription"]

        query_words = query.split()

        # Count keyword matches
        climate_matches = sum(1 for word in query_words if word in climate_keywords)
        medical_matches = sum(1 for word in query_words if word in medical_keywords)
        drug_matches = sum(1 for word in query_words if word in drug_keywords)

        # Return the domain with the most matches
        if climate_matches >= medical_matches and climate_matches >= drug_matches:
            return "climate_science"
        elif medical_matches >= climate_matches and medical_matches >= drug_matches:
            return "cardiology"
        elif drug_matches >= 1:
            return "pharmacology"
        else:
            return "general"

    def get_domain_capabilities(self, domain: str) -> List[str]:
        """Get the capabilities of a domain-specific agent."""
        domain_config = self.domain_templates.get(domain)
        return domain_config.get("required_capabilities", []) if domain_config else []

    def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all active spawned agents."""
        return [
            {"agent_id": agent_id, "name": agent.name, "type": type(agent).__name__}
            for agent_id, agent in self.active_agents.items()
        ]

    def retire_agent(self, agent_id: str):
        """Retire an active agent."""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]


class TaskPlannerAgent(BaseAgent):
    """Task Planner Agent for decomposing queries and assigning tasks."""

    def __init__(self, spawner: DomainSpawner):
        super().__init__("TaskPlannerAgent")
        self.spawner = spawner

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a user query into subtasks and assign to agents."""
        query = task.get("query", "")
        user_id = task.get("user_id", "unknown")

        # Determine domain
        domain = self.spawner.determine_domain_from_task(task)

        # Create subtasks based on domain
        if domain == "climate_science":
            subtasks = self._create_climate_subtasks(query)
        else:
            subtasks = self._create_generic_subtasks(query)

        # Assign subtasks to agents
        assignments = []
        for subtask in subtasks:
            assignment = {
                "subtask": subtask,
                "assigned_agent": self._assign_agent(subtask, domain),
                "domain": domain,
            }
            assignments.append(assignment)

        # Create domain specialist if needed
        if domain != "general":
            specialist_agent = self.spawner.spawn_domain_agent(domain, task)
            assignments.append(
                {
                    "subtask": "Specialist analysis",
                    "assigned_agent": specialist_agent.name,
                    "domain": domain,
                }
            )

        return {
            "status": "planned",
            "query": query,
            "domain": domain,
            "subtasks": subtasks,
            "assignments": assignments,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _create_climate_subtasks(self, query: str) -> List[Dict[str, Any]]:
        """Create subtasks for climate-related queries."""
        subtasks = []

        # Research task
        subtasks.append(
            {
                "id": "research_1",
                "type": "research",
                "goal": f"Gather evidence about: {query}",
                "constraints": ["reliable sources", "recent data"],
            }
        )

        # Data analysis task
        subtasks.append(
            {
                "id": "data_1",
                "type": "data_analysis",
                "goal": f"Analyze relevant climate datasets",
                "constraints": ["structured data", "numerical analysis"],
            }
        )

        # Prediction task
        subtasks.append(
            {
                "id": "prediction_1",
                "type": "prediction",
                "goal": "Generate forecasts using ML models",
                "constraints": ["quantitative", "uncertainty estimates"],
            }
        )

        # Debate task
        subtasks.append(
            {
                "id": "debate_1",
                "type": "debate",
                "goal": "Critique and refine findings",
                "constraints": ["multi-agent", "iterative refinement"],
            }
        )

        # Synthesis task
        subtasks.append(
            {
                "id": "synthesis_1",
                "type": "synthesis",
                "goal": "Combine insights into final answer",
                "constraints": ["comprehensive", "well-structured"],
            }
        )

        return subtasks

    def _create_generic_subtasks(self, query: str) -> List[Dict[str, Any]]:
        """Create generic subtasks for general queries."""
        return [
            {
                "id": "research_1",
                "type": "research",
                "goal": f"Research information about: {query}",
                "constraints": [],
            },
            {
                "id": "synthesis_1",
                "type": "synthesis",
                "goal": "Synthesize findings into answer",
                "constraints": [],
            },
        ]

    def _assign_agent(self, subtask: Dict[str, Any], domain: str) -> str:
        """Assign a subtask to an appropriate agent."""
        task_type = subtask.get("type", "")

        agent_mapping = {
            "research": "ResearchAgent",
            "data_analysis": "DataAgent",
            "prediction": "PredictionAgent",
            "debate": "DebateCoordinator",
            "synthesis": "SynthesizerAgent",
        }

        return agent_mapping.get(task_type, "SynthesizerAgent")
