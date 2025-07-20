# pages/4_Compliance_&_Audit_Hub.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_audit_trail
from utils.plotters import plot_audit_timeline

# --- Page Configuration and Sidebar ---
st.set_page_config(layout="wide", page_title="Compliance Hub", page_icon="🧪")
with st.sidebar:
    st.title("VERITAS")
    get_user_role()

# --- Page Header and Introduction ---
st.title("Module 4: Compliance & Audit Hub")
st.markdown("The central source for all audit trails, data lineage, and compliance documentation, ensuring constant inspection readiness.")

# --- Data Loading ---
@st.cache_data
def load_audit_data():
    """Loads a large, comprehensive audit trail dataset, cached for performance."""
    return create_mock_audit_trail(250)
audit_df = load_audit_data()

# --- Main Tabs for different compliance views ---
tab1, tab2, tab3 = st.tabs(["🔍 **Audit Trail Explorer**", "🧬 **Data Lineage Tracer**", "✍️ **E-Signature Log**"])

with tab1:
    st.subheader("Interactive Audit Trail Explorer")
    st.info("Search, filter, and export the immutable, 21 CFR Part 11-compliant audit trail for all system activities.")
    
    # --- Powerful Filtering UI for Auditors ---
    with st.expander("Show Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            users_to_filter = st.multiselect(
                "Filter by User:", 
                options=audit_df['User'].unique(),
                help="Select one or more users to narrow the audit trail."
            )
        with col2:
            actions_to_filter = st.multiselect(
                "Filter by Action:", 
                options=audit_df['Action'].unique(),
                help="Select one or more action types."
            )
        with col3:
            record_id_filter = st.text_input(
                "Filter by Record ID (contains):",
                help="Enter a partial or full Record ID, e.g., 'SMP-10' or 'RPT-112'."
            )
    
    # --- Apply Filters to the DataFrame ---
    filtered_df = audit_df.copy()
    if users_to_filter:
        filtered_df = filtered_df[filtered_df['User'].isin(users_to_filter)]
    if actions_to_filter:
        filtered_df = filtered_df[filtered_df['Action'].isin(actions_to_filter)]
    if record_id_filter:
        filtered_df = filtered_df[filtered_df['Record ID'].str.contains(record_id_filter, case=False, na=False)]
        
    # --- Display Filtered Results ---
    st.metric("Total Records Found", len(filtered_df))
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # --- Export Functionality ---
    st.download_button(
        "Export Filtered Results to CSV", 
        filtered_df.to_csv(index=False).encode('utf-8'), 
        "audit_export.csv", 
        "text/csv",
        help="Download the currently displayed audit trail data as a CSV file."
    )

with tab2:
    st.subheader("Visual Data Lineage Tracer")
    st.info("Trace the complete history of any data record, from ingestion through QC and transformation to final reporting.")
    
    # --- ENHANCED: Find a good example record to ensure the chart is populated on first view ---
    # Find the Record ID with the most audit entries to use as a robust default example.
    good_example_id = audit_df['Record ID'].mode()[0]
    
    record_id = st.text_input(
        "Enter Record ID to Trace", 
        value=good_example_id, # Use the dynamically found good example as the default
        help=f"Example: {good_example_id}"
    )
    if record_id:
        with st.spinner(f"Generating lineage for {record_id}..."):
            lineage_fig = plot_audit_timeline(audit_df, record_id)
            st.plotly_chart(lineage_fig, use_container_width=True)
            
with tab3:
    st.subheader("Electronic Signature Log")
    st.info("An immutable log of all electronic signatures applied to documents and records within VERITAS, as required by 21 CFR Part 11.")
    
    # Mock data for signature status, representing a query to a secure log table
    sig_data = {
        'Document Name': ['IND Study Report', 'PK Analysis Summary', 'Tox_Assay_Run_05_Report', 'Method Validation M-101'],
        'Version': ['v2.0', 'v1.1', 'v1.0', 'v3.2'],
        'Status': ['Approved', 'Approved', 'Rejected', 'Approved'],
        'Signer': ['S. Director', 'A. Turing', 'M. Curie', 'QA.Bot'],
        'Timestamp': [datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2, hours=4), datetime.now() - timedelta(days=3)],
        'Meaning of Signature': ['Author Approval', 'Scientific Review', 'Data Inaccurate', 'QA Approval']
    }
    sig_df = pd.DataFrame(sig_data)
    st.dataframe(sig_df, use_container_width=True, hide_index=True)
    
# --- Global Compliance Footer ---
display_compliance_footer()
