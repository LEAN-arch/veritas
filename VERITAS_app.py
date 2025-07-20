# VERITAS_app.py
import streamlit as st
from utils.auth import get_user_role, display_compliance_footer
from utils.data_generator import *
from utils.plotters import *

# --- Page Configuration: Must be the first Streamlit command ---
st.set_page_config(
    page_title="VERITAS",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Caching: Load all data once ---
@st.cache_data
def load_all_data():
    return {
        "hplc": create_mock_hplc_data(250),
        "gantt": get_program_gantt_data(),
        "errors": get_qc_error_data(),
        "dose": create_dose_response_data(),
        "plate": create_plate_heatmap_data()
    }
data = load_all_data()

# --- Sidebar for Navigation and Controls ---
with st.sidebar:
    st.title("VERITAS")
    st.caption("Vertex Ensured Reporting & Integrity Transformation Automation Suite")
    st.markdown("---")
    user_role = get_user_role()
    st.markdown("---")
    if st.button("Logout"):
        # Clear session state on logout
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# --- Main Application Logic ---
st.header(f"'{user_role}' Command Center")

# --- DTE LEADERSHIP VIEW ---
if user_role == 'DTE Leadership':
    st.markdown("##### High-level overview of operational efficiency, program risk, and system health.")
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]: st.metric("System Uptime", "99.98%", help="Availability of all VERITAS modules over the last 30 days.")
    with kpi_cols[1]: st.metric("Data Quality Score (DQS)", "97.1%", "0.8%", help="A composite score reflecting the percentage of data points passing all automated QC checks.")
    with kpi_cols[2]: st.metric("First Pass Yield (FPY)", "88.2%", "-1.5%", help="The percentage of data packages that pass all QC checks on the first attempt.")
    with kpi_cols[3]: st.metric("Mean Time to Resolution (MTTR)", "4.1 Hrs", "-0.5 Hrs", delta_color="inverse", help="Average time to investigate and close a data discrepancy ticket.")

    st.markdown("---")
    
    col1, col2 = st.columns((6, 4))
    with col1:
        st.subheader("Data Package Velocity & Yield")
        st.plotly_chart(plot_sankey_flow(), use_container_width=True)
        st.subheader("Drug Program Timelines & Submission Risk")
        st.plotly_chart(plot_gantt_chart(data['gantt']), use_container_width=True)
    with col2:
        st.subheader("Active System & Data Alerts")
        alert_df = pd.DataFrame([
            {"Priority": "High", "Alert": "HPLC-03 drift exceeds threshold", "Owner": "QC Analyst"},
            {"Priority": "Medium", "Alert": "Ingestion latency > 10 mins", "Owner": "DTE Ops"},
            {"Priority": "Low", "Alert": "3 reports pending signature > 48h", "Owner": "S. Director"},
        ])
        st.dataframe(alert_df, use_container_width=True, hide_index=True)
        st.subheader("QC Failure Hotspots")
        st.plotly_chart(plot_pareto_chart(data['errors']), use_container_width=True)

# --- SCIENTIST / STUDY DIRECTOR VIEW ---
elif user_role in ['Scientist', 'Study Director']:
    st.markdown("##### Focused dashboard for assay analysis, study tracking, and personal action items.")
    
    study_id = st.selectbox("Select Your Study to Analyze", options=data['hplc']['study_id'].unique())
    study_data = data['hplc'][data['hplc']['study_id'] == study_id]

    kpi_cols = st.columns(3)
    with kpi_cols[0]: st.metric("Samples in Study", len(study_data))
    with kpi_cols[1]: st.metric("Data Quality Score (DQS)", f"{np.random.uniform(95, 99.9):.1f}%")
    with kpi_cols[2]: st.metric("Pending Action Items", 5, delta="2 new", delta_color="inverse")

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔬 Assay Analysis", "📈 Plate & Batch Analysis", "✅ My Tasks"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1: st.plotly_chart(plot_dose_response(data['dose']), use_container_width=True)
        with col2: st.plotly_chart(plot_inter_assay_comparison(data['hplc']), use_container_width=True)
    with tab2:
        st.subheader("96-Well Plate Analysis")
        st.plotly_chart(plot_plate_heatmap(data['plate'], "Screening Plate #SP-103 - Cell Viability"), use_container_width=True)
        st.info("💡 **SME Insight:** The heatmap reveals a potential 'edge effect,' where wells on the outer edges show lower values. This is a common experimental artifact that may warrant investigation or data normalization.")
    with tab3:
        st.subheader("Pending Action Items")
        tasks_df = pd.DataFrame([
            {"Type": "Discrepancy", "ID": "SMP-1005", "Details": "Negative concentration value", "Due": "2024-05-21"},
            {"Type": "E-Signature", "ID": "RPT-112", "Details": "IND Study Report v2", "Due": "2024-05-22"},
        ])
        st.dataframe(tasks_df, use_container_width=True, hide_index=True)

# --- QC ANALYST VIEW ---
elif user_role == 'QC Analyst':
    st.markdown("##### Control room for process stability, instrument performance, and data integrity triage.")
    
    tab1, tab2 = st.tabs(["🚨 Triage & Instrument Monitoring", "🔧 Cross-Instrument Performance"])
    with tab1:
        col1, col2 = st.columns((4,6))
        with col1:
            st.subheader("Discrepancy Triage Queue")
            discrepancies = data['hplc'][~data['hplc']['analyte_concentration'].between(0, 150) | data['hplc']['peak_area'].isnull()].copy().head()
            discrepancies['Status'] = 'Open'
            st.data_editor(discrepancies[['sample_id', 'instrument_id', 'analyte_concentration', 'Status']], use_container_width=True, hide_index=True)
        with col2:
            st.subheader("Live Instrument Monitoring")
            instrument_id = st.selectbox("Select Instrument for QC Monitoring", options=data['hplc']['instrument_id'].unique())
            instrument_data = data['hplc'][data['hplc']['instrument_id'] == instrument_id]
            st.plotly_chart(plot_levey_jennings(instrument_data), use_container_width=True)
    with tab2:
        st.subheader("Cross-Instrument Performance Analysis")
        st.info("💡 **SME Insight:** Use ANOVA (Analysis of Variance) to statistically determine if there are significant differences between instrument measurement populations. A low p-value (< 0.05) suggests that at least one instrument performs differently from the others.")
        st.plotly_chart(plot_anova_results(data['hplc'], 'retention_time', 'instrument_id'), use_container_width=True)

display_compliance_footer()
