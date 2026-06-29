import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from data_manager import generate_synthetic_data, preprocess_data

class DemandPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.feature_cols = [
            'hour', 'day_of_week', 'is_weekend', 'is_peak',
            'temperature', 'demand_lag_1h', 'demand_lag_24h', 'temp_lag_1h'
        ]
        self.is_trained = False

    def train(self, df):
        """
        Train Random Forest Regressor to predict next-hour energy demand.
        """
        X = df[self.feature_cols]
        y = df['energy_demand']
        
        # Split train/test (80/20 temporal split)
        split_idx = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        y_pred = self.model.predict(X_test)
        metrics = {
            'MAE': mean_absolute_error(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'R2': r2_score(y_test, y_pred)
        }
        return metrics

    def predict_next_hour(self, current_features):
        """
        Predict demand for the given feature set (dict, pd.Series, or DataFrame).
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        
        if isinstance(current_features, dict):
            input_df = pd.DataFrame([current_features])
        elif isinstance(current_features, pd.Series):
            input_df = pd.DataFrame([current_features.to_dict()])
        elif isinstance(current_features, pd.DataFrame):
            input_df = current_features.copy()
        else:
            input_df = pd.DataFrame(current_features)
            
        input_df = input_df[self.feature_cols]
        prediction = self.model.predict(input_df)[0]
        return round(float(prediction), 2)

if __name__ == '__main__':
    raw_df = generate_synthetic_data()
    df = preprocess_data(raw_df)
    predictor = DemandPredictor()
    metrics = predictor.train(df)
    print("Model trained successfully. Test Metrics:", metrics)
