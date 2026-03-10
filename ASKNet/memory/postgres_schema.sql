-- PostgreSQL schema for ASK-Net memory and logging

-- Users table (optional, for multi-user support)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Queries submitted by users
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    query_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Tasks (subtasks) generated from queries
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id),
    task_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    assigned_agent VARCHAR(100),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent outputs and interactions
CREATE TABLE IF NOT EXISTS agent_outputs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    sender VARCHAR(100),
    receiver VARCHAR(100),
    content TEXT,
    confidence FLOAT DEFAULT 0.5,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Debate logs
CREATE TABLE IF NOT EXISTS debates (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    round_number INTEGER,
    messages JSONB NOT NULL,
    outcome VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Final answers
CREATE TABLE IF NOT EXISTS final_answers (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    answer_text TEXT NOT NULL,
    justification TEXT,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory store for agent recall
CREATE TABLE IF NOT EXISTS memory_store (
    id SERIAL PRIMARY KEY,
    agent VARCHAR(100),
    key VARCHAR(255),
    value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent, key)
);

-- Trust scores for agents
CREATE TABLE IF NOT EXISTS trust_scores (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    domain VARCHAR(100),
    score FLOAT DEFAULT 0.5,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_name, domain)
);

-- User feedback
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_query_id ON tasks(query_id);
CREATE INDEX IF NOT EXISTS idx_agent_outputs_task_id ON agent_outputs(task_id);
CREATE INDEX IF NOT EXISTS idx_debates_task_id ON debates(task_id);
CREATE INDEX IF NOT EXISTS idx_final_answers_task_id ON final_answers(task_id);
CREATE INDEX IF NOT EXISTS idx_memory_store_key ON memory_store(key);
CREATE INDEX IF NOT EXISTS idx_trust_scores_agent ON trust_scores(agent_name);