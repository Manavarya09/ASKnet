# ASK-Net: Autonomous Self-learning Knowledge Network

A multi-agent self-learning AI system where specialized agents collaborate, query each other, debate answers, and improve over time through feedback and learning.

## Project Overview

ASK-Net implements an AI research team with specialized agents that work together to produce higher-quality outputs than a single model. The system supports agent-to-agent communication, iterative reasoning loops, and self-learning mechanisms.

### Core Features
- **Agent Orchestration**: Task decomposition and assignment
- **Multi-Agent Communication**: Structured message passing between agents
- **Debate Mechanism**: Multi-round reasoning with critique and refinement
- **Self-Learning**: Trust scoring and feedback-based improvements
- **Dynamic Domain Spawning**: Create specialized agents on-demand
- **Persistent Memory**: Long-term memory for learning and recall

## Architecture

```
User Query
    ↓
Task Planner
    ↓
Agent Pool (Research, Data, Prediction, etc.)
    ↓
Debate Layer (multi-round reasoning)
    ↓
Critic Agent (evaluation)
    ↓
Synthesizer Agent (final answer)
    ↓
Memory + Learning System
```

## Agent Roles

1. **Task Planner Agent**: Decomposes queries into subtasks
2. **Research Agent**: Retrieves knowledge using embeddings and vector search
3. **Data Agent**: Handles structured datasets and preprocessing
4. **Prediction Agent**: Runs ML models for forecasting
5. **Debate Coordinator**: Manages multi-round discussions
6. **Critic Agent**: Evaluates logic and identifies inconsistencies
7. **Synthesizer Agent**: Combines outputs into final answer
8. **Memory Agent**: Stores interactions and results for learning

## Tech Stack

- **Backend**: Python + FastAPI
- **Machine Learning**: PyTorch + scikit-learn
- **Embeddings**: SentenceTransformers
- **Vector Store**: FAISS (or in-memory fallback)
- **Memory**: PostgreSQL + file-based store (MVP)
- **Development**: Docker + docker-compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)

### Running with Docker Compose

1. Clone and navigate to the project directory
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000`

### API Endpoints

- **POST /query**: Submit a query
- **GET /tasks/{task_id}**: Get task status and results
- **POST /feedback**: Submit feedback for a task
- **GET /memory/{agent_name}**: Get agent memory context
- **GET /**: Health check

## Example Usage

### Submit a Query
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query_text": "Assess wildfire risk under drought-prone conditions and propose mitigation strategies"
  }'
```

### Get Task Results
```bash
curl http://localhost:8000/tasks/{task_id}
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "{task_id}",
    "rating": 5,
    "comments": "Great analysis!"
  }'
```

## Project Structure

```
ASKNet/
├── api/                          # FastAPI application
│   ├── main.py                  # API endpoints and orchestration
│   └── schemas.py               # Pydantic models
├── agents/                       # Agent implementations
│   ├── base_agent.py            # Base agent class
│   ├── task_planner.py          # Task planning agent
│   ├── research_agent.py        # Knowledge retrieval
│   ├── data_agent.py            # Data handling
│   ├── prediction_agent.py      # ML forecasting
│   ├── critic_agent.py          # Logic evaluation
│   ├── synthesizer_agent.py     # Answer synthesis
│   ├── memory_agent.py          # Memory management
│   ├── debate_coordinator.py    # Debate orchestration
│   └── spawner.py               # Dynamic agent spawning
├── ml/                          # Machine learning components
│   ├── embeddings/
│   │   └── embedder.py          # Text embedding
│   └── models/
│       └── forecast_model.py    # Forecasting model
├── vector_store/                # Vector storage
│   └── interface.py            # FAISS wrapper
├── memory/                      # Memory persistence
│   ├── memory_store.py         # File-based store
│   └── postgres_schema.sql     # PostgreSQL schema
├── data/datasets/               # Sample datasets
│   └── climate_sample.csv      # Climate data
├── tests/                       # Test files
│   └── test_flow.py            # Flow tests
└── utils/
    └── logger.py                # Logging utilities

docker-compose.yml
Dockerfile
requirements.txt
README.md
```

## Self-Learning Mechanisms

### Agent Trust Scoring
- Each agent maintains a dynamic trust score (0-1)
- Updated based on task outcomes and user feedback
- Higher trust scores influence decision-making

### Feedback Loop
- Store: user query, agent outputs, debate logs, final response, user rating
- Use feedback to improve agent routing and performance

### Reinforcement Learning
- Agents learn which reasoning paths are most effective
- Update routing policies based on reward signals
- Optimize task assignment over time

## Development

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run the API: `uvicorn ASKNet.api.main:app --reload`
3. Run tests: `pytest ASKNet/tests/`

### Testing
Run the test suite:
```bash
pytest ASKNet/tests/ -v
```

## Climate Science Focus

This MVP is specialized for climate science analysis with:
- Climate dataset integration
- Wildfire risk forecasting
- Drought and temperature analysis
- Climate evidence retrieval

## Next Steps

- [ ] Add PostgreSQL persistence for memory and logs
- [ ] Implement full trust scoring system
- [ ] Expand dynamic agent spawning capabilities
- [ ] Add more sophisticated reasoning loops
- [ ] Implement web-based UI
- [ ] Add more climate domain specialists

## License

MIT License