"""
Youth Employment Policy Simulator - Streamlit Web Interface

Interactive tool for exploring the effects of policy interventions on youth employment.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.simulation import SimulationEngine
from src.llm import LLMClient

# Page configuration
st.set_page_config(
    page_title="Youth Employment Policy Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LinkedIn URL
LINKEDIN_URL = "https://www.linkedin.com/in/marti-taru-38358320/"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .contact-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎓 Youth Employment Policy Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Explore how counseling services and wage subsidies impact NEET employment outcomes</div>', unsafe_allow_html=True)

# Introduction
with st.expander("ℹ️ About This Simulation", expanded=False):
    st.markdown("""
    This interactive tool simulates the effects of social policy interventions on youth employment.

    **What it models:**
    - **NEETs** (Not in Education, Employment, or Training) seeking employment
    - **Businesses** that can hire youth as apprentices
    - **Counseling Services** that reduce barriers and increase motivation
    - **Wage Subsidies** that incentivize business hiring

    **How it works:**
    1. Adjust the policy parameters below
    2. Click "Run Simulation"
    3. Explore the results and outcomes

    **Note:** This is a simplified demonstration model. For realistic policy analysis
    tailored to your specific context, please contact me for a consultation.
    """)

# Sidebar - Configuration
st.sidebar.header("📋 Configure Your Policy Scenario")

st.sidebar.markdown("---")
st.sidebar.subheader("Population")

num_neets = st.sidebar.slider(
    "Number of NEETs",
    min_value=10,
    max_value=100,
    value=20,
    step=5,
    help="Youth not in employment, education, or training"
)

num_businesses = st.sidebar.slider(
    "Number of Businesses",
    min_value=5,
    max_value=50,
    value=10,
    step=5,
    help="Employers who can hire apprentices"
)

st.sidebar.markdown("---")
st.sidebar.subheader("💬 Counseling Services")

counseling_budget = st.sidebar.slider(
    "Monthly Budget (€)",
    min_value=10000,
    max_value=150000,
    value=50000,
    step=10000,
    help="Funds available for counseling services per month"
)

counseling_intensity = st.sidebar.slider(
    "Intensity",
    min_value=0.05,
    max_value=0.30,
    value=0.12,
    step=0.01,
    help="How effectively counseling reduces barriers (0-1)"
)

st.sidebar.markdown(f"""
<div style="background-color: #f0f2f6; padding: 0.5rem; border-radius: 0.25rem; font-size: 0.85rem;">
💡 At €{counseling_budget:,}/month, approximately {counseling_budget // 500} NEETs can receive services
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Wage Subsidies")

subsidy_enabled = st.sidebar.checkbox(
    "Enable Wage Subsidy Program",
    value=True,
    help="Subsidies incentivize businesses to hire NEETs"
)

subsidy_effectiveness = st.sidebar.slider(
    "Subsidy Effectiveness",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1,
    help="How much subsidies increase hiring probability (0-1)",
    disabled=not subsidy_enabled
)

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Simulation Settings")

duration_months = st.sidebar.slider(
    "Duration (months)",
    min_value=6,
    max_value=24,
    value=12,
    step=3,
    help="Length of simulation period"
)

random_seed = st.sidebar.number_input(
    "Random Seed (for reproducibility)",
    min_value=0,
    max_value=9999,
    value=42,
    help="Same seed = same results"
)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Your Policy Configuration")

    config_summary = f"""
    - **Population:** {num_neets} NEETs, {num_businesses} businesses
    - **Counseling:** €{counseling_budget:,}/month at {counseling_intensity:.0%} intensity
    - **Subsidies:** {"✅ Enabled" if subsidy_enabled else "❌ Disabled"} {f"({subsidy_effectiveness:.0%} effectiveness)" if subsidy_enabled else ""}
    - **Duration:** {duration_months} months
    """
    st.markdown(config_summary)

with col2:
    st.markdown("### Quick Scenarios")
    scenario = st.selectbox(
        "Load preset scenario",
        ["Custom", "Minimal Intervention", "High Investment", "Subsidy Focus", "Counseling Focus"]
    )

    if scenario == "Minimal Intervention":
        st.info("Low budget, low subsidies")
    elif scenario == "High Investment":
        st.info("Maximum investment in both")
    elif scenario == "Subsidy Focus":
        st.info("Low counseling, high subsidies")
    elif scenario == "Counseling Focus":
        st.info("High counseling, low subsidies")

# Apply scenario presets
if scenario == "Minimal Intervention":
    counseling_budget = 30000
    counseling_intensity = 0.10
    subsidy_enabled = True
    subsidy_effectiveness = 0.3
elif scenario == "High Investment":
    counseling_budget = 100000
    counseling_intensity = 0.15
    subsidy_enabled = True
    subsidy_effectiveness = 0.8
elif scenario == "Subsidy Focus":
    counseling_budget = 30000
    counseling_intensity = 0.10
    subsidy_enabled = True
    subsidy_effectiveness = 0.8
elif scenario == "Counseling Focus":
    counseling_budget = 100000
    counseling_intensity = 0.15
    subsidy_enabled = True
    subsidy_effectiveness = 0.3

# Run simulation button
st.markdown("---")
run_button = st.button("▶️ Run Simulation", type="primary", use_container_width=True)

if run_button:
    with st.spinner('🔄 Running simulation... This will take 5-10 seconds.'):
        try:
            # Create simulation
            llm_client = LLMClient(provider='mock')  # Always use mock for speed

            sim = SimulationEngine(
                num_neets=num_neets,
                num_businesses=num_businesses,
                duration_months=duration_months,
                random_seed=random_seed,
                use_llm_profiles=True,
                llm_client=llm_client,
                config={
                    'counseling_budget': counseling_budget,
                    'counseling_intensity': counseling_intensity,
                    'subsidy_available': subsidy_enabled,
                    'subsidy_effectiveness': subsidy_effectiveness if subsidy_enabled else 0.0,
                    'skill_threshold': 0.4,
                    'transportation_floor': 0.6,
                    'min_business_willingness': 0.5,
                    'max_attempts_per_neet': 3,
                    'region_size': 50,
                }
            )

            # Run simulation
            monthly_metrics = sim.run()
            final_report = sim.get_final_report()

            # Store in session state
            st.session_state['monthly_metrics'] = monthly_metrics
            st.session_state['final_report'] = final_report
            st.session_state['simulation_run'] = True

            st.success('✅ Simulation complete!')

        except Exception as e:
            st.error(f"❌ Error running simulation: {str(e)}")
            st.session_state['simulation_run'] = False

# Display results if simulation has been run
if st.session_state.get('simulation_run', False):
    st.markdown("---")
    st.markdown("## 📊 Results")

    monthly_metrics = st.session_state['monthly_metrics']
    final_report = st.session_state['final_report']

    # Convert to DataFrame
    df = pd.DataFrame(monthly_metrics)

    # Key metrics
    st.markdown("### 📈 Final Outcomes")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Employment Rate",
            f"{final_report['final_employment_rate']:.0%}",
            delta=f"{final_report['final_employment_rate']:.0%} of NEETs employed"
        )

    with col2:
        st.metric(
            "Total Placements",
            final_report['total_placements'],
            delta=f"out of {final_report['num_neets']} NEETs"
        )

    with col3:
        st.metric(
            "Success Rate",
            f"{final_report['overall_success_rate']:.1%}",
            delta="of applications succeeded"
        )

    with col4:
        st.metric(
            "Skill Improvement",
            f"+{final_report['avg_skill_change']:.2f}",
            delta="average increase"
        )

    # Charts
    st.markdown("### 📉 Employment Trend Over Time")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['month'], df['employment_rate'] * 100, marker='o', linewidth=2, markersize=6, color='#1f77b4')
    ax.fill_between(df['month'], 0, df['employment_rate'] * 100, alpha=0.3, color='#1f77b4')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Employment Rate (%)', fontsize=12)
    ax.set_title('Employment Rate Evolution', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)
    st.pyplot(fig)

    # Monthly placements
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Monthly Placements")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df['month'], df['placements_this_month'], color='#2ca02c', alpha=0.7)
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('New Hires', fontsize=10)
        ax.set_title('New Placements Per Month', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)

    with col2:
        st.markdown("### 📊 Attribute Evolution")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['month'], df['avg_skill_level'], label='Skill Level', marker='o')
        ax.plot(df['month'], df['avg_willingness'], label='Willingness', marker='s')
        ax.plot(df['month'], df['avg_impeding_factors'], label='Barriers', marker='^')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Average Value (0-1)', fontsize=10)
        ax.set_title('NEET Attributes Over Time', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    # Interpretation
    st.markdown("### 💡 Interpretation")

    # Generate interpretation based on results
    emp_rate = final_report['final_employment_rate']
    total_placements = final_report['total_placements']

    if emp_rate >= 0.7:
        outcome = "highly effective"
        color = "green"
    elif emp_rate >= 0.5:
        outcome = "moderately effective"
        color = "blue"
    elif emp_rate >= 0.3:
        outcome = "somewhat effective"
        color = "orange"
    else:
        outcome = "limited effectiveness"
        color = "red"

    interpretation = f"""
    With a counseling budget of **€{counseling_budget:,}/month** and
    {"**enabled**" if subsidy_enabled else "**disabled**"} wage subsidies
    {f"at **{subsidy_effectiveness:.0%} effectiveness**" if subsidy_enabled else ""},
    the intervention achieved **{emp_rate:.0%} employment rate** after {duration_months} months.

    This represents **{total_placements} successful placements** out of {final_report['num_neets']} NEETs,
    indicating **{outcome}** policy intervention.

    **Key Insights:**
    - NEETs' average skill level improved by **{final_report['avg_skill_change']:.2f}** points
    - Barriers decreased by **{abs(final_report['avg_impeding_factors_change']):.2f}** points
    - Willingness to work increased by **{final_report['avg_willingness_change']:.2f}** points
    """

    st.markdown(f":{color}[{interpretation}]")

    # Download data
    st.markdown("### 💾 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Monthly Data (CSV)",
            data=csv,
            file_name=f"simulation_results_{random_seed}.csv",
            mime="text/csv"
        )

    with col2:
        import json
        json_str = json.dumps(final_report, indent=2)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json_str,
            file_name=f"simulation_report_{random_seed}.json",
            mime="application/json"
        )

# Contact section
st.markdown("---")
st.markdown("""
<div class="contact-box">
    <h2 style="margin-top: 0;">🤝 Interested in Realistic Policy Analysis?</h2>
    <p style="font-size: 1.1rem;">
        This is a simplified demonstration model. For comprehensive policy analysis
        tailored to your specific context, jurisdiction, and population characteristics,
        let's connect!
    </p>
    <p style="font-size: 0.95rem; opacity: 0.9;">
        I specialize in agent-based modeling for social policy evaluation, including:
        <br>• Custom calibration to your regional data
        <br>• Integration of multiple policy interventions
        <br>• Cost-effectiveness analysis
        <br>• Scenario planning and sensitivity analysis
    </p>
</div>
""", unsafe_allow_html=True)

# LinkedIn contact button
st.markdown(f"""
<div style="text-align: center; margin: 2rem 0;">
    <a href="{LINKEDIN_URL}" target="_blank" style="text-decoration: none;">
        <button style="
            background-color: #0077b5;
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            padding: 1rem 2rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            💼 Contact Me on LinkedIn
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    <p>Built with Python, Streamlit, and Agent-Based Modeling</p>
    <p>© 2024 | Youth Employment Policy Simulator</p>
</div>
""", unsafe_allow_html=True)
