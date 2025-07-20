# pages/1_Process_Capability_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth
from utils.plotters import (
    plot_historical_control_chart,
    plot_process_capability
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Process Capability Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Authentication and Data Loading ---
user_role = auth.authenticate_user()
db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
APP_CONFIG = dc.fetch_app_config(db_connection)
hplc_df = dc.fetch_hplc_data(db_connection)

# --- Page Header ---
st.title("📈 Process Capability Dashboard")
st.markdown("Analyze historical process stability and capability (Cpk) for any product or assay.")

with st.expander("ℹ️ SME Overview: Understanding Process Capability"):
    st.info(f"""
        - **Process Capability (Cpk):** A statistical measure of a process's ability to produce output within specification limits. A Cpk of **{APP_CONFIG['process_capability']['cpk_target']}** or greater is generally considered capable.
        - **Control Charts (I-Chart):** A graphical tool used to monitor a process over time. It helps distinguish between common cause variation (the natural noise of the process) and special cause variation (unexpected, assignable events).
        - **How to Use:** Select a Critical Quality Attribute (CQA) and a time frame to analyze. The control chart shows stability over time, while the Cpk histogram shows capability within that time frame.
    """)

# --- Sidebar for Filtering ---
st.sidebar.markdown("## Filter Data")
study_id_filter = st.sidebar.selectbox(
    "Filter by Study:",
    options=['All'] + sorted(hplc_df['study_id'].unique()),
    key="study_filter"
)
instrument_id_filter = st.sidebar.selectbox(
    "Filter by Instrument:",
    options=['All'] + sorted(hplc_df['instrument_id'].unique()),
    key="instrument_filter"
)

# --- Apply Filters to Data ---
filtered_data = hplc_df.copy()
if study_id_filter != 'All':
    filtered_data = filtered_data[filtered_data['study_id'] == study_id_filter]
if instrument_id_filter != 'All':
    filtered_data = filtered_data[filtered_data['instrument_id'] == instrument_id_filter]

st.sidebar.success(f"{len(filtered_data)} data points selected.")

# --- PHASE 2: Dynamic and Configurable CQA Selection ---
st.subheader("Analysis Configuration")

# Get available CQAs from the external configuration
available_cqas = APP_CONFIG['process_capability']['available_cqas']
selected_cqa = st.selectbox(
    "Select a Critical Quality Attribute (CQA) to Analyze:",
    options=available_cqas
)

# --- PHASE 2: Historical Trending for SPC ---
# Define date range slider
min_date = hplc_df['injection_time'].min().date()
max_date = hplc_df['injection_time'].max().date()
date_range = st.slider(
    "Select Date Range for Analysis:",
    min_value=min_date,
    max_value=max_date,
    value=(max_date - timedelta(days=90), max_date), # Default to last 90 days
    format="YYYY-MM-DD"
)

# --- Display Analytics ---
st.markdown("---")

if len(filtered_data) > 2:
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            plot_historical_control_chart(filtered_data, selected_cqa, date_range),
            use_container_width=True
        )

    with col2:
        # For Cpk, we need spec limits. We'll simulate them here.
        # In a real app, these would come from the config or a database.
        spec_limits = {
            "Purity": {"LSL": 98.0, "USL": 102.0},
            "Aggregate Content": {"LSL": 0, "USL": 1.0},
            "Main Impurity": {"LSL": 0, "USL": 0.5},
            "Bio-activity": {"LSL": 90.0, "USL": 110.0}
        }
        lsl = spec_limits[selected_cqa].get("LSL")
        usl = spec_limits[selected_cqa].get("USL")
        
        st.plotly_chart(
            plot_process_capability(filtered_data, selected_cqa, lsl, usl),
            use_container_width=True
        )
else:
    st.warning("Not enough data available for the selected filters to perform analysis.")

# --- Global Compliance Footer ---
auth.display_compliance_footer()
