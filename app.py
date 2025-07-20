# VERITAS_app.py
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from utils.auth import get_user_role, display_compliance_footer
from utils.data_generator import get_program_gantt_data, create_mock_hplc_data, get_qc_error_data
from utils.plotters import plot_sankey_flow, plot_gantt_chart, plot_spc_chart, plot_pareto_chart, VERTEX_COLORS

# --- Page Configuration (CORRECTED) ---
st.set_page_config(
    page_title="VERITAS Command Center",
    page_icon="🧪",  # Changed from "V_logo.png" to a standard emoji
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Logo and Header (CORRECTED) ---
# st.image("vertex-logo.png", width=250) # Commented out this line to prevent the error
st.markdown("<h1 style='color: {};'>VERITAS Command Center</h1>".format(VERTEX_COLORS['blue']), unsafe_allow_html=True)
st.markdown("Automated QC, Reporting, and Data Integrity for Pre-Clinical Research")
st.markdown("---")

# --- Authentication and Role-Based Access ---
user_role = get_user_role()

# --- Load Data (cached for performance) ---
@st.cache_data
def load_data():
    hplc_data = create_mock_hplc_data(100)
    gantt_data = get_program_gantt_data()
    error_data = get_qc_error_data()
    return hplc_data, gantt_data, error_data

hplc_df, gantt_df, error_df = load_data()

# --- DTE-RPMS Command Center (Module 4) ---
# This main page serves as the dashboard hub.

def dte_leadership_view():
    st.header("DTE Leadership Dashboard")
    st.markdown("High-level overview of system health, data quality, and program velocity.")
    
    # KPI Scorecard
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Overall Data Quality Score (DQS)", "96.4%", "1.2%")
    kpi2.metric("First Pass Yield (FPY)", "85.1%", "-0.5%")
    kpi3.metric("Avg. Report Cycle Time", "3.2 Hours", "-8% vs Target")
    kpi4.metric("Submission Readiness", "99.8%", "Ready")

    st.markdown("---")
    
    col1, col2 = st.columns((1, 1))
    with col1:
        st.plotly_chart(plot_sankey_flow(), use_container_width=True)
    with col2:
        st.plotly_chart(plot_gantt_chart(gantt_df), use_container_width=True)

def scientist_view(data):
    st.header("Scientist / Study Director Dashboard")
    
    # Filter for a specific study
    study_id = st.selectbox("Select a Study to Analyze", options=data['batch_id'].unique())
    study_data = data[data['batch_id'] == study_id]
    
    st.subheader(f"Analysis for Study: {study_id}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Samples in Study", len(study_data))
        st.metric("Avg. Analyte Concentration", f"{study_data['analyte_concentration'].mean():.2f} µg/mL")
        st.progress(85, text="Live QC Status: 85% Checks Passed")

    with col2:
        # Interactive Data Exploration
        st.markdown("<b>Interactive Data Exploration</b>", unsafe_allow_html=True)
        x_axis = st.selectbox("X-Axis", options=study_data.columns, index=5) # retention_time
        y_axis = st.selectbox("Y-Axis", options=study_data.columns, index=3) # analyte_concentration
        
        import plotly.express as px
        fig = px.scatter(study_data, x=x_axis, y=y_axis, color="instrument_id", 
                         title=f"{y_axis} vs. {x_axis}", hover_data=['sample_id'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(study_data.head())


def qc_analyst_view(data, error_data):
    st.header("QC Analyst Dashboard")
    st.markdown("Tools for monitoring process stability and triaging data integrity issues.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Discrepancy Triage Queue")
        discrepancies = data[~data['analyte_concentration'].between(0, 120) | data['peak_area'].isnull()].copy()
        discrepancies['Status'] = 'Open'
        st.data_editor(discrepancies[['sample_id', 'batch_id', 'analyte_concentration', 'peak_area', 'Status']])
    
    with col2:
        st.plotly_chart(plot_pareto_chart(error_data), use_container_width=True)
        
    st.markdown("---")
    st.subheader("Live Instrument Process Control")
    instrument = st.selectbox("Select Instrument to Monitor", options=data['instrument_id'].unique())
    instrument_data = data[data['instrument_id'] == instrument]
    st.plotly_chart(plot_spc_chart(instrument_data), use_container_width=True)


# --- Render the correct view based on role ---
if user_role == 'DTE Leadership':
    dte_leadership_view()
elif user_role in ['Scientist', 'Study Director']:
    scientist_view(hplc_df)
elif user_role == 'QC Analyst':
    qc_analyst_view(hplc_df, error_df)

# --- Add compliance footer to all pages ---
display_compliance_footer()
