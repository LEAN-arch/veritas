# pages/2_QC_&_Integrity_Center.py
import streamlit as st
import pandas as pd
import time
from sklearn.ensemble import IsolationForest
import numpy as np

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_hplc_data
from utils.plotters import plot_qq, plot_ml_anomaly_results

st.set_page_config(layout="wide", page_title="QC & Integrity Center")
get_user_role()
st.title("Module 2: Automated QC & Integrity Engine")
st.markdown("Define, execute, and review automated data quality checks with statistical and ML-powered tools.")

# Load mock data
@st.cache_data
def load_data():
    return create_mock_hplc_data(100)
df = load_data()

# --- Data Selection ---
st.subheader("1. Select Data Package for Analysis")
dataset_option = st.selectbox(
    "Select a Dataset", 
    options=df['study_id'].unique(),
    help="Choose the dataset you wish to subject to quality control analysis."
)
selected_df = df[df['study_id'] == dataset_option]

# --- QC Tabs ---
summary_tab, stats_tab, ml_tab = st.tabs(["📋 QC Summary & Triage", "📈 Statistical Deep Dive", "🤖 ML Anomaly Detection"])

with summary_tab:
    st.subheader("QC Rule Execution & Discrepancy Triage")
    with st.expander("ℹ️ How to Use This Tab", expanded=False):
        st.info("""
            - **Configure & Run:** Select the QC rules to apply from the standard library.
            - **Data Quality Score (DQS):** See a high-level score calculated from the results. A lower score indicates more issues.
            - **Discrepancy Report:** Review, assign, and resolve flagged data points. Changes made here are fully audited.
        """)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Configure QC Rules")
        rules = {
            'check_nulls': st.checkbox("Check for missing values", value=True, help="Scans for any empty cells."),
            'check_negatives': st.checkbox("Check for negative concentrations", value=True, help="Flags concentrations < 0, which are physically impossible."),
            'check_retention_range': st.checkbox("Check retention time spec (2.4-2.8 min)", value=True, help="Verifies that retention times fall within the validated method's specification."),
        }
        
        if st.button("▶️ Execute QC Analysis"):
            with st.spinner("Executing QC checks..."):
                time.sleep(1)
                st.session_state['qc_run'] = True
    
    with col2:
        if st.session_state.get('qc_run', False):
            st.markdown("#### QC Results")
            # Simulate results
            total_issues = selected_df.isnull().sum().sum() + (selected_df['analyte_concentration'] < 0).sum()
            num_cells = selected_df.shape[0] * selected_df.shape[1]
            dqs = 100 * (1 - total_issues / num_cells)

            st.metric("Data Quality Score (DQS)", f"{dqs:.1f}%", f"-{total_issues} issues found")
            
            st.markdown("#### Discrepancy Report & Triage")
            discrepancies = selected_df[
                selected_df.isnull().any(axis=1) | (selected_df['analyte_concentration'] < 0)
            ].copy()
            discrepancies['Issue'] = "Missing Value"
            discrepancies.loc[discrepancies['analyte_concentration'] < 0, 'Issue'] = "Negative Concentration"
            discrepancies['Status'] = 'Open'
            discrepancies['Assigned To'] = 'QC Analyst'
            
            st.data_editor(discrepancies[['sample_id', 'Issue', 'Status', 'Assigned To']], use_container_width=True)

with stats_tab:
    st.subheader("Statistical Deep Dive")
    with st.expander("ℹ️ How to Use This Tab", expanded=False):
        st.info("""
            Use these plots to understand the underlying distribution and characteristics of your data.
            - **Distribution Plot:** Visualizes the spread of a single parameter. A 'bell curve' shape suggests a normal distribution.
            - **Q-Q Plot:** A more rigorous check for normality. If data points follow the red line, the data is normally distributed, which is an assumption for many statistical tests.
        """)
    
    param_to_analyze = st.selectbox("Select Parameter for Statistical Analysis", 
                                    options=['analyte_concentration', 'peak_area', 'retention_time'])
    
    plot_col1, plot_col2 = st.columns(2)
    with plot_col1:
        st.markdown(f"**Distribution of {param_to_analyze}**")
        fig = px.histogram(selected_df, x=param_to_analyze, marginal="box",
                           color_discrete_sequence=[VERTEX_COLORS['lightblue']])
        st.plotly_chart(fig, use_container_width=True)
    with plot_col2:
        st.markdown(f"**Normality Check (Q-Q Plot)**")
        fig = plot_qq(selected_df[param_to_analyze].dropna())
        st.plotly_chart(fig, use_container_width=True)

with ml_tab:
    st.subheader("Machine Learning-Powered Anomaly Detection")
    with st.expander("ℹ️ How to Use This Tab", expanded=False):
        st.info("""
            This tool uses an **Isolation Forest** algorithm to find subtle, multi-variate outliers that simple rule-based checks might miss.
            - **Purpose:** To identify data points that are 'unusual' when considering multiple parameters at once.
            - **Significance:** Can detect complex issues like unexpected instrument behavior or sample preparation errors.
            - **Interpretation:** The plot shows outliers flagged in red. These are candidates for investigation, not automatically invalid.
        """)
        
    if st.button("🤖 Run Isolation Forest Analysis"):
        with st.spinner("Training model and identifying anomalies..."):
            numeric_cols = selected_df.select_dtypes(include=np.number).dropna()
            iso_forest = IsolationForest(contamination=0.05, random_state=42)
            preds = iso_forest.fit_predict(numeric_cols)
            
            st.plotly_chart(plot_ml_anomaly_results(numeric_cols, preds), use_container_width=True)
            st.success(f"Analysis complete. Found { (preds == -1).sum() } potential anomalies for review.")

display_compliance_footer()
