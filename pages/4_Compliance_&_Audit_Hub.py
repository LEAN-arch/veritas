# pages/4_Compliance_&_Audit_Hub.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_audit_trail
from utils.plotters import plot_data_lineage_sankey # <-- IMPORT THE NEW FUNCTION

st.set_page_config(layout="wide", page_title="Compliance Hub", page_icon="🧪")
with st.sidebar:
    st.title("VERITAS")
    get_user_role()

st.title("Module 4: Compliance & Audit Hub")
st.markdown("The central source for all audit trails, data lineage, and compliance documentation, ensuring constant inspection readiness.")

@st.cache_data
def load_audit_data():
    return create_mock_audit_trail(250)
audit_df = load_audit_data()

tab1, tab2, tab3 = st.tabs(["🔍 **Audit Trail Explorer**", "🧬 **Data Lineage Tracer**", "✍️ **E-Signature Log**"])

with tab1:
    st.subheader("Interactive Audit Trail Explorer")
    # ... (This tab's code remains the same as it is already functional)
    st.info("Search, filter, and export the immutable, 21 CFR Part 11-compliant audit trail for all system activities.")
    with st.expander("Show Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1: users_to_filter = st.multiselect("Filter by User:", options=audit_df['User'].unique())
        with col2: actions_to_filter = st.multiselect("Filter by Action:", options=audit_df['Action'].unique())
        with col3: record_id_filter = st.text_input("Filter by Record ID (contains):")
    
    filtered_df = audit_df.copy()
    if users_to_filter: filtered_df = filtered_df[filtered_df['User'].isin(users_to_filter)]
    if actions_to_filter: filtered_df = filtered_df[filtered_df['Action'].isin(actions_to_filter)]
    if record_id_filter: filtered_df = filtered_df[filtered_df['Record ID'].str.contains(record_id_filter, case=False, na=False)]
        
    st.metric("Total Records Found", len(filtered_df))
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    st.download_button("Export Filtered Results to CSV", filtered_df.to_csv(index=False).encode('utf-8'), "audit_export.csv", "text/csv")


with tab2:
    st.subheader("Visual Data Lineage Tracer")
    st.info("Trace the complete history of any data record from ingestion to final state using a Sankey flow diagram.")

    with st.expander("ℹ️ SME Insight: How to Read a Lineage Diagram"):
        st.info("""
            This Sankey diagram shows the lifecycle of a single data record.
            - **Nodes (vertical bars):** Represent a specific **Action** performed by a **User**.
            - **Links (horizontal flows):** Represent the chronological sequence of events. The flow moves from left to right, showing how the record transitioned from one state to the next.
            - **Purpose:** This visualization provides an immediate, intuitive understanding of a record's history, making it easy for auditors to verify data integrity and traceability.
        """)
    
    valid_ids = sorted(audit_df['Record ID'].unique().tolist())
    good_example_id = audit_df['Record ID'].value_counts().idxmax() # Find ID with most events
    default_index = valid_ids.index(good_example_id) if good_example_id in valid_ids else 0

    record_id = st.selectbox(
        "Select a Record ID to Trace", 
        options=valid_ids,
        index=default_index,
    )
    
    if record_id:
        with st.spinner(f"Generating lineage for {record_id}..."):
            # --- USE THE NEW, CORRECTED PLOTTING FUNCTION ---
            lineage_fig = plot_data_lineage_sankey(audit_df, record_id)
            
            if lineage_fig is not None:
                st.plotly_chart(lineage_fig, use_container_width=True)
            else:
                st.warning(f"Lineage trace requires at least two events. Only one event was found for Record ID: **{record_id}**.")
            
with tab3:
    st.subheader("Electronic Signature Log")
    # ... (This tab's code remains the same as it is already functional)
    st.info("An immutable log of all electronic signatures applied to documents and records within VERITAS, as required by 21 CFR Part 11.")
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
    
display_compliance_footer()
