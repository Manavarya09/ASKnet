import pytest
import asyncio
from datetime import datetime
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_store import MemoryStore
from agents.data_agent import DataAgent
from agents.prediction_agent import PredictionAgent
from agents.critic_agent import CriticAgent
from agents.synthesizer_agent import SynthesizerAgent
from agents.memory_agent import MemoryAgent


@pytest.fixture
def memory_store():
    return MemoryStore()


@pytest.fixture
def data_agent():
    return DataAgent()


@pytest.fixture
def prediction_agent(data_agent):
    return PredictionAgent(data_agent)


@pytest.fixture
def critic_agent():
    return CriticAgent()


@pytest.fixture
def synthesizer_agent():
    return SynthesizerAgent()


@pytest.fixture
def memory_agent(memory_store):
    return MemoryAgent(memory_store)


@pytest.mark.asyncio
async def test_data_agent_load(data_agent):
    """Test data agent can load climate data."""
    result = await data_agent.handle({"operation": "load"})
    assert result["status"] == "loaded"
    assert "shape" in result
    assert "columns" in result


@pytest.mark.asyncio
async def test_prediction_agent_train(prediction_agent):
    """Test prediction agent can train model."""
    result = await prediction_agent.handle({"operation": "train"})
    assert result["status"] == "trained"
    assert "evaluation" in result


@pytest.mark.asyncio
async def test_prediction_agent_predict(prediction_agent):
    """Test prediction agent can make predictions."""
    # First train the model
    train_result = await prediction_agent.handle({"operation": "train"})
    assert train_result["status"] == "trained"

    # Then make a prediction
    predict_result = await prediction_agent.handle(
        {
            "operation": "predict",
            "input_data": {"drought_index": 0.85, "temp_anomaly": 1.2},
        }
    )
    assert predict_result["status"] == "predicted"
    assert "wildfire_risk_prediction" in predict_result
    assert "interpretation" in predict_result


@pytest.mark.asyncio
async def test_critic_agent(critic_agent):
    """Test critic agent can evaluate claims."""
    test_claims = [
        {
            "content": "Wildfire risk is 0.75 with high confidence",
            "confidence": 0.8,
            "source": "prediction",
        },
        {
            "content": "Climate change is happening",
            "confidence": 0.9,
            "source": "research",
        },
    ]

    result = await critic_agent.handle(
        {"claims": test_claims, "context": {"query": "test query"}}
    )

    assert result["status"] == "evaluated"
    assert "critiques" in result
    assert "overall_evaluation" in result


@pytest.mark.asyncio
async def test_synthesizer_agent(synthesizer_agent):
    """Test synthesizer agent can create final answer."""
    agent_outputs = [
        {
            "agent": "ResearchAgent",
            "content": "Evidence shows climate impact",
            "confidence": 0.8,
        },
        {
            "agent": "PredictionAgent",
            "content": "Wildfire risk is 0.75",
            "confidence": 0.75,
        },
    ]

    critique_results = {"critiques": []}

    result = await synthesizer_agent.handle(
        {
            "agent_outputs": agent_outputs,
            "critique_results": critique_results,
            "context": {"query": "test query"},
        }
    )

    assert result["status"] == "synthesized"
    assert "final_answer" in result
    assert "citations" in result


@pytest.mark.asyncio
async def test_memory_agent_store_retrieve(memory_agent):
    """Test memory agent can store and retrieve data."""
    test_data = {"test_key": "test_value"}

    # Store
    await memory_agent.handle(
        {"operation": "store", "key": "test_key", "value": test_data}
    )

    # Retrieve
    result = await memory_agent.handle({"operation": "retrieve", "key": "test_key"})

    assert result["status"] == "retrieved"
    assert result["value"] == test_data


@pytest.mark.asyncio
async def test_end_to_end_flow(
    data_agent, prediction_agent, critic_agent, synthesizer_agent
):
    """Test a simplified end-to-end flow."""
    # Load data
    data_result = await data_agent.handle({"operation": "load"})
    assert data_result["status"] == "loaded"

    # Train prediction model
    train_result = await prediction_agent.handle({"operation": "train"})
    assert train_result["status"] == "trained"

    # Make prediction
    predict_result = await prediction_agent.predict(
        {"drought_index": 0.8, "temp_anomaly": 1.0}
    )
    assert predict_result["status"] == "predicted"

    # Create mock agent outputs for synthesis
    agent_outputs = [
        {
            "agent": "DataAgent",
            "content": f"Loaded data with {data_result['shape'][0]} rows",
            "confidence": 0.8,
        },
        {
            "agent": "PredictionAgent",
            "content": f"Wildfire risk: {predict_result['wildfire_risk_prediction']}",
            "confidence": 0.75,
        },
    ]

    # Critique
    critique_result = await critic_agent.handle(
        {"claims": agent_outputs, "context": {"query": "climate analysis"}}
    )

    # Synthesize
    synthesis_result = await synthesizer_agent.handle(
        {
            "agent_outputs": agent_outputs,
            "critique_results": critique_result,
            "context": {"query": "climate analysis"},
        }
    )

    assert synthesis_result["status"] == "synthesized"
    assert "final_answer" in synthesis_result
    assert len(synthesis_result["final_answer"]) > 0
