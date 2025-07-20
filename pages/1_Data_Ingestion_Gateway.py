# pages/1_data_ingestion_gateway.py
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Import from the new, centralized backend and UI modules
from utils import plotters, qc_engine, data_connector as dc

def render_page():
    """
    Renders the Data Ingestion Gateway page.
    """
    st.title("📥 Data Ingestion & Harmonization Gateway")
    st.markdown("Secure, automated entry point for all raw data files with real-time and historical monitoring.")
    
    # --- Load data and config from session state ---
    db_connection = st.session_state.get('db_connection')
    username = st.session_state.get('username', 'Unknown User')
    # This data would need to be added to the mock_data_factory for a complete demo
    # For now, we simulate it here to demonstrate functionality.
    ingestion_history_df = pd.DataFrame({
        'Date': pd.to_datetime(pd.date_range(end=datetime.now(), periods=30, freq='D')),
        'Success Rate (%)': np.clip(95 + np.random.randn(30).cumsum() * 0.1, 90, 99.8),
        'Files Processed': np.random.randint(500, 800, 30)
    })

    with st.expander("ℹ️ SME Overview: The Importance of a Data Gateway"):
        st.info("""
            - **Purpose:** To establish a single, GxP-compliant "front door" for all raw data, eliminating manual data handling.
            - **Functionality:** Automates parsing, schema validation, integrity checks, and metadata enrichment.
            - **Value:** A robust gateway is the foundation of data integrity, ensuring all data is clean, standardized, and traceable for reliable analytics and submissions.
        """)

    # --- Historical Performance Dashboard ---
    st.subheader("📈 Historical Ingestion Performance (Last 30 Days)")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plotters.plot_ingestion_trend(ingestion_history_df), use_container_width=True)
    with col2:
        st.plotly_chart(plotters.plot_ingestion_volume(ingestion_history_df), use_container_width=True)

    st.markdown("---")

    # --- Live Ingestion Workflow ---
    st.subheader("⚡ Live Data Ingestion Workflow")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("#### Step 1: Upload Files")
        uploaded_files = st.file_uploader(
            "Select one or more raw data files", 
            accept_multiple_files=True,
            type=['csv', 'txt', 'xlsx']
        )
        
        st.markdown("#### Step 2: GxP Compliance")
        e_signature = st.text_input("E-Signature (Your Full Name)", help="Required for all data entry actions per 21 CFR Part 11.")
        justification = st.selectbox("Justification for Upload", ["Routine data upload", "Re-analysis of previous run", "Method validation study"])

    with col2:
        st.markdown("#### Step 3: Automated Validation & Results")
        if uploaded_files:
            if st.button("Begin Secure Ingestion", type="primary", disabled=(not e_signature)):
                results = []
                progress_bar = st.progress(0, text="Initializing...")
                
                for i, file in enumerate(uploaded_files):
                    # Simulate processing using a backend function (though simple here)
                    # A real implementation would be in qc_engine or a new actions.py
                    status = "Success" if np.random.rand() > 0.1 else "Failed"
                    reason = "All checks passed" if status == "Success" else np.random.choice(["Schema Mismatch", "Header Corrupted", "Invalid File Type"])
                    
                    results.append({
                        "Filename": file.name, 
                        "Status": status, 
                        "Details": reason, 
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Log the action
                    dc.write_to_audit_log(
                        db_connection,
                        user=username,
                        action="File Ingested",
                        details=f"File '{file.name}' ingestion attempt. Status: {status}. Justification: {justification}.",
                        record_id=file.name
                    )
                    
                    time.sleep(0.5) # Simulate work
                    progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processing {file.name}...")
                
                st.success("Ingestion workflow complete.")
                st.dataframe(pd.DataFrame(results), hide_index=True)
            
            elif not e_signature:
                 st.warning("Please provide your E-Signature to enable the ingestion button.")
        else:
            st.info("Upload files and provide your e-signature to start.")

# This check ensures the page is run correctly from the main app
if __name__ == "__main__":
    st.error("This page should be run from the main VERITAS Command Center app.")
