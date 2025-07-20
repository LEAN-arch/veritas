# pages/1_Data_Ingestion_Gateway.py
import streamlit as st
import time
import pandas as pd
import numpy as np
from datetime import datetime
from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import get_ingestion_history
from utils.plotters import plot_ingestion_trend, plot_ingestion_volume

st.set_page_config(layout="wide", page_title="Data Ingestion Gateway")
get_user_role()
st.title("Module 1: Data Ingestion & Harmonization Gateway")
st.markdown("Secure, automated entry point for all pre-clinical raw data files with real-time and historical monitoring.")

with st.expander("ℹ️ What is this Module For?", expanded=False):
    st.info("""
        This gateway is the single, GxP-compliant entry point for data into VERITAS.
        - **Purpose:** To automate the tedious and error-prone process of uploading, validating, and standardizing data from diverse lab instruments.
        - **Functionality:** It performs initial checks like file format validation, virus scanning, and metadata completeness before passing the data to the QC Engine.
        - **Significance:** Ensures a consistent and reliable starting point for all downstream analysis, preventing a "garbage in, garbage out" scenario.
    """)

# --- Historical Performance Dashboard ---
st.subheader("Historical Ingestion Performance (Last 30 Days)")
hist_df = get_ingestion_history()
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_ingestion_trend(hist_df), use_container_width=True)
with col2:
    st.plotly_chart(plot_ingestion_volume(hist_df), use_container_width=True)
st.markdown("---")

# --- File Uploader Functionality ---
st.subheader("Live Data Ingestion")
uploaded_files = st.file_uploader(
    "Drag and drop raw data files here (.csv, .txt, .mzML)",
    accept_multiple_files=True,
    type=['csv', 'txt', 'mzml']
)

if uploaded_files:
    if st.button("Begin Ingestion Process"):
        results = []
        st.info("Ingestion process started. All actions are logged per 21 CFR Part 11.")
        progress_bar = st.progress(0, text="Initializing...")
        
        for i, file in enumerate(uploaded_files):
            progress_text = f"Processing {file.name}: Validating schema... "
            progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)
            time.sleep(np.random.uniform(0.3, 0.8))
            
            # Simulate more detailed validation steps
            is_success = np.random.choice([True, False], p=[0.95, 0.05])
            if is_success:
                progress_text += "✅ | Running checksum... "
                progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)
                time.sleep(0.2)
                progress_text += "✅"
                status = "Success"
                reason = "All checks passed"
            else:
                progress_text += "❌"
                status = "Failed"
                reason = np.random.choice(["Schema Mismatch", "Header Corrupted", "Invalid File Type"])

            results.append({
                "Filename": file.name,
                "Status": status,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Checksum (SHA256)": f"0x{np.random.randint(1e10, 1e11):x}",
                "Details": reason
            })
            progress_bar.progress((i + 1) / len(uploaded_files), text=progress_text)
            
        st.success("Ingestion process complete!")
        st.dataframe(pd.DataFrame(results))
else:
    st.info("Upload one or more files to begin the automated ingestion and validation workflow.")

display_compliance_footer()
