import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import sys
import os

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))
asknet_dir = os.path.dirname(current_dir)

# Add to Python path
if asknet_dir not in sys.path:
    sys.path.insert(0, asknet_dir)

from memory.memory_store import MemoryStore
from vector_store.interface import VectorStore
from ml.embeddings.embedder import Embedder
from agents.data_agent import DataAgent
from agents.prediction_agent import PredictionAgent
from agents.research_agent import ResearchAgent
from agents.critic_agent import CriticAgent
from agents.debate_coordinator import DebateCoordinator
from agents.synthesizer_agent import SynthesizerAgent
from agents.memory_agent import MemoryAgent
from agents.spawner import TaskPlannerAgent, DomainSpawner
from orchestration.manager import OrchestrationManager
from learning.trust_scorer import TrustScorer, LearningCoordinator
from config.settings import settings
from .schemas import QueryRequest, QueryResponse, TaskStatus, FeedbackRequest

app = FastAPI(title="ASK-Net API", version="0.1.0")

# Global state
memory_store = MemoryStore()
embedder = Embedder()
vector_store = VectorStore(dimension=settings.VECTOR_STORE_DIMENSION)

# Initialize agents
research_agent = ResearchAgent(vector_store, embedder)

# Try multiple possible paths for the dataset
dataset_candidates = [
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data/datasets/climate_sample.csv",
    ),
    "/app/ASKNet/data/datasets/climate_sample.csv",
    os.path.join(os.getcwd(), "ASKNet/data/datasets/climate_sample.csv"),
    settings.CLIMATE_DATA_PATH,
]
dataset_path = None
for candidate in dataset_candidates:
    if os.path.exists(candidate):
        dataset_path = candidate
        break

data_agent = DataAgent(dataset_path=dataset_path)
prediction_agent = PredictionAgent(data_agent)
critic_agent = CriticAgent()
debate_coordinator = DebateCoordinator(max_rounds=settings.DEBATE_MAX_ROUNDS)
synthesizer_agent = SynthesizerAgent()
memory_agent = MemoryAgent(memory_store)
spawner = DomainSpawner()
planner_agent = TaskPlannerAgent(spawner)

# Initialize orchestration and learning systems
orchestration_manager = OrchestrationManager(memory_store)
trust_scorer = TrustScorer(
    decay_rate=settings.TRUST_DECAY_RATE, update_factor=settings.TRUST_UPDATE_FACTOR
)
learning_coordinator = LearningCoordinator(trust_scorer)

# Register agents with orchestration
orchestration_manager.register_agent(research_agent)
orchestration_manager.register_agent(data_agent)
orchestration_manager.register_agent(prediction_agent)
orchestration_manager.register_agent(critic_agent)
orchestration_manager.register_agent(debate_coordinator)
orchestration_manager.register_agent(synthesizer_agent)
orchestration_manager.register_agent(memory_agent)

# Task storage (in-memory for MVP)
tasks: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    # Seed the vector store with some basic climate knowledge
    climate_docs = [
        "Climate change is causing increased temperatures and drought in many regions.",
        "Wildfire risk increases with higher temperatures and drought conditions.",
        "Drought index above 0.8 indicates severe drought conditions.",
        "Temperature anomalies above 1.0C can significantly increase wildfire risk.",
        "Wildfire risk is influenced by vegetation type, topography, and weather patterns.",
    ]

    if embedder:
        embeddings = embedder.encode(climate_docs)
        vector_store.add_documents(climate_docs, embeddings)


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle a user query through the multi-agent system."""
    task_id = str(uuid.uuid4())

    # Store initial task
    tasks[task_id] = {
        "task_id": task_id,
        "user_id": request.user_id,
        "query_text": request.query_text,
        "status": "planning",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "constraints": request.constraints or {},
    }

    # Process in background
    asyncio.create_task(process_query(task_id, request))

    return QueryResponse(
        task_id=task_id, status="planning", timestamp=datetime.utcnow()
    )


async def process_query(task_id: str, request: QueryRequest):
    """Process a query through the multi-agent pipeline."""
    try:
        # Step 1: Task Planning
        tasks[task_id]["status"] = "planning"
        tasks[task_id]["updated_at"] = datetime.utcnow()

        plan_result = await planner_agent.handle(
            {"query": request.query_text, "user_id": request.user_id}
        )

        tasks[task_id]["plan"] = plan_result
        tasks[task_id]["domain"] = plan_result.get("domain")
        tasks[task_id]["assignments"] = plan_result.get("assignments", [])

        # Step 2: Execute subtasks
        tasks[task_id]["status"] = "executing"
        tasks[task_id]["updated_at"] = datetime.utcnow()

        agent_outputs = []

        # Research agent task
        research_task = {
            "query": request.query_text,
            "sources": ["climate_data", "public_docs"],
            "k": 3,
        }
        research_result = await research_agent.handle(research_task)
        agent_outputs.append(
            {
                "agent": "ResearchAgent",
                "content": str(research_result),
                "confidence": 0.7,
            }
        )

        # Data agent task
        data_task = {"operation": "load"}
        data_result = await data_agent.handle(data_task)
        agent_outputs.append(
            {
                "agent": "DataAgent",
                "content": f"Loaded climate data with {data_result.get('shape', [0])[0]} rows",
                "confidence": 0.8,
            }
        )

        # Prediction agent task
        prediction_task = {"operation": "train"}
        prediction_result = await prediction_agent.handle(prediction_task)
        agent_outputs.append(
            {
                "agent": "PredictionAgent",
                "content": f"Model trained with evaluation: {prediction_result.get('evaluation', {})}",
                "confidence": 0.75,
            }
        )

        # Make a specific prediction
        specific_pred = await prediction_agent.predict(
            {"drought_index": 0.85, "temp_anomaly": 1.2}
        )
        agent_outputs.append(
            {
                "agent": "PredictionAgent",
                "content": specific_pred.get("wildfire_risk_prediction", 0),
                "confidence": specific_pred.get("confidence", 0.75),
            }
        )

        # Step 3: Debate coordination
        tasks[task_id]["status"] = "debating"
        tasks[task_id]["updated_at"] = datetime.utcnow()

        debate_task = {
            "participants": ["ResearchAgent", "PredictionAgent", "CriticAgent"],
            "initial_claims": agent_outputs,
            "context": {"query": request.query_text},
        }
        debate_result = await debate_coordinator.handle(debate_task)
        tasks[task_id]["debate_history"] = debate_result.get("debate_history", [])

        # Step 4: Critic evaluation
        tasks[task_id]["status"] = "critiquing"
        tasks[task_id]["updated_at"] = datetime.utcnow()

        critique_task = {
            "claims": agent_outputs,
            "context": {"query": request.query_text},
        }
        critique_result = await critic_agent.handle(critique_task)

        # Step 5: Synthesis
        tasks[task_id]["status"] = "synthesizing"
        tasks[task_id]["updated_at"] = datetime.utcnow()

        synthesis_task = {
            "agent_outputs": agent_outputs,
            "critique_results": critique_result,
            "context": {"query": request.query_text},
        }
        synthesis_result = await synthesizer_agent.handle(synthesis_task)

        # Store final result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["updated_at"] = datetime.utcnow()
        tasks[task_id]["final_answer"] = synthesis_result.get("final_answer")
        tasks[task_id]["synthesis"] = synthesis_result

        # Step 6: Store in memory
        await memory_agent.store_interaction(
            task_id,
            {
                "task_id": task_id,
                "query": request.query_text,
                "agent_outputs": agent_outputs,
                "debate": debate_result,
                "critique": critique_result,
                "synthesis": synthesis_result,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["updated_at"] = datetime.utcnow()


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return TaskStatus(
        task_id=task["task_id"],
        status=task["status"],
        query_text=task["query_text"],
        domain=task.get("domain"),
        assignments=task.get("assignments", []),
        final_answer=task.get("final_answer"),
        debate_history=task.get("debate_history"),
        created_at=task["created_at"],
        updated_at=task["updated_at"],
    )


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a task."""
    if request.task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store feedback
    await memory_agent.store_feedback(
        request.task_id, request.rating, request.comments or ""
    )

    # Update trust scores (simple reward/penalty based on rating)
    rating = request.rating
    if rating >= 4:
        reward = 0.1
    elif rating >= 3:
        reward = 0.05
    elif rating >= 2:
        reward = -0.05
    else:
        reward = -0.1

    # Update trust for all agents involved in the task
    agents_to_update = [
        "ResearchAgent",
        "DataAgent",
        "PredictionAgent",
        "CriticAgent",
        "SynthesizerAgent",
    ]
    for agent_name in agents_to_update:
        # This is a simplified version - in reality, each agent would have its own trust score
        pass

    return {"status": "feedback_received", "rating": rating}


@app.get("/memory/{agent_name}")
async def get_memory(agent_name: str):
    """Get memory context for an agent."""
    prefix = f"interaction_"
    interactions = await memory_store.search(prefix)
    return {
        "agent": agent_name,
        "interactions": len(interactions),
        "preview": list(interactions.items())[:5] if interactions else [],
    }


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "ASK-Net Multi-Agent System",
        "version": "0.1.0",
        "agents": [
            "TaskPlanner",
            "Research",
            "Data",
            "Prediction",
            "Critic",
            "Debate",
            "Synthesizer",
            "Memory",
        ],
        "features": [
            "multi_agent",
            "debate",
            "learning",
            "trust_scoring",
            "domain_spawning",
        ],
    }


@app.get("/agents")
async def list_agents():
    """List all registered agents and their trust scores."""
    agent_info = []
    for agent_name, agent in orchestration_manager.agents.items():
        trust_score = trust_scorer.get_score(agent_name)
        agent_info.append(
            {
                "name": agent_name,
                "type": type(agent).__name__,
                "trust_score": trust_score,
            }
        )

    return {"agents": agent_info, "total": len(agent_info)}


@app.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get detailed information about an agent."""
    if agent_name not in orchestration_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = orchestration_manager.agents[agent_name]
    trust_score = trust_scorer.get_score(agent_name)
    history = trust_scorer.get_agent_history(agent_name)

    return {
        "name": agent_name,
        "type": type(agent).__name__,
        "trust_score": trust_score,
        "history_length": len(history),
        "recent_history": history[-5:] if history else [],
    }


@app.get("/learning/analytics")
async def get_learning_analytics():
    """Get learning analytics and recommendations."""
    analysis = learning_coordinator.analyze_patterns()
    recommendations = learning_coordinator.get_recommendations()
    top_agents = trust_scorer.get_top_agents(limit=5)

    return {
        "analytics": analysis,
        "recommendations": recommendations,
        "top_agents": top_agents,
    }


@app.post("/orchestrate/workflow")
async def run_workflow(workflow_config: Dict[str, Any]):
    """Run a predefined workflow using orchestration manager."""
    workflow_name = workflow_config.get("name", "climate_analysis")
    inputs = workflow_config.get("inputs", {})

    # Create workflow template if not exists
    if workflow_name not in orchestration_manager.workflows:
        orchestration_manager.create_workflow_template(
            workflow_name, workflow_config.get("steps", [])
        )

    result = await orchestration_manager.execute_workflow(workflow_name, inputs)
    return result


@app.get("/tasks")
async def list_tasks():
    """List all tasks."""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task.get("status"),
                "query": task.get("query_text")[:100] + "..."
                if len(task.get("query_text", "")) > 100
                else task.get("query_text"),
                "created_at": task.get("created_at"),
            }
            for task_id, task in tasks.items()
        ],
        "total": len(tasks),
    }
