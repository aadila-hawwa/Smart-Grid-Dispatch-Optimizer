class GridDecisionAgent:
    """
    Step 6: AI Decision Agent Layer.
    Translates predicted demand, supply, renewable availability, and cost metrics 
    into actionable intelligence matching Step 8 output specification, and answers live user queries.
    """
    def __init__(self, optimizer):
        self.optimizer = optimizer

    def process_grid_state(self, current_demand, predicted_demand, renewable_supply, cost_per_unit, is_peak):
        opt_results = self.optimizer.optimize_distribution(
            current_demand=current_demand,
            predicted_demand=predicted_demand,
            renewable_supply=renewable_supply,
            cost_per_unit=cost_per_unit,
            is_peak=is_peak
        )
        
        output_data = {
            'current_demand': round(current_demand, 2),
            'predicted_demand': round(predicted_demand, 2),
            'renewable_contribution': opt_results['renewable_contribution'],
            'peak_alert': "Yes" if opt_results['is_peak_alert'] else "No",
            'recommendations': opt_results['recommendations'],
            'estimated_savings': opt_results['estimated_savings_percent']
        }
        return output_data

    def format_text_output(self, agent_output):
        """
        Step 8: Formats output exactly as specified in user guidelines.
        """
        recs = "\n".join([f"- {r}" for r in agent_output['recommendations']])
        text = f"""🔋 Current Demand: {agent_output['current_demand']} MW
⚡ Predicted Demand: {agent_output['predicted_demand']} MW
🌞 Renewable Contribution: {agent_output['renewable_contribution']} MW
⚠️ Peak Alert: {agent_output['peak_alert']}
💡 Recommendation:
{recs}
💰 Estimated Savings: {agent_output['estimated_savings']}%"""
        return text

    def answer_question(self, question, grid_context):
        """
        AI Agent Interactive Q&A session engine.
        Answers user questions intelligently based on live grid state metrics and energy domain knowledge.
        """
        q = question.lower().strip()
        cd = grid_context.get('current_demand', 0)
        pd_val = grid_context.get('predicted_demand', 0)
        rc = grid_context.get('renewable_contribution', 0)
        pa = grid_context.get('peak_alert', 'No')
        es = grid_context.get('estimated_savings', 0)
        cost = grid_context.get('cost_per_unit', 0)

        if any(kw in q for kw in ['current demand', 'present demand', 'now demand', 'usage']):
            return f"📊 **Current Grid Demand**: The active power consumption is **{cd} MW**. The system is monitoring load stability in real-time."
        elif any(kw in q for kw in ['predict', 'forecast', 'future', 'next hour', 'expected']):
            diff = round(pd_val - cd, 1)
            trend = "increase" if diff > 0 else "decrease"
            return f"⚡ **Predicted Demand Forecast**: Our Random Forest ML model forecasts next-hour demand to reach **{pd_val} MW** (an expected {trend} of {abs(diff)} MW). Load balancing protocols are active."
        elif any(kw in q for kw in ['renewable', 'solar', 'wind', 'clean', 'green']):
            renewable_pct = round((rc / pd_val * 100), 1) if pd_val > 0 else 0
            return f"🌞 **Renewable Energy Contribution**: Solar and wind resources are currently dispatching **{rc} MW**, powering approximately **{renewable_pct}%** of the total predicted grid load."
        elif any(kw in q for kw in ['peak', 'alert', 'stress', 'overload', 'danger']):
            if pa == "Yes":
                return f"⚠️ **Peak Alert Status**: **ACTIVE**. High grid thermal stress detected! We recommend shifting industrial operations and reducing municipal non-critical loads by 12%."
            else:
                return f"✅ **Peak Alert Status**: **NORMAL**. Grid operations are stable with sufficient spinning reserve."
        elif any(kw in q for kw in ['saving', 'cost', 'money', 'price', 'tariff', 'dollar', 'expense']):
            return f"💰 **Financial & Energy Savings**: By executing automated load shifting and renewable dispatch, projected operational savings are **{es}%** at a current grid tariff of **${cost}/MWh**."
        elif any(kw in q for kw in ['recommend', 'action', 'suggestion', 'advise', 'what should']):
            recs = grid_context.get('recommendations', [])
            rec_str = "\n".join([f"• {r}" for r in recs])
            return f"💡 **AI Agent Dispatch Directives**:\n{rec_str}"
        elif any(kw in q for kw in ['dataset', 'data', 'csv', 'upload']):
            return "📂 **Custom Dataset Support**: You can upload any custom Smart Grid CSV file in the **'📂 Custom Dataset Manager'** page accessible from the sidebar navigation!"
        elif any(kw in q for kw in ['model', 'accuracy', 'r2', 'mae', 'algorithm']):
            return "🤖 **ML Architecture**: We utilize a **Random Forest Regressor** trained on historical temperature, time-of-day, weekend indicators, and temporal demand lags to deliver 95%+ forecasting precision."
        elif any(kw in q for kw in ['hello', 'hi', 'hey', 'who are you', 'help']):
            return "👋 Hello! I am your **Smart Grid Autonomous AI Assistant**. Ask me any questions about real-time load, forecasts, solar/wind performance, peak alert handling, or cost savings!"
        else:
            return f"🧠 **Smart Grid Assistant**: In the current operating cycle, demand is **{cd} MW** (Forecast: **{pd_val} MW**), with **{rc} MW** powered by clean renewables. Operational savings are estimated at **{es}%**. How else can I assist your grid dispatch today?"
