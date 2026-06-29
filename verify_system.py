import sys
from data_manager import generate_synthetic_data, preprocess_data
from predictor import DemandPredictor
from optimizer import SmartGridOptimizer
from agent import GridDecisionAgent

def run_verification():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== Step 2 & 3: Generating and Processing Smart Grid Telemetry ===")
    raw_df = generate_synthetic_data(days=14)
    df = preprocess_data(raw_df)
    print(f"Dataset ready. Total processed records: {len(df)}")

    print("\n=== Step 4: Training ML Demand Forecasting Model ===")
    predictor = DemandPredictor()
    metrics = predictor.train(df)
    print(f"Model Trained. Validation Metrics: MAE={metrics['MAE']:.2f}, R2={metrics['R2']:.3f}")

    print("\n=== Step 5 & 6: Running Optimization Logic & AI Decision Agent ===")
    optimizer = SmartGridOptimizer()
    agent = GridDecisionAgent(optimizer)

    # Test with current simulation state
    row = df.iloc[-1]
    predicted_demand = predictor.predict_next_hour(row)
    current_demand = float(row['energy_demand'])
    renewable_supply = float(row['solar_output'] + row['wind_output'])
    cost_per_unit = float(row['cost_per_unit'])
    is_peak = bool(row['is_peak'])

    agent_output = agent.process_grid_state(
        current_demand=current_demand,
        predicted_demand=predicted_demand,
        renewable_supply=renewable_supply,
        cost_per_unit=cost_per_unit,
        is_peak=is_peak
    )

    print("\n=== Step 8: Final Output Verification ===")
    formatted_output = agent.format_text_output(agent_output)
    print(formatted_output)
    print("\n=== System Verification Complete Successfully! ===")

if __name__ == '__main__':
    run_verification()
