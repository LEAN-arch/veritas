# pages/3_CMC_Regulatory_Support.py
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth
from utils.plotters import plot_process_capability # We can reuse plots here

# --- PHASE 3: PDF Report Generation ---
# SME EXPLANATION: This is a critical "last mile" feature for a reporting solutions tool.
# It transforms on-screen data into a formal, distributable artifact. We use the FPDF2 library,
# which is a pure-Python solution that does not require any external dependencies like LaTeX.

class PDF(FPDF):
    """Custom PDF class to handle headers, footers, and content generation."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'VERITAS - CMC Data Summary Report', 0, 1, 'C')
        self.set_font('Arial', '', 8)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        self.set_x(-50)
        self.cell(0, 10, 'CONFIDENTIAL', 0, 0, 'R')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

    def add_dataframe(self, df):
        self.set_font('Arial', 'B', 9)
        # Header
        for col in df.columns:
            self.cell(38, 7, col, 1, 0, 'C')
        self.ln()
        # Data
        self.set_font('Arial', '', 9)
        for index, row in df.iterrows():
            for col in df.columns:
                self.cell(38, 6, str(row[col]), 1, 0, 'L')
            self.ln()
        self.ln(5)

def generate_pdf_report(report_data: dict) -> bytes:
    """Creates a formatted PDF report from the provided data."""
    pdf = PDF()
    pdf.add_page()
    
    # Section 1: Report Metadata
    pdf.chapter_title(f"1.0 Summary for Study: {report_data['study_id']}")
    metadata_body = (
        f"This document summarizes key data for the selected study, generated from the VERITAS system. "
        f"The data is intended for regulatory support and internal review.\n\n"
        f"**Selected Critical Quality Attribute (CQA):** {report_data['cqa']}\n"
        f"**Number of Data Points Included:** {len(report_data['data'])}"
    )
    pdf.chapter_body(metadata_body)

    # Section 2: Summary Statistics
    pdf.chapter_title("2.0 Summary Statistics")
    summary_stats = report_data['data'][[report_data['cqa']]].describe().round(3).reset_index()
    pdf.add_dataframe(summary_stats)

    # Section 3: Analyst Commentary
    pdf.chapter_title("3.0 Analyst Commentary")
    pdf.chapter_body(report_data['commentary'])
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


# --- Page Configuration ---
st.set_page_config(
    page_title="CMC Regulatory Support",
    page_icon="📄",
    layout="wide"
)

# --- Authentication and Data Loading ---
user_role = auth.authenticate_user()
db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
hplc_df = dc.fetch_hplc_data(db_connection)

# --- Page Header ---
st.title("📄 CMC Regulatory Support Tool")
st.markdown("Compile data summaries and generate formatted PDF reports for submissions.")

# --- UI for Report Configuration ---
st.subheader("1. Select Data for Report")
col1, col2 = st.columns(2)
with col1:
    study_id = st.selectbox(
        "Select a Study:",
        options=hplc_df['study_id'].unique()
    )
with col2:
    cqa = st.selectbox(
        "Select Primary CQA:",
        options=['Purity', 'Aggregate Content', 'Main Impurity', 'Bio-activity']
    )

# Filter data based on selection
report_df = hplc_df[hplc_df['study_id'] == study_id]

st.subheader("2. Add Commentary")
commentary = st.text_area(
    "Enter Analyst Commentary (will be included in the PDF):",
    "The data from this study demonstrates consistent process performance. The selected CQA remained well within the established specification limits throughout the analysis. No adverse trends were observed.",
    height=150
)

st.subheader("3. Generate Report")
st.info("Click the button below to compile the selected data and commentary into a formal PDF document.")

if st.button("Generate PDF Summary", type="primary"):
    report_data = {
        "study_id": study_id,
        "cqa": cqa,
        "data": report_df,
        "commentary": commentary
    }
    
    with st.spinner("Generating PDF..."):
        pdf_bytes = generate_pdf_report(report_data)
        st.session_state['pdf_bytes'] = pdf_bytes
        
        # Audit Log Entry
        dc.write_to_audit_log(
            db_connection,
            user=st.session_state.username,
            action="Report Generated",
            details=f"Generated PDF summary for Study: {study_id}, CQA: {cqa}"
        )
    
    st.success("PDF report generated successfully!")

# --- Download Button (appears after generation) ---
if 'pdf_bytes' in st.session_state:
    st.download_button(
        label="⬇️ Download PDF Report",
        data=st.session_state['pdf_bytes'],
        file_name=f"VERITAS_Summary_{study_id}_{cqa}.pdf",
        mime="application/pdf"
    )

# --- Global Compliance Footer ---
auth.display_compliance_footer()
