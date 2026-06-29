class SmartGridOptimizer:
    """
    Step 5: Optimization Logic (load balancing, peak shifting, renewable prioritization).
    """
    def __init__(self, baseline_grid_capacity=1000.0):
        self.grid_capacity = baseline_grid_capacity

    def optimize_distribution(self, current_demand, predicted_demand, renewable_supply, cost_per_unit, is_peak):
        """
        Calculates optimal load allocation, renewable dispatch, load shifting recommendations,
        and projected cost savings.
        """
        total_supply_available = self.grid_capacity + renewable_supply
        net_grid_demand = max(0.0, predicted_demand - renewable_supply)
        
        # Determine if peak stress alert is active
        capacity_usage = predicted_demand / total_supply_available
        is_peak_alert = is_peak or (capacity_usage > 0.82)
        
        load_shifting_mw = 0.0
        actions = []
        
        # Renewable prioritization logic
        renewable_contribution = min(predicted_demand, renewable_supply)
        renewable_percentage = (renewable_contribution / predicted_demand * 100) if predicted_demand > 0 else 0
        
        actions.append("Prioritize max dispatch from solar and wind farms to clean grid.")
        
        # Load balancing and peak mitigation logic
        if is_peak_alert:
            # Shift industrial and non-critical loads by 10-15%
            load_shifting_mw = round(predicted_demand * 0.12, 2)
            actions.append(f"Shift industrial load ({load_shifting_mw} MW) to off-peak hours.")
            actions.append("Reduce non-critical urban municipal lighting and HVAC consumption by 12%.")
            actions.append("Dispatch battery energy storage systems (BESS) to buffer grid ramp rate.")
        else:
            actions.append("Grid operating under nominal stress. Enable standard economic dispatch.")
            actions.append("Charge municipal storage batteries with excess off-peak energy.")

        # Calculate estimated savings
        # Savings come from: avoiding peak tariff penalties + utilizing free renewable energy
        peak_penalty_savings = (load_shifting_mw * cost_per_unit * 0.4) if is_peak_alert else 0
        renewable_savings = renewable_contribution * cost_per_unit * 0.8
        total_baseline_cost = predicted_demand * cost_per_unit * 1.2
        
        estimated_savings_percent = round(((peak_penalty_savings + renewable_savings) / total_baseline_cost) * 100, 1)
        estimated_savings_percent = min(35.0, max(5.0, estimated_savings_percent)) # Bound between reasonable percentages

        return {
            'net_grid_demand': round(net_grid_demand, 2),
            'renewable_contribution': round(renewable_contribution, 2),
            'renewable_percentage': round(renewable_percentage, 1),
            'is_peak_alert': is_peak_alert,
            'load_shifting_mw': load_shifting_mw,
            'recommendations': actions,
            'estimated_savings_percent': estimated_savings_percent
        }
