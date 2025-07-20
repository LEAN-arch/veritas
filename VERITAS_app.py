# VERITAS_app.py
import streamlit as st
import pandas as pd
from utils import auth, data_connector as dc, config, plotters

st.set_page_config(
    page_title="VERITAS Command Center", page_icon="🧪", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.vertex.com/contact-us',
        'About': f"VERITAS Command Center, Version {config.APP_CONFIG['app_version']}"
    }
)

# Initialize session state (user, data, etc.) once
auth.initialize_session()
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
    st.session_state.app_config = dc.fetch_app_config(st.session_state.db_connection)
    dc.initialize_session_data()

# Render the sidebar with role switcher. Streamlit handles the page links automatically.
auth.render_main_sidebar()

# Log user login action once per session
if not st.session_state.get('login_audited', False):
    dc.write_to_audit_log(
        _connection=st.session_state.db_connection, user=st.session_state.username,
        action="User Login", details=f"User logged in with the '{st.session_state.user_role}' role view."
    )
    st.session_state.login_audited = True

# --- THE FIX IS HERE ---
# The manual st.page_link loop has been completely removed.
# Streamlit will now automatically discover and display the pages from the `pages/` directory.
# Access control is now handled by the `auth.check_page_authorization()` call within each page file.

def render_dte_view():
    st.markdown("##### High-level overview of operational efficiency, program risk, and system health.")
    hplc_df, deviations_df, gantt_df = dc.fetch_hplc_data(), dc.fetch_deviations_data(), dc.fetch_gantt_data()
    kpi_cols = st.columns(4)
    active_deviations = deviations_df[deviations_df['status'] != 'Closed'].shape[0]
    kpi_cols[0].metric("Active Deviations", active_deviations)
    dqs_lsl = config.APP_CONFIG['process_capability']['spec_limits']['Purity']['LSL']
    dqs_score = 100 * (hplc_df['Purity'] >= dqs_lsl).mean()
    kpi_cols[1].metric("Data Quality Score (DQS)", f"{dqs_score:.1f}%", f"{((dqs_score/100)-0.95)*100:.1f}% vs Target")
    kpi_cols[2].metric("First Pass Yield (FPY)", "88.2%", "-1.5%")
    kpi_cols[3].metric("Mean Time to Resolution (MTTR)", f"{active_deviations * 1.2:.1f} Hrs", "-0.5 Hrs", delta_color="inverse")
    st.markdown("---")
    col1, col2 = st.columns((6, 4))
    with col1:
        st.subheader("Data Package Velocity & Yield")
        sankey_data = {'ingested': len(hplc_df), 'passed': (hplc_df['Purity'] >= dqs_lsl).sum(), 'failed': (hplc_df['Purity'] < dqs_lsl).sum()}
        st.plotly_chart(plotters.plot_kpi_sankey(sankey_data), use_container_width=True)
        st.subheader("Drug Program Timelines & Submission Risk")
        st.plotly_chart(plotters.plot_gantt_chart(gantt_df), use_container_width=True)
    with col2:
        st.subheader("QC Failure Hotspots (from Deviations)")
        if not deviations_df.empty:
            error_data = pd.DataFrame(deviations_df['title'].str.extract(r'(OOS|Drift|Breach|Contamination|Missing)')[0].value_counts()).reset_index()
            error_data.columns = ['Error Type', 'Frequency']
            st.plotly_chart(plotters.plot_pareto_chart(error_data), use_container_width=True)

def render_scientist_director_view():
    st.markdown("##### Overview of key programs and links to analytical modules.")
    st.info("💡 **Navigate to specialized modules using the sidebar on the left.**")
    hplc_df = dc.fetch_hplc_data()
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

st.title("VERITAS Command Center")
st.header(f"'{st.session_state.user_role}' View")
st.markdown("---")

user_role = st.session_state.user_role
if user_role == 'DTE Leadership':
    render_dte_view()
elif user_role in ['Scientist', 'Study Director']:
    render_scientist_director_view()
elif user_role == 'QC Analyst':
    render_qc_analyst_view()

auth.display_compliance_footer()
