import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_manager import generate_synthetic_data, load_kaggle_dataset, process_custom_dataset, preprocess_data
from predictor import DemandPredictor
from optimizer import SmartGridOptimizer
from agent import GridDecisionAgent

# Page Configuration
st.set_page_config(
    page_title="Smart Grid Optimization Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS enforcing strict high contrast: Sleek Dark Backgrounds with Crisp White Fonts
st.markdown("""
<style>
    /* Main Background & Text Color */
    .stApp {
        background-color: #080c14;
        color: #ffffff !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div, li {
        color: #ffffff !important;
    }

    /* Sidebar Top Collapse/Expand Arrow Icon in Vibrant Red */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarToggle"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"],
    [data-testid="stHeader"] button {
        color: #ff0000 !important;
        fill: #ff0000 !important;
    }
    button[data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="stSidebarToggle"] svg,
    button[aria-label="Close sidebar"] svg,
    button[aria-label="Open sidebar"] svg,
    [data-testid="stHeader"] button svg {
        fill: #ff0000 !important;
        color: #ff0000 !important;
        stroke: #ff0000 !important;
    }
    
    /* Custom Styling for the 5 Interactive Clickable KPI Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #ffffff !important;
        border: 2px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5) !important;
        width: 100% !important;
        white-space: pre-wrap !important;
        min-height: 85px !important;
    }
    div.stButton > button:hover {
        border-color: #38bdf8 !important;
        background: linear-gradient(135deg, #0f172a 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
    }
    div.stButton > button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* AI Decision Agent Box */
    .agent-box {
        background-color: #0f172a;
        padding: 22px;
        border-radius: 12px;
        border-left: 6px solid #38bdf8;
        border: 1px solid #1e293b;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    .agent-text {
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 15px;
        color: #f8fafc !important;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    /* Chat bubbles */
    .chat-bubble-user {
        background-color: #0284c7;
        color: #ffffff !important;
        padding: 12px 18px;
        border-radius: 18px 18px 2px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        font-size: 15px;
    }
    .chat-bubble-agent {
        background-color: #1e293b;
        color: #f8fafc !important;
        padding: 14px 20px;
        border-radius: 18px 18px 18px 2px;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
        border: 1px solid #334155;
        font-size: 15px;
    }
    .chat-container {
        padding: 5px 0px;
        margin-bottom: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "custom_df_raw" not in st.session_state:
    st.session_state.custom_df_raw = None
if "selected_kpi_detail" not in st.session_state:
    st.session_state.selected_kpi_detail = "🔋 Current Demand"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "agent", "text": "👋 Hello! I am your Smart Grid Autonomous AI Assistant. Type any question below to ask me about load demand, solar/wind supply, peak alerts, or cost saving tips!"}
    ]

@st.cache_data
def load_base_data(source_type):
    if source_type == "📊 Kaggle Smart Grid Dataset":
        raw_df = load_kaggle_dataset()
    else:
        raw_df = generate_synthetic_data(days=30)
    return raw_df

# ==========================================
# SIDEBAR NAVIGATION & CONTROLS
# ==========================================
st.sidebar.title("⚡ Smart Grid System")
st.sidebar.markdown("---")

st.sidebar.subheader("📌 Navigation Menu")
nav_page = st.sidebar.radio(
    "Select Session:",
    [
        "⚡ Smart Grid Optimization Dashboard", 
        "🤖 AI Interactive Chat Session", 
        "📂 Custom Dataset Manager", 
        "📈 ML Predictive Analytics"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Data Pipeline Source")
dataset_choice = st.sidebar.radio(
    "Select Pipeline:",
    ["🤖 Synthetic Simulation", "📊 Kaggle Smart Grid Dataset", "📁 Custom CSV Upload"],
    index=0
)

# Load Active Dataframe
if dataset_choice == "📁 Custom CSV Upload" and st.session_state.custom_df_raw is not None:
    raw_df = st.session_state.custom_df_raw
else:
    raw_df = load_base_data(dataset_choice)

# Preprocess and train ML model
df = preprocess_data(raw_df)
predictor = DemandPredictor()
metrics = predictor.train(df)
optimizer = SmartGridOptimizer(baseline_grid_capacity=1000.0)
agent = GridDecisionAgent(optimizer)

# EXPLICIT SIDEBAR CONTROLS FOR TEMPERATURE, SOLAR CAPACITY, AND WIND CAPACITY
st.sidebar.markdown("---")
st.sidebar.header("🎛️ Smart Grid Optimization Controls")
st.sidebar.markdown("Adjust environmental variables to dynamically test grid optimization:")

selected_index = st.sidebar.slider("⏰ Time Index (Hours)", 24, len(df)-1, len(df)-12)
row = df.iloc[selected_index]

temp_override = st.sidebar.slider("🌡️ Temperature (°C)", 10.0, 45.0, float(row['temperature']))
solar_override = st.sidebar.slider("🌞 Solar Capacity (MW)", 0.0, 600.0, float(row['solar_output']))
wind_override = st.sidebar.slider("💨 Wind Capacity (MW)", 0.0, 400.0, float(row['wind_output']))

# Sidebar System Documentation Menu
st.sidebar.markdown("---")
with st.sidebar.expander("ℹ️ Data Source & System Guide"):
    st.markdown("""
    **🌐 Where Data is Collected From:**
    - **🤖 Synthetic Simulation**: Generated in Python modeling 30-day hourly load curves, weather variations, solar/wind farms, and electricity pricing tariffs.
    - **📊 Kaggle Dataset**: Pre-processed real-world smart grid operational dataset (PJM Load & weather metrics).
    - **📁 Custom Upload**: Upload your own CSV file in the **Custom Dataset Manager**!

    **📋 System Architecture:**
    1. Scope Definition & Architecture
    2. Data Collection Engine
    3. Missing Value & Feature Engineering
    4. Random Forest ML Forecast Model
    5. Smart Grid Optimization Logic
    6. Autonomous AI Decision Agent Layer
    7. Real-Time Visual Dashboard
    8. Structured Action Directives & Savings
    """)

sim_features = row.copy()
sim_features['temperature'] = temp_override

predicted_demand = predictor.predict_next_hour(sim_features)
current_demand = float(row['energy_demand'])
renewable_supply = float(solar_override + wind_override)
cost_per_unit = float(row['cost_per_unit'])
is_peak = bool(row['is_peak'])

agent_output = agent.process_grid_state(
    current_demand=current_demand,
    predicted_demand=predicted_demand,
    renewable_supply=renewable_supply,
    cost_per_unit=cost_per_unit,
    is_peak=is_peak
)
agent_output['cost_per_unit'] = cost_per_unit


# Helper function to render Q&A Chat Box
def render_interactive_chat(key_prefix="main"):
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["sender"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-agent">{msg["text"]}</div>', unsafe_allow_html=True)
    st.markdown('<div style="clear:both;"></div></div>', unsafe_allow_html=True)

    with st.form(key=f"chat_form_{key_prefix}", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            user_q = st.text_input("Ask your Smart Grid AI Agent anything...", placeholder="e.g., What is the current demand? How can we save energy?", label_visibility="collapsed")
        with col_btn:
            btn_click = st.form_submit_button("Send Query 🚀")

    if btn_click and user_q.strip():
        st.session_state.chat_history.append({"sender": "user", "text": user_q})
        response_text = agent.answer_question(user_q, agent_output)
        st.session_state.chat_history.append({"sender": "agent", "text": response_text})
        st.rerun()


# ==========================================
# SESSION 1: SMART GRID OPTIMIZATION DASHBOARD
# ==========================================
if nav_page == "⚡ Smart Grid Optimization Dashboard":
    st.title("⚡ Smart Grid Optimization Dashboard")
    st.markdown(f"Real-time grid load balancing & forecast visualization. *(Data Pipeline: **{dataset_choice}**)*")
    st.markdown("---")

    # 5 Sleek Dark Metallic Clickable KPI Boxes
    st.subheader("👆 Interactive Grid KPI Metrics (Click any box for detailed breakdown!)")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        if st.button(f"🔋 Current Demand\n\n{agent_output['current_demand']} MW"):
            st.session_state.selected_kpi_detail = "🔋 Current Demand"
            
    with kpi_col2:
        if st.button(f"⚡ Predicted Demand\n\n{agent_output['predicted_demand']} MW"):
            st.session_state.selected_kpi_detail = "⚡ Predicted Demand"
            
    with kpi_col3:
        if st.button(f"🌞 Renewable Supply\n\n{agent_output['renewable_contribution']} MW"):
            st.session_state.selected_kpi_detail = "🌞 Renewable Supply"
            
    with kpi_col4:
        if st.button(f"⚠️ Peak Alert\n\n{agent_output['peak_alert']}"):
            st.session_state.selected_kpi_detail = "⚠️ Peak Alert"
            
    with kpi_col5:
        if st.button(f"💰 Est. Savings\n\n{agent_output['estimated_savings']}%"):
            st.session_state.selected_kpi_detail = "💰 Est. Savings"

    # Deep-Dive Information Panel for Clicked Box
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"### 🔍 Deep-Dive Breakdown: **{st.session_state.selected_kpi_detail}**")
        selected = st.session_state.selected_kpi_detail
        
        if selected == "🔋 Current Demand":
            st.info(f"💡 **Current Grid Load Details**: Active power consumption is currently **{agent_output['current_demand']} MW**. The baseline substation threshold is rated for 1000 MW capacity.")
        elif selected == "⚡ Predicted Demand":
            diff = round(agent_output['predicted_demand'] - agent_output['current_demand'], 2)
            st.success(f"📈 **ML Demand Forecast Details**: Next-hour forecasted demand is **{agent_output['predicted_demand']} MW** (Net delta: **{diff} MW**). Predicted using Random Forest Regressor models based on temperature spikes and temporal lags.")
        elif selected == "🌞 Renewable Supply":
            pct = round((agent_output['renewable_contribution'] / agent_output['predicted_demand'] * 100), 1) if agent_output['predicted_demand'] > 0 else 0
            st.warning(f"🌱 **Renewable Supply Details**: Solar and wind clean power output is generating **{agent_output['renewable_contribution']} MW**, meeting **{pct}%** of grid demand.")
        elif selected == "⚠️ Peak Alert":
            if agent_output['peak_alert'] == "Yes":
                st.error("🚨 **Peak Alert Details**: Grid load is operating in high-stress peak pricing hours (5 PM - 9 PM) or exceeding capacity reserves. Industrial load shifting directives are enforced.")
            else:
                st.info("✅ **Peak Alert Details**: Grid operations are within normal stability margins. Spinning reserves are adequate.")
        elif selected == "💰 Est. Savings":
            st.success(f"💵 **Estimated Savings Details**: **{agent_output['estimated_savings']}% financial savings** achieved by prioritizing zero-marginal-cost clean renewables and shifting non-essential loads off-peak.")

    st.markdown("---")
    
    # Visual Analytics & AI Directives Split
    g_col1, g_col2 = st.columns([2, 1])
    
    with g_col1:
        st.subheader("📊 Demand Forecasting & Energy Mix (Past 24 Hours)")
        recent_df = df.iloc[max(0, selected_index-24):selected_index+1].copy()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recent_df['timestamp'], y=recent_df['energy_demand'], name='Actual Demand (MW)', line=dict(color='#38bdf8', width=3)))
        fig.add_trace(go.Scatter(x=recent_df['timestamp'], y=recent_df['solar_output'], name='Solar Supply', stackgroup='one', line=dict(color='#facc15', width=0)))
        fig.add_trace(go.Scatter(x=recent_df['timestamp'], y=recent_df['wind_output'], name='Wind Supply', stackgroup='one', line=dict(color='#4ade80', width=0)))
        
        next_timestamp = recent_df['timestamp'].iloc[-1] + pd.Timedelta(hours=1)
        fig.add_trace(go.Scatter(x=[next_timestamp], y=[predicted_demand], name='Next-Hour Forecast', mode='markers+text', text=["Predicted"], textposition="top center", marker=dict(color='#f43f5e', size=13, symbol='star')))

        fig.update_layout(
            template="plotly_dark",
            height=420,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,0.6)',
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color='#ffffff'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with g_col2:
        st.subheader("🤖 AI Agent Directives")
        formatted_text = agent.format_text_output(agent_output)
        st.markdown(f'<div class="agent-box"><div class="agent-text">{formatted_text}</div></div>', unsafe_allow_html=True)

    # DIRECT EMBEDDED LIVE AI INTERACTIVE CHAT SECTION ON MAIN DASHBOARD
    st.markdown("---")
    st.subheader("💬 AI Agent Live Interactive Q&A")
    render_interactive_chat("dash_main")


# ==========================================
# SESSION 2: AI INTERACTIVE CHAT SESSION
# ==========================================
elif nav_page == "🤖 AI Interactive Chat Session":
    st.title("🤖 Autonomous AI Decision Agent Session")
    st.markdown("Have a dedicated conversation with your Smart Grid AI Agent. Ask any questions about real-time load, forecasts, solar/wind performance, or cost saving tips!")
    st.markdown("---")
    render_interactive_chat("full_session")


# ==========================================
# SESSION 3: CUSTOM DATASET MANAGER
# ==========================================
elif nav_page == "📂 Custom Dataset Manager":
    st.title("📂 Custom Smart Grid Dataset Manager")
    st.markdown("Upload your own Smart Grid CSV file to train the ML prediction model and run optimization logic directly on your custom data.")
    st.markdown("---")

    uploaded_file = st.file_uploader("Upload Smart Grid CSV File", type=["csv"])
    
    if uploaded_file is not None:
        try:
            custom_df = process_custom_dataset(uploaded_file)
            st.session_state.custom_df_raw = custom_df
            st.success("✅ Custom CSV Dataset loaded and preprocessed successfully! Select '📁 Custom CSV Upload' in the sidebar to activate it.")
            
            st.subheader("📊 Dataset Summary Statistics")
            st.dataframe(custom_df.describe(), use_container_width=True)
            
            st.subheader("🔍 Dataset Preview (First 20 Rows)")
            st.dataframe(custom_df.head(20), use_container_width=True)
        except Exception as e:
            st.error(f"Error parsing custom dataset: {e}")
    else:
        st.info("ℹ️ Drag and drop any smart grid or energy consumption CSV file above. The system will automatically detect demand, time, temperature, and renewable energy features!")


# ==========================================
# SESSION 4: ML PREDICTIVE ANALYTICS
# ==========================================
elif nav_page == "📈 ML Predictive Analytics":
    st.title("📈 Machine Learning Demand Predictive Analytics")
    st.markdown("Detailed model performance metrics, feature importance rankings, and full dataset inspection.")
    st.markdown("---")

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("🎯 Mean Absolute Error (MAE)", f"{metrics['MAE']:.2f} MW")
    m_col2.metric("📏 Root Mean Sq. Error (RMSE)", f"{metrics['RMSE']:.2f} MW")
    m_col3.metric("📊 Model Accuracy (R² Score)", f"{metrics['R2']:.3f}")

    st.markdown("---")
    st.subheader("🌳 Random Forest Feature Importance Ranking")
    
    if hasattr(predictor.model, 'feature_importances_'):
        importances = predictor.model.feature_importances_
        feature_names = predictor.feature_cols
        fi_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values('Importance', ascending=True)
        
        fig_fi = px.bar(fi_df, x='Importance', y='Feature', orientation='h', title='Feature Contribution to Next-Hour Demand Forecast', color='Importance', color_continuous_scale='Blues')
        fig_fi.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.6)')
        st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Full Active Dataset Inspection")
    st.dataframe(df, use_container_width=True)
