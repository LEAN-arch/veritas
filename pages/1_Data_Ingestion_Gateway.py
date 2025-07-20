# pages/1_data_ingestion_gateway.py
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Import from the new, centralized backend and UI modules
from utils import plotters, data_connector as dc

# THE FIX: All code is now at the top level of the script.
# The `def render_page():` wrapper has been removed.

st.set_page_config(page_title="Ingestion Gateway", page_icon="📥", layout="wide")

st.title("📥 Data Ingestion & Harmonization Gateway")
st.markdown("Secure, automated entry point for all raw data files with real-time and historical monitoring.")

# --- Load data and config from session state ---
db_connection = st.session_state.get('db_connection')
username = st.session_state.get('username', 'Unknown User')
ingestion_history_df = st.session_state.get('ingestion_history_df', pd.DataFrame())

if not db_connection:
    st.warning("Database connection not found. Please return to the main Command Center and restart the session.")
    st.stop()

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
                status = "Success" if np.random.rand() > 0.1 else "Failed"
                reason = "All checks passed" if status == "Success" else np.random.choice(["Schema Mismatch", "Header Corrupted", "Invalid File Type"])
                
                results.append({
                    "Filename": file.name, 
                    "Status": status, 
                    "Details": reason, 
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                dc.write_to_audit_log(
                    db_connection,
                    user=username,
                    action="File Ingested",
                    details=f"File '{file.name}' ingestion attempt. Status: {status}. Justification: {justification}.",
                    record_id=file.name
                )
                
                time.sleep(0.5)
                progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processing {file.name}...")
            
            st.success("Ingestion workflow complete.")
            st.dataframe(pd.DataFrame(results), hide_index=True)
        
        elif not e_signature:
             st.warning("Please provide your E-Signature to enable the ingestion button.")
    else:
        st.info("Upload files and provide your e-signature to start.")
