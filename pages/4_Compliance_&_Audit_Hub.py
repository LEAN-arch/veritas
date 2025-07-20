# pages/4_Compliance_&_Audit_Hub.py
import streamlit as st
import pandas as pd  # <-- ADDED
from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_audit_trail
from utils.plotters import plot_data_lineage

st.set_page_config(layout="wide", page_title="Compliance Hub")
get_user_role()
st.title("Module 5: Compliance & Audit Hub")
st.markdown("Ensuring constant inspection readiness with immutable logs, data lineage, and e-signature tracking.")

tab1, tab2, tab3 = st.tabs(["Data Lineage Viewer", "21 CFR Part 11 Audit Trail", "E-Signature Status"])

with tab1:
    st.header("Data Lineage Viewer")
    st.info("Trace any data point from raw file to final report, ensuring full traceability.")
    
    record_id = st.text_input("Enter Record ID to Trace Lineage", value="SMP-1005")
    if record_id:
        st.plotly_chart(plot_data_lineage(), use_container_width=True)

with tab2:
    st.header("Immutable Audit Trail")
    st.warning("All actions on GxP-relevant data are logged below. This log is secure and cannot be altered.")
    
    # Load and display the audit trail
    audit_df = create_mock_audit_trail()
    
    # Add filtering
    search_query = st.text_input("Search Audit Log (by User, Action, or Record ID)")
    if search_query:
        filtered_df = audit_df[
            audit_df['User'].str.contains(search_query, case=False) |
            audit_df['Action'].str.contains(search_query, case=False) |
            audit_df['Record ID'].str.contains(search_query, case=False)
        ]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(audit_df, use_container_width=True)

with tab3:
    st.header("Electronic Signature Status")
    st.markdown("Track the review and approval status of critical documents.")
    
    # Mock data for signature status
    sig_data = {
        'Document Name': ['IND Study Report', 'PK Analysis Summary', 'Tox_Assay_Run_05_Report'],
        'Version': ['v1.0', 'v2.1', 'v1.3'],
        'Status': ['Pending QA Signature', 'Approved', 'Pending Study Director Review'],
        'Last Action By': ['A. Turing (Scientist)', 'QA.Bot', 'M. Curie (Scientist)'],
        'Timestamp': ['2024-05-10 11:00 UTC', '2024-05-09 15:30 UTC', '2024-05-10 14:00 UTC']
    }
    sig_df = pd.DataFrame(sig_data)
    st.dataframe(sig_df, use_container_width=True, hide_index=True)

display_compliance_footer()
