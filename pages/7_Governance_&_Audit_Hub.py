# pages/7_governance_and_audit_hub.py
import streamlit as st
import pandas as pd
from datetime import datetime

# Import from the centralized backend modules
from utils import ui_components, auth

# Set the page configuration for this specific page
st.set_page_config(page_title="Governance & Audit", page_icon="⚖️", layout="wide")

st.title("⚖️ Governance & Audit Hub")
st.markdown("Central hub for 21 CFR Part 11 compliance, data lineage, and system audit trails.")

# --- Load data from session state ---
audit_df = st.session_state.get('audit_df', pd.DataFrame())

# Stop execution if the main app hasn't initialized the session properly
if audit_df.empty:
    st.warning("Session not initialized. Please start from the main VERITAS Command Center.")
    st.stop()

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["🔍 **Audit Trail Explorer**", "🧬 **Data Lineage Tracer**", "✍️ **E-Signature Log**"])

with tab1:
    st.subheader("Interactive Audit Trail Explorer")
    st.info("Search, filter, and export the immutable, 21 CFR Part 11-compliant audit trail for all system activities.")
    
    with st.expander("Show Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            users_to_filter = st.multiselect("Filter by User:", options=sorted(audit_df['User'].unique()))
        with col2:
            actions_to_filter = st.multiselect("Filter by Action:", options=sorted(audit_df['Action'].unique()))
        with col3:
            record_id_filter = st.text_input("Filter by Record ID (contains):")
    
    # Apply Filters
    filtered_df = audit_df.copy()
    if users_to_filter:
        filtered_df = filtered_df[filtered_df['User'].isin(users_to_filter)]
    if actions_to_filter:
        filtered_df = filtered_df[filtered_df['Action'].isin(actions_to_filter)]
    if record_id_filter:
        filtered_df = filtered_df[filtered_df['Record ID'].str.contains(record_id_filter, case=False, na=False)]
        
    st.metric("Total Records Found", f"{len(filtered_df)} / {len(audit_df)}")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.download_button(
        "Export Filtered Results to CSV", 
        filtered_df.to_csv(index=False).encode('utf-8'), 
        f"VERITAS_Audit_Export_{datetime.now().strftime('%Y%m%d')}.csv", 
        "text/csv"
    )

with tab2:
    st.subheader("Visual Data Lineage Tracer")
    st.info("Trace the complete history of any data record from creation to final state.")
    
    # Use a selectbox for a better user experience
    valid_ids = sorted([str(i) for i in audit_df['Record ID'].unique() if i and i != 'N/A'])
    
    # Find a good default example with many events
    if not audit_df.empty:
        good_example_id = audit_df['Record ID'].value_counts().idxmax()
        default_index = valid_ids.index(good_example_id) if good_example_id in valid_ids else 0
    else:
        default_index = 0

    record_id = st.selectbox(
        "Select a Record ID to Trace", 
        options=valid_ids,
        index=default_index,
    )
    
    if record_id:
        # Call the custom renderer from the ui_components module
        ui_components.render_lineage_timeline(audit_df, record_id)
        
with tab3:
    st.subheader("Electronic Signature Log")
    st.info("A live, filtered view of all electronic signature events recorded in the audit trail.")
    
    # --- DYNAMIC E-SIGNATURE LOG ---
    # This is now a live, filtered view of the main audit trail, not a static table.
    sig_keywords = ['Signature', 'Signed', 'E-Sign']
    sig_mask = audit_df['Action'].str.contains('|'.join(sig_keywords), case=False, na=False)
    
    sig_df = audit_df[sig_mask]
    
    if not sig_df.empty:
        st.dataframe(sig_df[['Timestamp', 'User', 'Action', 'Record ID', 'Details']], use_container_width=True, hide_index=True)
    else:
        st.success("No electronic signature events have been recorded in the audit trail yet.")

# Add the compliance footer
auth.display_compliance_footer()
