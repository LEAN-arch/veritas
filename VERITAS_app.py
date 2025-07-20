# VERITAS_app.py
import streamlit as st
import pandas as pd

# Import foundational modules for the main app
from utils import auth, data_connector as dc, config
from utils.plotters import plot_kpi_sankey, plot_gantt_chart, plot_pareto_chart

# --- 1. Application Setup: Called only once ---
st.set_page_config(
    page_title="VERITAS Command Center",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.vertex.com/contact-us',
        'About': f"VERITAS Command Center, Version {config.APP_CONFIG['app_version']}"
    }
)

# --- 2. Session Initialization and Data Loading ---
# This block runs once per session to set up the environment.
if 'session_initialized' not in st.session_state:
    auth.initialize_session()
    
    # Store app config and DB connection in session state for universal access
    st.session_state.db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
    st.session_state.app_config = dc.fetch_app_config(st.session_state.db_connection)
    
    # Initialize mutable data (deviations, audit log) into session state
    # This copies the data from the cached factory, allowing for safe modification.
    dc.initialize_session_data()

# --- 3. Render Universal UI Elements ---
auth.render_main_sidebar()

# --- 4. Centralized Audit Log for User Login ---
if not st.session_state.get('login_audited', False):
    dc.write_to_audit_log(
        st.session_state.db_connection,
        user=st.session_state.username,
        action="User Login",
        details=f"User logged in and was assigned the '{st.session_state.user_role}' role view."
    )
    st.session_state.login_audited = True

# --- Role-Based Page Access Control ---
# Define which pages each role can see
PAGE_PERMISSIONS = {
    'DTE Leadership': [
        "Process Capability Dashboard", "Stability Program Dashboard", 
        "Regulatory Support", "Governance & Audit Hub", "Deviation Hub"
    ],
    'Study Director': [
        "Process Capability Dashboard", "Stability Program Dashboard", 
        "Regulatory Support", "Governance & Audit Hub"
    ],
    'Scientist': [
        "Process Capability Dashboard", "Stability Program Dashboard", "Regulatory Support"
    ],
    'QC Analyst': [
        "Process Capability Dashboard", "Deviation Hub", "Governance & Audit Hub"
    ]
}

# --- Dynamic Page Links based on Role ---
st.sidebar.markdown("## Analytical Modules")
user_role = st.session_state.user_role
for page_name in PAGE_PERMISSIONS.get(user_role, []):
    # Convert page name to the expected file name format
    file_name = f"pages/{page_name.lower().replace(' & ', '_and_').replace(' ', '_')}.py"
    st.sidebar.page_link(file_name, label=page_name)

# --- Dashboard Rendering Functions (for the main page) ---
def render_dte_view():
    st.markdown("##### High-level overview of operational efficiency, program risk, and system health.")
    
    hplc_df = dc.fetch_hplc_data(st.session_state.db_connection)
    deviations_df = dc.fetch_deviations_data()
    gantt_df = dc.fetch_gantt_data(st.session_state.db_connection)
    
    kpi_cols = st.columns(4)
    active_deviations = deviations_df[deviations_df['status'] != 'Closed'].shape[0]
    kpi_cols[0].metric("Active Deviations", active_deviations, help="Total number of open deviation investigations.")
    
    dqs = config.APP_CONFIG.get('process_capability', {}).get('spec_limits', {}).get('Purity', {}).get('LSL', 98.0)
    dqs_score = 100 * (hplc_df['Purity'] >= dqs).mean()
    kpi_cols[1].metric("Data Quality Score (DQS)", f"{dqs_score:.1f}%", f"{((dqs_score/100)-0.95)*100:.1f}% vs Target", help="Percentage of data passing automated checks.")
    
    kpi_cols[2].metric("First Pass Yield (FPY)", "88.2%", "-1.5%")
    kpi_cols[3].metric("Mean Time to Resolution (MTTR)", f"{active_deviations * 1.2:.1f} Hrs", "-0.5 Hrs", delta_color="inverse")

    st.markdown("---")
    
    col1, col2 = st.columns((6, 4))
    with col1:
        st.subheader("Data Package Velocity & Yield")
        sankey_data = {'ingested': len(hplc_df), 'passed': len(hplc_df[hplc_df['Purity'] >= dqs]), 'failed': len(hplc_df[hplc_df['Purity'] < dqs])}
        st.plotly_chart(plot_kpi_sankey(sankey_data), use_container_width=True)
        st.subheader("Drug Program Timelines & Submission Risk")
        st.plotly_chart(plot_gantt_chart(gantt_df), use_container_width=True)
    with col2:
        st.subheader("QC Failure Hotspots (from Deviations)")
        if not deviations_df.empty:
            error_data = pd.DataFrame(deviations_df['title'].str.extract(r'(OOS|Drift|Breach|Contamination|Missing)')[0].value_counts()).reset_index()
            error_data.columns = ['Error Type', 'Frequency']
            st.plotly_chart(plot_pareto_chart(error_data), use_container_width=True)

def render_scientist_director_view():
    st.markdown("##### Overview of key programs and links to analytical modules.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.**")
    
    hplc_df = dc.fetch_hplc_data(st.session_state.db_connection)
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Active Studies", len(hplc_df['study_id'].unique()))
    kpi_cols[1].metric("Upcoming Stability Pulls", "12 Lots")
    kpi_cols[2].metric("Pending Action Items", "5", delta="2 new", delta_color="inverse")

def render_qc_analyst_view():
    st.markdown("##### Central hub for managing deviations and monitoring instrument health.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.**")

    deviations_df = dc.fetch_deviations_data()
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("New Deviations", deviations_df[deviations_df['status'] == 'New'].shape[0])
    kpi_cols[1].metric("In Progress Deviations", deviations_df[deviations_df['status'] == 'In Progress'].shape[0])
    kpi_cols[2].metric("Deviations Pending QA", deviations_df[deviations_df['status'] == 'Pending QA'].shape[0])

# --- 6. Main Application Logic: Render the correct view based on role ---
st.title("VERITAS Command Center")
st.header(f"'{st.session_state.user_role}' View")
st.markdown("---")

# Main dashboard router
if user_role == 'DTE Leadership':
    render_dte_view()
elif user_role in ['Scientist', 'Study Director']:
    render_scientist_director_view()
elif user_role == 'QC Analyst':
    render_qc_analyst_view()

# Add the compliance footer to the bottom of the main page
auth.display_compliance_footer()
