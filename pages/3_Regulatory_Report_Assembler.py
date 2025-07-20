# pages/3_Regulatory_Report_Assembler.py
import streamlit as st
import time
from utils.auth import display_compliance_footer, get_user_role
from utils.plotters import plot_spc_chart
from utils.data_generator import create_mock_hplc_data

st.set_page_config(layout="wide", page_title="Report Assembler")
get_user_role()
st.title("Module 3: Regulatory Package & Report Assembler")
st.markdown("Automate the generation of study reports and data packages from the Single Source of Truth.")

# --- Configuration ---
st.subheader("1. Report Configuration")
col1, col2 = st.columns(2)
with col1:
    report_template = st.selectbox(
        "Select Report Template", 
        ("IND Study Report", "PK Analysis Summary", "Response to Agency Query")
    )
with col2:
    data_package = st.selectbox(
        "Select Approved QC'd Data Package",
        ("PK_Study_2024-A (v2.1)", "Tox_Assay_Run_05 (v1.0)")
    )
    
# --- Generation ---
if st.button("Assemble Report"):
    st.subheader("2. Report Generation and Preview")
    
    with st.spinner("Assembling report... Please wait."):
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        time.sleep(1)
        my_bar.progress(25, text="Pulling QC'd data from SSOT...")
        time.sleep(2)
        my_bar.progress(50, text="Generating dynamic plots and statistical summaries...")
        df = create_mock_hplc_data(50) # Load data for plots
        fig = plot_spc_chart(df)
        
        time.sleep(2)
        my_bar.progress(80, text="Populating report template (IND Study Report)...")
        time.sleep(1)
        my_bar.progress(100, text="Report Assembled. Awaiting E-Signature.")

    st.success("Report generation complete!")
    
    with st.container(border=True):
        st.markdown(f"### Preview: {report_template} - {data_package}")
        st.markdown("**Section 3.1: Assay Performance**")
        st.write("The assay demonstrated high precision and accuracy within the validated range. All system suitability tests passed. The following SPC chart shows the process was in a state of statistical control during the run.")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Section 4.2: Results Table**")
        st.dataframe(df.head(10))

    # --- Finalization and Download ---
    st.subheader("3. Finalize and Distribute")
    st.info("This report has been sent for electronic signature. Once approved, it will be available for download.")
    
    # Simulate an approved report download
    report_content = "This is a simulated PDF report content."
    st.download_button(
        label="Download Submission-Ready PDF (Simulated)",
        data=report_content,
        file_name=f"{report_template.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

display_compliance_footer()
