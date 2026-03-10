import numpy as np
from typing import Any, Dict, List
from datetime import datetime

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
asknet_dir = os.path.dirname(current_dir)
if asknet_dir not in sys.path:
    sys.path.insert(0, asknet_dir)

from agents.base_agent import BaseAgent
from ml.models.forecast_model import ForecastModel
from agents.data_agent import DataAgent


class PredictionAgent(BaseAgent):
    """Prediction agent for running ML models and generating forecasts."""

    def __init__(self, data_agent: DataAgent):
        super().__init__("PredictionAgent")
        self.data_agent = data_agent
        self.model = ForecastModel()
        self.feature_columns = ["drought_index", "temp_anomaly"]

    async def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Run prediction on provided data or using the data agent."""
        operation = task.get("operation", "predict")

        if operation == "train":
            return await self.train_model()
        elif operation == "predict":
            return await self.predict(task.get("input_data"))
        elif operation == "forecast":
            return await self.forecast_future(task.get("horizon", 1))
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}

    async def train_model(self) -> Dict[str, Any]:
        """Train the model using data from the data agent."""
        try:
            # Get features and target from data agent
            features = await self.data_agent.prepare_features()
            target = await self.data_agent.get_target()

            if features is None or target is None:
                return {
                    "status": "error",
                    "message": "Failed to get features or target from data agent",
                }

            # Convert to numpy arrays
            X = features.values
            y = target.values

            # Train model
            self.model.train(X, y)

            # Evaluate
            eval_results = self.model.evaluate(X, y)

            return {
                "status": "trained",
                "model_type": "linear_regression",
                "feature_columns": self.feature_columns,
                "evaluation": eval_results,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def predict(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a prediction."""
        try:
            if not self.model.is_trained:
                train_result = await self.train_model()
                if train_result["status"] != "trained":
                    return train_result

            if input_data is None:
                # Use default values
                X = np.array(
                    [[0.85, 1.2]]
                )  # Example: drought_index=0.85, temp_anomaly=1.2
            else:
                X = np.array(
                    [
                        [
                            input_data.get("drought_index", 0.8),
                            input_data.get("temp_anomaly", 1.0),
                        ]
                    ]
                )

            prediction = self.model.predict(X)

            return {
                "status": "predicted",
                "input": {
                    "drought_index": float(X[0, 0]),
                    "temp_anomaly": float(X[0, 1]),
                },
                "wildfire_risk_prediction": float(prediction[0]),
                "interpretation": self._interpret_prediction(prediction[0]),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def forecast_future(self, horizon: int = 1) -> Dict[str, Any]:
        """Forecast future values based on trends."""
        try:
            if not self.model.is_trained:
                train_result = await self.train_model()
                if train_result["status"] != "trained":
                    return train_result

            # Simple trend-based forecasting
            # For MVP, we'll assume slight increases in drought and temperature
            # This could be enhanced with time-series models
            current_data = await self.data_agent.load_data()
            if current_data["status"] != "loaded":
                return {"status": "error", "message": "Failed to load current data"}

            # Get latest data point
            df = self.data_agent.data
            if df is None:
                return {"status": "error", "message": "Data not loaded"}
            latest = df.iloc[-1]

            forecasts = []
            for h in range(1, horizon + 1):
                # Simple trend assumption
                drought_trend = latest["drought_index"] + 0.02 * h
                temp_trend = latest["temp_anomaly"] + 0.05 * h

                X = np.array([[drought_trend, temp_trend]])
                risk = self.model.predict(X)[0]

                forecasts.append(
                    {
                        "horizon": h,
                        "drought_index": float(drought_trend),
                        "temp_anomaly": float(temp_trend),
                        "wildfire_risk": float(risk),
                        "interpretation": self._interpret_prediction(risk),
                    }
                )

            return {
                "status": "forecasted",
                "horizon": horizon,
                "forecasts": forecasts,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _interpret_prediction(self, risk: float) -> str:
        """Interpret the wildfire risk prediction."""
        if risk >= 0.8:
            return "Very high wildfire risk"
        elif risk >= 0.6:
            return "High wildfire risk"
        elif risk >= 0.4:
            return "Moderate wildfire risk"
        elif risk >= 0.2:
            return "Low wildfire risk"
        else:
            return "Very low wildfire risk"
