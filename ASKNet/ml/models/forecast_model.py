import numpy as np
from typing import Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


class ForecastModel:
    """Simple forecasting model using linear regression."""

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_data(
        self, X: np.ndarray, y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training."""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the model on provided data."""
        X_scaled, y_scaled = self.prepare_data(X, y)
        self.model.fit(X_scaled, y_scaled)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on provided data."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> dict:
        """Evaluate model performance."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        y_pred = self.predict(X)
        mse = np.mean((y_pred - y_true) ** 2)
        mae = np.mean(np.abs(y_pred - y_true))

        return {
            "mse": float(mse),
            "mae": float(mae),
            "r2_score": float(self.model.score(self.scaler.transform(X), y_true)),
        }

    def save_model(self, filepath: str):
        """Save model parameters."""
        import pickle

        params = {
            "model_coef": self.model.coef_,
            "model_intercept": self.model.intercept_,
            "scaler_mean": self.scaler.mean_,
            "scaler_scale": self.scaler.scale_,
            "is_trained": self.is_trained,
        }
        with open(filepath, "wb") as f:
            pickle.dump(params, f)

    def load_model(self, filepath: str):
        """Load model parameters."""
        import pickle

        with open(filepath, "rb") as f:
            params = pickle.load(f)
        self.model.coef_ = params["model_coef"]
        self.model.intercept_ = params["model_intercept"]
        self.scaler.mean_ = params["scaler_mean"]
        self.scaler.scale_ = params["scaler_scale"]
        self.is_trained = params["is_trained"]
