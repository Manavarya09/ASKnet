#!/usr/bin/env python3
"""
Advanced demo script for ASK-Net multi-agent system.

Demonstrates:
1. Multi-agent orchestration
2. Trust scoring and learning
3. Climate science analysis
4. Message broker usage
5. Workflow execution
"""

import asyncio
import sys
import os

# Add ASKNet to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ASKNet"))

from agents.research_agent import ResearchAgent
from agents.data_agent import DataAgent
from agents.prediction_agent import PredictionAgent
from agents.critic_agent import CriticAgent
from agents.synthesizer_agent import SynthesizerAgent
from agents.domain.climate_agent import ClimateScienceAgent
from orchestration.manager import OrchestrationManager
from learning.trust_scorer import TrustScorer
from messaging.broker import MessageBroker, Message


async def demo_orchestration():
    """Demonstrate orchestration capabilities."""
    print("\n" + "=" * 60)
    print("DEMO 1: Orchestration Manager")
    print("=" * 60)

    manager = OrchestrationManager()

    # Create mock agents
    class MockAgent:
        def __init__(self, name):
            self.name = name
            self.trust_score = 0.5

        async def handle(self, task):
            return {
                "agent": self.name,
                "result": f"Processed {task.get('type', 'task')}",
            }

    manager.register_agent(MockAgent("Research"))
    manager.register_agent(MockAgent("Prediction"))
    manager.register_agent(MockAgent("Critic"))

    # Test workflow execution
    workflow_result = await manager.execute_workflow(
        "test_workflow", {"input": "climate analysis"}
    )

    print(f"Workflow executed: {workflow_result.get('status', 'unknown')}")
    print(f"Agents registered: {len(manager.agents)}")


async def demo_trust_scoring():
    """Demonstrate trust scoring system."""
    print("\n" + "=" * 60)
    print("DEMO 2: Trust Scoring System")
    print("=" * 60)

    trust_scorer = TrustScorer()

    # Update trust scores
    trust_scorer.update_score("ResearchAgent", 0.2)  # Good performance
    trust_scorer.update_score("ResearchAgent", 0.15)
    trust_scorer.update_score("PredictionAgent", -0.1)  # Poor performance

    print("Trust Scores:")
    for agent in ["ResearchAgent", "PredictionAgent", "CriticAgent"]:
        score = trust_scorer.get_score(agent)
        print(f"  {agent}: {score:.3f}")

    # Get top agents
    top_agents = trust_scorer.get_top_agents(limit=3)
    print(f"\nTop agents: {[a['agent'] for a in top_agents]}")


async def demo_climate_analysis():
    """Demonstrate climate science agent capabilities."""
    print("\n" + "=" * 60)
    print("DEMO 3: Climate Science Analysis")
    print("=" * 60)

    climate_agent = ClimateScienceAgent()

    # Test climate trends analysis
    task = {
        "type": "analyze_trends",
        "region": "Southwest US",
        "data": {
            "temperature": [1.1, 1.2, 1.3, 1.4, 1.5],
            "precipitation": [0.8, 0.7, 0.6, 0.5, 0.4],
        },
    }

    result = await climate_agent.handle(task)
    print(f"Analysis for {result['region']}:")
    for trend in result.get("trends", []):
        print(
            f"  {trend['type']}: {trend['interpretation']} (confidence: {trend['confidence']})"
        )

    # Test risk assessment
    risk_task = {
        "type": "assess_risk",
        "region": "California",
        "indicators": {
            "temperature_anomaly": 1.6,
            "drought_index": 0.85,
            "wildfire_risk": 0.75,
        },
    }

    risk_result = await climate_agent.handle(risk_task)
    print(f"\nRisk Assessment for {risk_result['region']}:")
    for risk in risk_result.get("risks", []):
        print(f"  {risk['type']} ({risk['level']}): {risk['description']}")


async def demo_message_broker():
    """Demonstrate message broker capabilities."""
    print("\n" + "=" * 60)
    print("DEMO 4: Message Broker")
    print("=" * 60)

    broker = MessageBroker()
    received_messages = []

    # Create a simple handler
    async def message_handler(message):
        received_messages.append(message)
        print(f"  Received: {message.content}")

    # Register handlers
    broker.register_handler("AgentA", message_handler)
    broker.register_handler("AgentB", message_handler)

    # Subscribe to message types
    broker.subscribe("AgentA", "climate_update")
    broker.subscribe("AgentB", "climate_update")

    # Send messages
    msg1 = Message("Broker", "AgentA", "Temperature update: +1.5°C", "climate_update")
    msg2 = Message("Broker", "AgentB", "Drought index: 0.85", "climate_update")

    await broker.send_message(msg1)
    await broker.send_message(msg2)

    # Process one message
    if not broker.message_queue.empty():
        message = await broker.message_queue.get()
        await broker._route_message(message)

    print(f"Messages processed: {len(received_messages)}")


async def demo_data_agent():
    """Demonstrate data agent capabilities."""
    print("\n" + "=" * 60)
    print("DEMO 5: Data Agent")
    print("=" * 60)

    data_agent = DataAgent()

    # Load data
    result = await data_agent.handle({"operation": "load"})
    if result["status"] == "loaded":
        print(
            f"Data loaded: {result['shape'][0]} rows, {len(result['columns'])} columns"
        )
        print(f"Columns: {', '.join(result['columns'])}")

        # Get statistics
        stats_result = await data_agent.handle({"operation": "stats"})
        if stats_result["status"] == "statistics":
            print(f"\nStatistics:")
            for col, stats in stats_result["stats"].items():
                print(
                    f"  {col}: mean={stats['mean']:.3f}, range=[{stats['min']:.3f}, {stats['max']:.3f}]"
                )


async def demo_prediction_agent():
    """Demonstrate prediction agent capabilities."""
    print("\n" + "=" * 60)
    print("DEMO 6: Prediction Agent")
    print("=" * 60)

    data_agent = DataAgent()
    prediction_agent = PredictionAgent(data_agent)

    # Train model
    train_result = await prediction_agent.handle({"operation": "train"})
    if train_result["status"] == "trained":
        print(f"Model trained successfully")
        print(f"Evaluation - MSE: {train_result['evaluation']['mse']:.4f}")
        print(f"R² Score: {train_result['evaluation']['r2_score']:.4f}")

        # Make predictions
        predictions = [
            {"drought_index": 0.7, "temp_anomaly": 1.0},
            {"drought_index": 0.85, "temp_anomaly": 1.2},
            {"drought_index": 0.9, "temp_anomaly": 1.5},
        ]

        print(f"\nPredictions:")
        for pred_input in predictions:
            pred_result = await prediction_agent.predict(pred_input)
            print(
                f"  Drought={pred_input['drought_index']}, Temp={pred_input['temp_anomaly']}: "
                f"Risk={pred_result['wildfire_risk_prediction']:.3f}"
            )


async def main():
    """Run all demos."""
    print("=" * 60)
    print("ASK-Net Multi-Agent System - Advanced Demo")
    print("=" * 60)

    try:
        await demo_orchestration()
        await demo_trust_scoring()
        await demo_climate_analysis()
        await demo_message_broker()
        await demo_data_agent()
        await demo_prediction_agent()

        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Start the API server: docker-compose up")
        print("  2. Submit queries via /query endpoint")
        print("  3. Monitor agent trust scores via /agents endpoint")
        print("  4. Check learning analytics via /learning/analytics")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
