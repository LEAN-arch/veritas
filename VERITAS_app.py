# VERITAS_app.py
import streamlit as st
import pandas as pd

# Import foundational modules for the main app
from utils import auth, data_connector as dc, config
from utils.plotters import plot_kpi_sankey, plot_gantt_chart, plot_pareto_chart

# Import page-rendering functions from the new modular pages
from pages import (
    p1_process_capability_dashboard,
    p2_stability_program_dashboard,
    p3_regulatory_support,
    p4_governance_audit_hub,
    p5_deviation_hub
)

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
    dc.initialize_session_data()

# --- 3. Render Universal UI Elements (Sidebar and Footer) ---
auth.render_main_sidebar()
auth.display_compliance_footer()

# --- 4. Centralized Audit Log for User Login ---
if not st.session_state.get('login_audited', False):
    dc.write_to_audit_log(
        st.session_state.db_connection,
        user=st.session_state.username,
        action="User Login",
        details=f"User logged in and was assigned the '{st.session_state.user_role}' role view."
    )
    st.session_state.login_audited = True

# --- 5. Page Routing: Map page names to their render functions ---
# This is a scalable way to manage a multi-page app.
PAGE_ROUTER = {
    "VERITAS Command Center": "render_main_dashboard", # Special case for the home page
    "Process Capability Dashboard": p1_process_capability_dashboard.render_page,
    "Stability Program Dashboard": p2_stability_program_dashboard.render_page,
    "Regulatory Support": p3_regulatory_support.render_page,
    "Governance & Audit Hub": p4_governance_audit_hub.render_page,
    "Deviation Hub": p5_deviation_hub.render_page
}

# --- Role-Based Page Access Control ---
# Define which pages each role can see
ROLE_PERMISSIONS = {
    'DTE Leadership': list(PAGE_ROUTER.keys()),
    'Study Director': ["VERITAS Command Center", "Process Capability Dashboard", "Stability Program Dashboard", "Regulatory Support", "Governance & Audit Hub"],
    'Scientist': ["VERITAS Command Center", "Process Capability Dashboard", "Stability Program Dashboard", "Regulatory Support"],
    'QC Analyst': ["VERITAS Command Center", "Process Capability Dashboard", "Deviation Hub", "Governance & Audit Hub"]
}

# --- Dynamic Page Links based on Role ---
# This replaces the hardcoded page links
st.sidebar.markdown("## Analytical Modules")
user_role = st.session_state.user_role
for page_name in ROLE_PERMISSIONS[user_role]:
    if page_name != "VERITAS Command Center":
        st.sidebar.page_link(f"pages/{page_name.lower().replace(' ', '_').replace('&', 'and')}.py", label=page_name)

# --- Dashboard Rendering Functions (for the main page) ---
def render_dte_view():
    """Renders the main dashboard for DTE Leadership."""
    st.markdown("##### High-level overview of operational efficiency, program risk, and system health.")
    
    # Load data dynamically
    hplc_df = dc.fetch_hplc_data(st.session_state.db_connection)
    deviations_df = dc.fetch_deviations_data()
    gantt_df = dc.fetch_gantt_data(st.session_state.db_connection)
    
    # --- Dynamic KPIs ---
    kpi_cols = st.columns(4)
    active_deviations = deviations_df[deviations_df['status'] != 'Closed'].shape[0]
    kpi_cols[0].metric("Active Deviations", active_deviations, help="Total number of open deviation investigations.")
    
    dqs = 100 * (1 - (hplc_df['Purity'] < 98.0).mean()) # Example DQS calculation
    kpi_cols[1].metric("Data Quality Score (DQS)", f"{dqs:.1f}%", f"{((dqs/100)-0.95)*100:.1f}% vs Target", help="Percentage of data passing automated checks.")
    
    # Placeholder KPIs (would be calculated in a real scenario)
    kpi_cols[2].metric("First Pass Yield (FPY)", "88.2%", "-1.5%")
    kpi_cols[3].metric("Mean Time to Resolution (MTTR)", f"{active_deviations * 1.2:.1f} Hrs", "-0.5 Hrs", delta_color="inverse")

    st.markdown("---")
    
    col1, col2 = st.columns((6, 4))
    with col1:
        st.subheader("Data Package Velocity & Yield")
        sankey_data = {'ingested': len(hplc_df), 'passed': len(hplc_df[hplc_df['Purity'] >= 98.0]), 'failed': len(hplc_df[hplc_df['Purity'] < 98.0])}
        st.plotly_chart(plot_kpi_sankey(sankey_data), use_container_width=True)

        st.subheader("Drug Program Timelines & Submission Risk")
        st.plotly_chart(plot_gantt_chart(gantt_df), use_container_width=True)
    with col2:
        st.subheader("QC Failure Hotspots (from Deviations)")
        # This chart is now derived from the LIVE deviation data
        if not deviations_df.empty:
            error_data = pd.DataFrame(deviations_df['title'].str.extract(r'(OOS|Drift|Breach|Contamination|Missing)')[0].value_counts()).reset_index()
            error_data.columns = ['Error Type', 'Frequency']
            st.plotly_chart(plot_pareto_chart(error_data), use_container_width=True)
        else:
            st.info("No deviation data to generate Pareto chart.")

def render_scientist_director_view():
    """Renders the main dashboard for Scientists and Study Directors."""
    st.markdown("##### Overview of key programs and links to analytical modules.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.** This Command Center provides a high-level summary.")
    
    hplc_df = dc.fetch_hplc_data(st.session_state.db_connection)
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Total Active Studies", len(hplc_df['study_id'].unique()))
    kpi_cols[1].metric("Upcoming Stability Pulls", "12 Lots")
    kpi_cols[2].metric("Pending Action Items", "5", delta="2 new", delta_color="inverse")
    
    st.markdown("---")
    st.subheader("Use the sidebar to navigate to your analytical tools.")

def render_qc_analyst_view():
    """Renders the main dashboard for QC Analysts."""
    st.markdown("##### Central hub for managing deviations and monitoring instrument health.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.** This Command Center provides a high-level summary of active issues.")

    deviations_df = dc.fetch_deviations_data()
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("New Deviations", deviations_df[deviations_df['status'] == 'New'].shape[0])
    kpi_cols[1].metric("In Progress Deviations", deviations_df[deviations_df['status'] == 'In Progress'].shape[0])
    kpi_cols[2].metric("Deviations Pending QA", deviations_df[deviations_df['status'] == 'Pending QA'].shape[0])

    st.markdown("---")
    st.subheader("Use the sidebar to navigate to the Deviation Hub and other tools.")

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
