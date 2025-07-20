# pages/4_Governance_&_Audit.py
import streamlit as st
import pandas as pd

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth
from utils.plotters import render_lineage_timeline

# --- Page Configuration ---
st.set_page_config(
    page_title="Governance & Audit Hub",
    page_icon="⚖️",
    layout="wide"
)

# --- Authentication and Data Loading ---
user_role = auth.authenticate_user()
db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
audit_df = dc.fetch_audit_log(db_connection)

# --- Page Header ---
st.title("⚖️ Governance & Audit Hub")
st.markdown("Central hub for 21 CFR Part 11 compliance, data lineage, and system audit trails.")

# --- Main Tabs ---
tab1, tab2 = st.tabs(["🔍 **Audit Trail Explorer**", "🧬 **Data Lineage Tracer**"])

with tab1:
    st.subheader("Interactive Audit Trail Explorer")
    st.info("Search, filter, and export the immutable, 21 CFR Part 11-compliant audit trail for all system activities.")
    
    # --- Powerful Filtering UI for Auditors ---
    with st.expander("Show Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            users_to_filter = st.multiselect(
                "Filter by User:", 
                options=sorted(audit_df['User'].unique()),
                help="Select one or more users to narrow the audit trail."
            )
        with col2:
            actions_to_filter = st.multiselect(
                "Filter by Action:", 
                options=sorted(audit_df['Action'].unique()),
                help="Select one or more action types."
            )
        with col3:
            record_id_filter = st.text_input(
                "Filter by Record ID (contains):",
                help="Enter a partial or full Record ID, e.g., 'SMP-10' or 'DEV-001'."
            )
    
    # --- Apply Filters ---
    filtered_df = audit_df.copy()
    if users_to_filter:
        filtered_df = filtered_df[filtered_df['User'].isin(users_to_filter)]
    if actions_to_filter:
        filtered_df = filtered_df[filtered_df['Action'].isin(actions_to_filter)]
    if record_id_filter:
        filtered_df = filtered_df[filtered_df['Record ID'].str.contains(record_id_filter, case=False, na=False)]
        
    st.metric("Total Records Found", f"{len(filtered_df)} / {len(audit_df)}")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # --- Export Functionality ---
    st.download_button(
        label="Export Filtered Results to CSV", 
        data=filtered_df.to_csv(index=False).encode('utf-8'), 
        file_name=f"VERITAS_Audit_Export_{datetime.now().strftime('%Y%m%d')}.csv", 
        mime="text/csv",
        help="Download the currently displayed audit trail data as a CSV file."
    )

with tab2:
    st.subheader("Visual Data Lineage Tracer")
    st.info("Trace the complete history of any data record from creation to its current state using a professional vertical timeline.")

    with st.expander("ℹ️ SME Insight: How to Read a Lineage Timeline"):
        st.info("""
            This timeline provides a clear, chronological history of a single data record.
            - **Icons:** Each icon represents a specific type of event (e.g., 👤 for login, 📄 for report generation).
            - **Chronological Order:** Events are listed from oldest at the top to newest at the bottom.
            - **Details on Demand:** Click "Show Details" to view the GxP-required information for that specific event.
            - **Purpose:** This visualization is designed for maximum clarity and is ideal for audit reviews and data integrity investigations.
        """)

    # Use a selectbox for a better user experience, preventing searches for non-existent IDs
    valid_ids = sorted(audit_df['Record ID'].unique().tolist())
    # Find a record ID with many events to serve as a good default example
    good_example_id = audit_df['Record ID'].value_counts().idxmax()
    default_index = valid_ids.index(good_example_id) if good_example_id in valid_ids else 0

    record_id = st.selectbox(
        "Select a Record ID to Trace", 
        options=valid_ids,
        index=default_index,
    )
    
    if record_id:
        with st.spinner(f"Rendering lineage for {record_id}..."):
            # Call the custom renderer from the plotters module
            render_lineage_timeline(audit_df, record_id)

# --- Global Compliance Footer ---
auth.display_compliance_footer()
