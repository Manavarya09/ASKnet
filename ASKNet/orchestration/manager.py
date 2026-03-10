"""
Orchestration Manager for ASK-Net
Coordinates agent workflows and manages multi-agent reasoning loops.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..agents.base_agent import BaseAgent
from ..agents.memory_agent import MemoryAgent
from ..memory.memory_store import MemoryStore


class OrchestrationManager:
    """Manages multi-agent workflows and coordination."""

    def __init__(self, memory_store: Optional[MemoryStore] = None):
        self.memory_store = memory_store or MemoryStore()
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestration manager."""
        self.agents[agent.name] = agent
        print(f"Registered agent: {agent.name}")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)

    async def execute_workflow(
        self, workflow_name: str, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a predefined workflow."""
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"error": f"Workflow '{workflow_name}' not found"}

        # Execute workflow steps
        results = {}
        for step_name, step_config in workflow.get("steps", []):
            agent_name = step_config.get("agent")
            task_config = step_config.get("task", {})

            if agent_name in self.agents:
                agent = self.agents[agent_name]
                result = await agent.handle(task_config)
                results[step_name] = result

        # Store workflow results
        workflow_result = {
            "workflow": workflow_name,
            "inputs": inputs,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Save to memory
        workflow_id = f"workflow_{workflow_name}_{datetime.utcnow().timestamp()}"
        await self.memory_store.store(workflow_id, workflow_result)

        return workflow_result

    async def coordinate_debate(
        self,
        participants: List[str],
        initial_claims: List[Dict[str, Any]],
        rounds: int = 3,
    ) -> Dict[str, Any]:
        """Coordinate a debate between multiple agents."""
        debate_history = []

        for round_num in range(1, rounds + 1):
            round_data = {
                "round": round_num,
                "participants": participants,
                "claims": initial_claims if round_num == 1 else [],
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Collect responses from participants
            responses = []
            for participant in participants:
                if participant in self.agents:
                    agent = self.agents[participant]
                    # Simple response collection (in real implementation, would pass specific tasks)
                    responses.append(
                        {
                            "agent": participant,
                            "response": f"Response from {participant} in round {round_num}",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

            round_data["responses"] = responses
            debate_history.append(round_data)

        return {
            "status": "completed",
            "debate_history": debate_history,
            "total_rounds": rounds,
        }

    async def evaluate_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """Evaluate an agent's performance based on trust score and activity."""
        if agent_name not in self.agents:
            return {"error": f"Agent '{agent_name}' not found"}

        agent = self.agents[agent_name]
        return {
            "agent": agent_name,
            "trust_score": agent.trust_score,
            "type": type(agent).__name__,
        }

    def create_workflow_template(self, name: str, steps: List[Dict[str, Any]]):
        """Create a reusable workflow template."""
        self.workflows[name] = {
            "name": name,
            "steps": steps,
            "created_at": datetime.utcnow().isoformat(),
        }
        print(f"Created workflow template: {name}")

    async def run_parallel_tasks(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Run multiple tasks in parallel."""
        coroutines = []
        for task in tasks:
            agent_name = task.get("agent")
            task_config = task.get("task", {})

            if agent_name and agent_name in self.agents:
                agent = self.agents[agent_name]
                coroutines.append(agent.handle(task_config))

        results = await asyncio.gather(*coroutines, return_exceptions=True)
        return results
