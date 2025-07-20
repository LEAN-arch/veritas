# VERITAS_app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth
from utils.plotters import (
    plot_sankey_flow, 
    plot_gantt_chart,
    plot_pareto_chart
)

# --- Page Configuration: Must be the first command ---
st.set_page_config(
    page_title="VERITAS Command Center",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PHASE 1: Enterprise Authentication ---
# SME EXPLANATION: The entire application is now wrapped in an authentication check.
# No data is loaded or displayed until the user successfully logs in. This is a
# non-negotiable security feature for any enterprise application.
user_role = auth.authenticate_user()

# --- PHASE 1: Data Architecture & Integration ---
# SME EXPLANATION: We now simulate connecting to a database and fetching data and configuration
# using the dedicated data_connector module. This architecture separates data access from the
# presentation layer (the Streamlit app), which is a critical best practice.
@st.cache_data(ttl=3600) # Cache the connection and config for 1 hour
def load_initial_data():
    """Connects to DB and fetches initial config and datasets."""
    db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
    app_config = dc.fetch_app_config(db_connection)
    hplc_data = dc.fetch_hplc_data(db_connection)
    deviations_data = dc.fetch_deviations_data(db_connection)
    return db_connection, app_config, hplc_data, deviations_data

db_connection, APP_CONFIG, hplc_df, deviations_df = load_initial_data()

# --- Audit Log Entry for User Login ---
# This ensures that the user's session start is captured for compliance.
if 'login_audited' not in st.session_state:
    dc.write_to_audit_log(
        db_connection,
        user=st.session_state.username,
        action="User Login",
        details=f"User logged in and was assigned the '{user_role}' role view."
    )
    st.session_state.login_audited = True

# --- Main Application Header ---
st.title("VERITAS Command Center")
st.header(f"'{user_role}' View")
st.markdown("---")

# --- DTE LEADERSHIP VIEW ---
if user_role == 'DTE Leadership':
    st.markdown("##### High-level overview of operational efficiency, program risk, and system health.")
    
    # KPIs using data from the simulated database
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Active Deviations", deviations_df[deviations_df['status'] != 'Closed'].shape[0], help="Total number of open deviation investigations.")
    with kpi_cols[1]:
        # Calculate Data Quality Score (DQS) based on a sample rule
        dqs = 100 * (1 - (hplc_df['Purity'] < 98.0).mean())
        st.metric("Data Quality Score (DQS)", f"{dqs:.1f}%", f"{((dqs/100)-0.95)*100:.1f}% vs Target", help="A composite score reflecting the percentage of data passing automated checks.")
    with kpi_cols[2]:
        st.metric("First Pass Yield (FPY)", "88.2%", "-1.5%", help="The percentage of data packages that pass all QC checks on the first attempt.")
    with kpi_cols[3]:
        st.metric("Mean Time to Resolution (MTTR)", "4.1 Hrs", "-0.5 Hrs", delta_color="inverse", help="Average time to investigate and close a data discrepancy ticket.")

    st.markdown("---")
    
    col1, col2 = st.columns((6, 4))
    with col1:
        st.subheader("Data Package Velocity & Yield")
        st.plotly_chart(plot_sankey_flow(), use_container_width=True)
        st.subheader("Drug Program Timelines & Submission Risk")
        gantt_data = pd.DataFrame([
            dict(Program="VX-770 (CFTR)", Start='2023-01-15', Finish='2023-06-30', Status='Completed', Risk='Low'),
            dict(Program="VX-809 (CFTR)", Start='2023-03-01', Finish='2023-09-15', Status='Completed', Risk='Low'),
            dict(Program="VX-561 (AATD)", Start='2023-07-01', Finish='2024-01-20', Status='In Progress', Risk='Medium'),
            dict(Program="VX-121 (Pain)", Start='2023-10-10', Finish='2024-05-30', Status='In Progress', Risk='High'),
        ])
        st.plotly_chart(plot_gantt_chart(gantt_data), use_container_width=True)
    with col2:
        st.subheader("Active System & Data Alerts")
        alert_df = pd.DataFrame([
            {"Priority": "High", "Alert": "Instrument HPLC-03 drift exceeds threshold", "Owner": "QC Analyst"},
            {"Priority": "Medium", "Alert": "Ingestion latency > 10 mins", "Owner": "DTE Ops"},
            {"Priority": "Low", "Alert": "3 reports pending signature > 48h", "Owner": "S. Director"},
        ])
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
        st.subheader("QC Failure Hotspots")
        error_data = pd.DataFrame(list({
            'Out of Spec Result': 45, 'Missing Metadata': 22, 'Instrument Drift': 15,
            'Invalid File Format': 8, 'Analyst Entry Error': 5
        }.items()), columns=['Error Type', 'Frequency']).sort_values(by='Frequency', ascending=False)
        st.plotly_chart(plot_pareto_chart(error_data), use_container_width=True)

# --- SCIENTIST / STUDY DIRECTOR VIEW ---
elif user_role in ['Scientist', 'Study Director']:
    st.markdown("##### Overview of key programs and links to analytical modules.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.** This Command Center provides a high-level summary. Detailed tools for Stability, Process Capability, and Regulatory Support are available on their respective pages.")
    
    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.metric("Total Active Studies", len(hplc_df['study_id'].unique()))
    with kpi_cols[1]:
        st.metric("Upcoming Stability Pulls", "12 Lots", help="Number of stability lots with testing due in the next 30 days.")
    with kpi_cols[2]:
        st.metric("Pending Action Items", "5", delta="2 new", delta_color="inverse")
        
    st.markdown("---")
    st.subheader("Module Quick Links")
    
    st.page_link("pages/1_Process_Capability_Dashboard.py", label="**Process Capability Dashboard**", icon="📈", help="Analyze historical process stability and capability (Cpk) for any product or assay.")
    st.page_link("pages/2_Stability_Program_Dashboard.py", label="**Stability Program Dashboard**", icon="⏳", help="View and trend stability data against specification limits.")
    st.page_link("pages/3_CMC_Regulatory_Support.py", label="**CMC Regulatory Support**", icon="📄", help="Generate formatted data summaries and PDF reports for regulatory submissions.")
    st.page_link("pages/4_Governance_&_Audit.py", label="**Governance & Audit Hub**", icon="⚖️", help="Review the GxP audit trail and data lineage.")

# --- QC ANALYST VIEW ---
elif user_role == 'QC Analyst':
    st.markdown("##### Central hub for managing deviations and monitoring instrument health.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.** This Command Center provides a high-level summary of active issues.")

    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.metric("New Deviations", deviations_df[deviations_df['status'] == 'New'].shape[0], help="Number of deviations awaiting initial investigation.")
    with kpi_cols[1]:
        st.metric("In Progress Deviations", deviations_df[deviations_df['status'] == 'In Progress'].shape[0])
    with kpi_cols[2]:
        st.metric("Deviations Pending QA", deviations_df[deviations_df['status'] == 'Pending QA'].shape[0])

    st.markdown("---")
    st.subheader("Module Quick Links")

    st.page_link("pages/1_Process_Capability_Dashboard.py", label="**Process Capability Dashboard**", icon="📈", help="Analyze historical process stability and capability (Cpk) for any product or assay.")
    st.page_link("pages/5_Deviation_Hub.py", label="**Deviation Hub**", icon="📌", help="Manage the lifecycle of deviations using an interactive Kanban board.")


# --- Global Compliance Footer ---
auth.display_compliance_footer()
