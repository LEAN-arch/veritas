# pages/1_Data_Ingestion_Gateway.py
import streamlit as st
import time
import pandas as pd
import numpy as np
from datetime import datetime
from utils.auth import display_compliance_footer, get_user_role

st.set_page_config(layout="wide", page_title="Data Ingestion Gateway")
get_user_role() # To show sidebar
st.title("Module 1: Data Ingestion & Harmonization Gateway")
st.markdown("Secure entry point for all pre-clinical raw data files.")

# --- KPIs & Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Today's Ingestion Success Rate", "98.2%", "1.5%")
col2.metric("Average Data Latency", "2.1 mins", "-0.2 mins")
col3.metric("Source with Most Errors", "HPLC-03", "Action Required")
st.markdown("---")

# --- File Uploader Functionality ---
uploaded_files = st.file_uploader(
    "Drag and drop raw data files here (.csv, .txt, .mzML)",
    accept_multiple_files=True,
    type=['csv', 'txt', 'mzml']
)

if uploaded_files:
    if st.button("Begin Ingestion Process"):
        results = []
        with st.spinner('Ingesting files... This includes schema validation and virus scanning.'):
            progress_bar = st.progress(0, text="Starting ingestion...")
            for i, file in enumerate(uploaded_files):
                time.sleep(np.random.uniform(0.5, 1.5))  # Simulate processing
                
                # Simulate validation
                is_success = np.random.choice([True, False], p=[0.95, 0.05])
                status = "Success" if is_success else "Failed"
                reason = "Schema Mismatch" if not is_success else "OK"
                
                results.append({
                    "Filename": file.name,
                    "Status": status,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Checksum (SHA256)": f"0x{np.random.randint(1e10, 1e11):x}",
                    "Reason": reason
                })
                progress_bar.progress((i + 1) / len(uploaded_files), text=f"Processing {file.name}...")
        
        st.success("Ingestion process complete!")
        
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)
        
        st.info("All ingestion actions have been logged in the Audit Hub.")

display_compliance_footer()
