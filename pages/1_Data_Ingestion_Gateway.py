# pages/1_Data_Ingestion_Gateway.py
import streamlit as st
import time, pandas as pd, numpy as np
from datetime import datetime
from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import get_ingestion_history
from utils.plotters import plot_ingestion_trend, plot_ingestion_volume

st.set_page_config(layout="wide", page_title="Data Ingestion Gateway")
with st.sidebar:
    st.image("vertex-logo.png", width=200)
    st.title("VERITAS")
get_user_role()
st.title("Module 1: Data Ingestion & Harmonization Gateway")
st.markdown("Secure, automated entry point for all pre-clinical raw data files with real-time and historical monitoring.")

with st.expander("ℹ️ SME Overview: The Importance of a Data Gateway", expanded=False):
    st.info("""
        - **Purpose:** To establish a single, GxP-compliant "front door" for all raw data. This eliminates manual data handling, which is a primary source of errors and compliance risks.
        - **Functionality:** It automates the parsing of diverse file formats, validates data against pre-defined schemas, checks for file integrity (checksums), and enriches data with critical metadata (e.g., timestamp, source).
        - **Commercial Significance:** A robust gateway is the foundation of data integrity. It ensures that all data entering the ecosystem is clean, standardized, and traceable, which is a prerequisite for reliable analytics, ML, and regulatory submissions.
    """)

st.subheader("📈 Historical Ingestion Performance (Last 30 Days)")
hist_df = get_ingestion_history()
col1, col2 = st.columns(2)
with col1: st.plotly_chart(plot_ingestion_trend(hist_df), use_container_width=True)
with col2: st.plotly_chart(plot_ingestion_volume(hist_df), use_container_width=True)

st.markdown("---")
st.subheader("⚡ Live Data Ingestion Workflow")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("#### Step 1: Upload Files")
    uploaded_files = st.file_uploader("Select one or more raw data files", accept_multiple_files=True)
    st.markdown("#### Step 2: GxP Compliance")
    st.text_input("E-Signature (Your Name)", help="Required for all data entry actions per 21 CFR Part 11.")
    st.selectbox("Justification for Upload", ["Routine data upload", "Re-analysis", "Method validation"])

with col2:
    st.markdown("#### Step 3: Automated Validation & Results")
    if uploaded_files:
        if st.button("Begin Secure Ingestion", type="primary"):
            results = []
            st.info("Ingestion process started...")
            progress_bar = st.progress(0, text="Initializing...")
            
            for i, file in enumerate(uploaded_files):
                # ... (rest of the ingestion simulation logic)
                status = "Success" if np.random.rand() > 0.1 else "Failed"
                reason = "All checks passed" if status == "Success" else "Schema Mismatch"
                results.append({"Filename": file.name, "Status": status, "Details": reason, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processing {file.name}...")
            
            st.success("Ingestion workflow complete.")
            st.dataframe(pd.DataFrame(results))
    else:
        st.info("Upload files and provide your e-signature to start the ingestion process.")

display_compliance_footer()
