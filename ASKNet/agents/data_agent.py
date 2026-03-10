import os
import pandas as pd
from typing import Any, Dict, Optional

import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
asknet_dir = os.path.dirname(current_dir)
if asknet_dir not in sys.path:
    sys.path.insert(0, asknet_dir)

from agents.base_agent import BaseAgent


class DataAgent(BaseAgent):
    """Data agent for retrieving and preprocessing structured datasets."""

    def __init__(self, dataset_path: Optional[str] = None):
        super().__init__("DataAgent")
        self.dataset_path = dataset_path or os.path.join(
            os.path.dirname(__file__), "../data/datasets/climate_sample.csv"
        )
        self.data = None

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Load and preprocess climate data."""
        operation = task.get("operation", "load")

        if operation == "load":
            return await self.load_data()
        elif operation == "filter":
            return await self.filter_data(task.get("filters", {}))
        elif operation == "stats":
            return await self.get_statistics()
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}

    async def load_data(self) -> Dict[str, Any]:
        """Load climate dataset."""
        try:
            if self.data is None:
                self.data = pd.read_csv(self.dataset_path)
            return {
                "status": "loaded",
                "shape": list(self.data.shape),
                "columns": list(self.data.columns),
                "preview": self.data.head(3).to_dict(orient="records"),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def filter_data(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on conditions."""
        try:
            if self.data is None:
                result = await self.load_data()
                if result["status"] != "loaded":
                    return result

            df = self.data.copy()
            for column, value in filters.items():
                if column in df.columns:
                    df = df[df[column] == value]

            return {
                "status": "filtered",
                "shape": list(df.shape),
                "data": df.to_dict(orient="records")[:10],  # Limit output size
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for the dataset."""
        try:
            if self.data is None:
                await self.load_data()

            stats = {}
            for col in self.data.select_dtypes(include=["number"]).columns:
                stats[col] = {
                    "mean": float(self.data[col].mean()),
                    "std": float(self.data[col].std()),
                    "min": float(self.data[col].min()),
                    "max": float(self.data[col].max()),
                }

            return {"status": "statistics", "stats": stats}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def prepare_features(self) -> Optional[pd.DataFrame]:
        """Prepare features for modeling."""
        try:
            if self.data is None:
                await self.load_data()

            # Use drought_index and temp_anomaly to predict wildfire_risk
            features = self.data[["drought_index", "temp_anomaly"]].copy()
            return features
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return None

    async def get_target(self) -> Optional[pd.Series]:
        """Get target variable for modeling."""
        try:
            if self.data is None:
                await self.load_data()

            return self.data["wildfire_risk"]
        except Exception as e:
            self.logger.error(f"Error getting target: {e}")
            return None
