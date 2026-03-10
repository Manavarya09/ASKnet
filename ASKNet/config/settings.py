"""
Configuration settings for ASK-Net multi-agent system.
"""

import os
from typing import Optional


class Settings:
    """Settings configuration for ASK-Net."""

    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() == "true"

    # Database Settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))

    # Memory Settings
    MEMORY_STORE_PATH: str = os.getenv("MEMORY_STORE_PATH", "memory_store.json")
    MEMORY_MAX_SIZE: int = int(os.getenv("MEMORY_MAX_SIZE", "1000"))

    # Vector Store Settings
    VECTOR_STORE_DIMENSION: int = int(os.getenv("VECTOR_STORE_DIMENSION", "384"))
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "faiss_index.bin")

    # Embedding Settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

    # Agent Settings
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    DEBATE_MAX_ROUNDS: int = int(os.getenv("DEBATE_MAX_ROUNDS", "3"))

    # Trust Scoring Settings
    TRUST_UPDATE_FACTOR: float = float(os.getenv("TRUST_UPDATE_FACTOR", "0.1"))
    TRUST_DECAY_RATE: float = float(os.getenv("TRUST_DECAY_RATE", "0.95"))

    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")

    # Climate Data Settings
    CLIMATE_DATA_PATH: str = os.getenv(
        "CLIMATE_DATA_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data/datasets/climate_sample.csv",
        ),
    )

    @property
    def database_url(self) -> str:
        """Get database URL with fallback for testing."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return "sqlite:///./asknet.db"


# Global settings instance
settings = Settings()
