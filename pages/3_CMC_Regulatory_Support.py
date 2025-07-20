# pages/3_Regulatory_Support.py
import streamlit as st
import pandas as pd

# Import from the new, centralized backend modules
from utils.data_connector import write_to_audit_log
from utils.report_generator import generate_pdf_report, generate_ppt_report
from utils.plotters import plot_spc_chart

def render_page():
    """
    Renders the consolidated Regulatory Support page for generating reports.
    """
    st.title("📄 Regulatory Support & Report Assembler")
    st.markdown("Compile data summaries and generate formatted PDF or PowerPoint reports for submissions.")

    # --- Load data and config from session state ---
    hplc_df = st.session_state.get('hplc_df', pd.DataFrame())
    app_config = st.session_state.get('app_config', {})
    db_connection = st.session_state.get('db_connection')
    username = st.session_state.get('username', 'Unknown User')

    if hplc_df.empty or not app_config or not db_connection:
        st.warning("Data not loaded. Please return to the main Command Center.")
        return

    # --- UI for Report Configuration ---
    st.subheader("1. Select Data & Format")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        study_id = st.selectbox(
            "Select a Study:",
            options=sorted(hplc_df['study_id'].unique())
        )
    with col2:
        available_cqas = app_config.get('process_capability', {}).get('available_cqas', [])
        cqa = st.selectbox(
            "Select Primary CQA for Analysis:",
            options=available_cqas
        )
    with col3:
        report_format = st.radio(
            "Select Report Format:",
            options=['PDF', 'PowerPoint'],
            horizontal=True
        )

    # Filter data based on selection
    report_df = hplc_df[hplc_df['study_id'] == study_id]

    st.subheader("2. Add Commentary")
    commentary = st.text_area(
        "Enter Analyst Commentary (will be included in the report):",
        f"The data from study {study_id} demonstrates consistent process performance. The selected CQA, {cqa}, remained well within the established specification limits throughout the analysis.",
        height=120
    )

    st.subheader("3. Generate Report")
    
    if st.button(f"Generate {report_format} Report", type="primary"):
        with st.spinner(f"Generating {report_format} report..."):
            file_bytes = None
            if report_format == 'PDF':
                pdf_data = {
                    "study_id": study_id,
                    "cqa": cqa,
                    "data": report_df,
                    "commentary": commentary
                }
                file_bytes = generate_pdf_report(pdf_data)
                st.session_state['report_filename'] = f"VERITAS_Summary_{study_id}_{cqa}.pdf"
                st.session_state['report_mime'] = "application/pdf"
            
            elif report_format == 'PowerPoint':
                # For PPTX, we generate a plot to include
                plot_to_include = plot_spc_chart(report_df, cqa)
                file_bytes = generate_ppt_report(report_df, f"{study_id} Summary", plot_to_include)
                st.session_state['report_filename'] = f"VERITAS_PPT_{study_id}_{cqa}.pptx"
                st.session_state['report_mime'] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            
            st.session_state['report_bytes'] = file_bytes
            
            # Audit Log Entry
            write_to_audit_log(
                db_connection,
                user=username,
                action="Report Generated",
                details=f"Generated {report_format} summary for Study: {study_id}, CQA: {cqa}",
                record_id=study_id
            )
        
        st.success(f"{report_format} report generated successfully!")

    # --- Download Button (appears after generation) ---
    if 'report_bytes' in st.session_state and 'report_filename' in st.session_state:
        st.download_button(
            label=f"⬇️ Download {st.session_state['report_filename']}",
            data=st.session_state['report_bytes'],
            file_name=st.session_state['report_filename'],
            mime=st.session_state['report_mime']
        )


# --- This check ensures the page is run correctly from the main app ---
if __name__ == "__main__":
    st.error("This page should be run from the main VERITAS Command Center app.")
