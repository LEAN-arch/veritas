# VERITAS_app.py
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px

from utils.auth import get_user_role, display_compliance_footer
from utils.data_generator import (
    get_program_gantt_data, create_mock_hplc_data, get_qc_error_data,
    create_dose_response_data
)
from utils.plotters import (
    plot_sankey_flow, plot_gantt_chart, plot_levey_jennings, plot_pareto_chart,
    plot_dose_response, plot_inter_assay_comparison, VERTEX_COLORS
)

# --- Page Configuration ---
st.set_page_config(
    page_title="VERITAS Command Center",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Logo and Header ---
st.markdown(f"<h1 style='color: {VERTEX_COLORS['blue']};'>VERITAS Command Center</h1>", unsafe_allow_html=True)
st.markdown("##### The Central Nervous System for Pre-Clinical Data Integrity, QC, and Reporting")

# --- Authentication and Role-Based Access ---
user_role = get_user_role()

# --- Load Data (cached for performance) ---
@st.cache_data
def load_data():
    hplc_data = create_mock_hplc_data(200)
    gantt_data = get_program_gantt_data()
    error_data = get_qc_error_data()
    dose_data = create_dose_response_data()
    return hplc_data, gantt_data, error_data, dose_data

hplc_df, gantt_df, error_df, dose_df = load_data()

st.markdown("---")

# --- Role-Based Tabbed Interface ---
dte_tab, scientist_tab, qc_tab = st.tabs(["🏢 DTE Leadership View", "🔬 Scientist / Study Director View", "📊 QC Analyst View"])

# --- DTE-RPMS Leadership View ---
with dte_tab:
    if user_role not in ['DTE Leadership']:
        st.warning("You are viewing a dashboard outside your primary role.")
    
    st.header("DTE & Program Leadership Dashboard")
    st.markdown("High-level overview of operational efficiency, data quality, program timelines, and system health.")

    with st.expander("ℹ️ How to Use This Dashboard", expanded=False):
        st.info("""
            - **KPIs:** Track the real-time health of the data pipeline.
            - **Data Flow:** Visualize bottlenecks from data ingestion to reporting.
            - **Timelines:** Monitor progress and risk for key drug programs.
            - **System Alerts:** Immediately identify and address critical system or data issues.
        """)
    
    # KPI Scorecard
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Overall Data Quality Score (DQS)", "97.1%", "0.8%", help="A composite score reflecting the percentage of data points passing all automated QC checks. Higher is better.")
    kpi2.metric("First Pass Yield (FPY)", "88.2%", "-1.5%", help="The percentage of data packages that pass all QC checks on the first attempt without manual intervention. A key measure of process efficiency.")
    kpi3.metric("Avg. Report Cycle Time", "2.9 Hours", "5% improvement", help="Average time from report request to final e-signed approval. Lower is better.")
    kpi4.metric("Cost of Poor Quality (COPQ)", "$1,250", "-$200 vs last week", delta_color="inverse", help="Estimated cost of rework, delays, and investigations due to data errors. Lower is better.")

    st.markdown("---")
    
    col1, col2 = st.columns((5, 5))
    with col1:
        st.plotly_chart(plot_sankey_flow(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_gantt_chart(gantt_df), use_container_width=True)

    st.markdown("---")
    st.subheader("⚠️ Active System & Data Alerts")
    alert_df = pd.DataFrame([
        {"Timestamp": "2024-05-20 09:15", "Priority": "High", "Alert": "Instrument HPLC-03 shows significant drift in retention time.", "Owner": "QC Analyst", "Status": "Investigating"},
        {"Timestamp": "2024-05-20 08:30", "Priority": "Medium", "Alert": "Ingestion latency > 10 mins for LIMS endpoint.", "Owner": "DTE Ops", "Status": "Monitoring"},
        {"Timestamp": "2024-05-19 17:00", "Priority": "Low", "Alert": "VX-121 data package has 3 documents pending signature > 48 hours.", "Owner": "S. Director", "Status": "Open"},
    ])
    st.dataframe(alert_df, use_container_width=True)

# --- Scientist / Study Director View ---
with scientist_tab:
    if user_role not in ['Scientist', 'Study Director']:
        st.warning("You are viewing a dashboard outside your primary role.")
    
    st.header("Scientist & Study Director Dashboard")
    study_id = st.selectbox("Select Your Study to Analyze", options=hplc_df['study_id'].unique())
    study_data = hplc_df[hplc_df['study_id'] == study_id]
    
    with st.expander("ℹ️ How to Use This Dashboard", expanded=False):
        st.info("""
            - **Study KPIs:** Get an at-a-glance summary of your selected study's data status.
            - **Inter-Assay Comparison:** Check for batch-to-batch or study-to-study variability, a key factor in data integrity.
            - **Dose-Response Curve:** A fundamental plot for pre-clinical research to determine compound potency.
            - **My Tasks:** A direct link to data discrepancies or reports requiring your attention.
        """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Samples in Study", len(study_data))
    col2.metric("Data Quality Score (DQS)", f"{np.random.uniform(95, 99.9):.1f}%")
    col3.metric("Discrepancies Requiring Action", study_data.isnull().sum().sum())

    st.markdown("---")
    
    plot_col1, plot_col2 = st.columns(2)
    with plot_col1:
        st.plotly_chart(plot_inter_assay_comparison(hplc_df), use_container_width=True)
    with plot_col2:
        st.plotly_chart(plot_dose_response(dose_df), use_container_width=True)
    
    st.markdown("---")
    st.subheader("My Action Items")
    st.warning("You have **2** data points flagged for review in the **QC & Integrity Center**.")

# --- QC Analyst View ---
with qc_tab:
    if user_role not in ['QC Analyst']:
        st.warning("You are viewing a dashboard outside your primary role.")
    
    st.header("QC Analyst Dashboard")
    st.markdown("Tools for monitoring process stability, instrument performance, and triaging data integrity issues.")

    with st.expander("ℹ️ How to Use This Dashboard", expanded=False):
        st.info("""
            - **Levey-Jennings Chart:** The gold standard for monitoring QC samples over time against statistical limits (mean +/- 1, 2, 3 SD). Use this to spot trends or shifts *before* they cause a failure.
            - **Pareto Chart:** Identifies the vital few error sources causing the majority of problems (the 80/20 rule). Focus your improvement efforts on the tallest bars.
            - **Instrument Performance:** Rank instruments by their error rates to proactively schedule maintenance or retraining.
        """)
    
    instrument_id = st.selectbox("Select Instrument for QC Monitoring", options=hplc_df['instrument_id'].unique())
    instrument_data = hplc_df[hplc_df['instrument_id'] == instrument_id]
    
    plot_col1, plot_col2 = st.columns(2)
    with plot_col1:
        st.plotly_chart(plot_levey_jennings(instrument_data), use_container_width=True)
    with plot_col2:
        st.plotly_chart(plot_pareto_chart(error_df), use_container_width=True)

    st.markdown("---")
    st.subheader("Instrument Performance Leaderboard")
    inst_perf = hplc_df.groupby('instrument_id')['analyte_concentration'].apply(lambda x: (np.abs(stats.zscore(x)) > 2.5).sum()).reset_index()
    inst_perf.rename(columns={'analyte_concentration': 'Outlier Count'}, inplace=True)
    inst_perf = inst_perf.sort_values('Outlier Count', ascending=False)
    st.dataframe(inst_perf, use_container_width=True)
    st.caption("Outlier count based on values > 2.5 standard deviations from the mean for each instrument.")

# --- Add compliance footer to all pages ---
display_compliance_footer()
