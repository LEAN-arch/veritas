# pages/4_Compliance_&_Audit_Hub.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_audit_trail
from utils.plotters import render_lineage_timeline # <-- IMPORT THE NEW RENDERER

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
    st.info("Trace the complete history of any data record from ingestion to final state using a professional vertical timeline.")

    with st.expander("ℹ️ SME Insight: How to Read a Lineage Timeline"):
        st.info("""
            This timeline provides a clear, chronological history of a single data record.
            - **Icons:** Each icon represents a specific type of event (e.g., 📥 for ingestion, ✍️ for signature).
            - **Chronological Order:** Events are listed from oldest at the top to newest at the bottom.
            - **Details on Demand:** Click "Show Details" to view the GxP-required information for that specific event, including what changed and why.
            - **Purpose:** This visualization is designed for maximum clarity and is ideal for audit reviews and data integrity investigations.
        """)

    valid_ids = sorted(audit_df['Record ID'].unique().tolist())
    good_example_id = audit_df['Record ID'].value_counts().idxmax()
    default_index = valid_ids.index(good_example_id) if good_example_id in valid_ids else 0

    record_id = st.selectbox(
        "Select a Record ID to Trace", 
        options=valid_ids,
        index=default_index,
    )
    
    if record_id:
        # --- CALL THE NEW, PROFESSIONAL RENDERER INSTEAD OF A PLOT ---
        render_lineage_timeline(audit_df, record_id)
            
with tab3:
    st.subheader("Electronic Signature Log")
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
