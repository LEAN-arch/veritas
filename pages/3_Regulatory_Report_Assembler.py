# pages/3_Regulatory_Report_Assembler.py
import streamlit as st
import pandas as pd
import time
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from prophet import Prophet
from prophet.plot import plot_plotly

from utils.auth import display_compliance_footer, get_user_role
from utils.plotters import plot_spc_chart
from utils.data_generator import create_mock_hplc_data

# --- Helper function to add a pandas DataFrame as a table to a slide ---
def add_table_to_slide(slide, df, left, top, width, height):
    """Adds a pandas DataFrame as a table to a PowerPoint slide."""
    rows, cols = df.shape
    rows += 1 # Add a row for the header
    table = slide.shapes.add_table(rows, cols, left, top, width, height).table

    # Set column widths
    for i in range(cols):
        table.columns[i].width = Inches(width.inches / cols)

    # Write header
    for i, col_name in enumerate(df.columns):
        cell = table.cell(0, i)
        cell.text = col_name
        cell.text_frame.paragraphs[0].font.bold = True
        cell.text_frame.paragraphs[0].font.size = Pt(10)

    # Write data
    for r in range(rows - 1):
        for c in range(cols):
            cell = table.cell(r + 1, c)
            cell.text = str(df.iloc[r, c])
            cell.text_frame.paragraphs[0].font.size = Pt(9)

# --- Main function to create the report ---
def create_report_pptx(df, report_title, data_package_name):
    """
    Generates a complete PowerPoint report with titles, data, and plots.
    """
    prs = Presentation()
    
    # Slide 1: Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    title.text = "VERITAS Automated Report"
    subtitle.text = f"Report Type: {report_title}\nData Source: {data_package_name}\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}"

    # Slide 2: Summary and Data Table
    content_slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(content_slide_layout)
    title = slide.shapes.title
    title.text = "Data Summary"
    
    # Add a data table
    summary_df = df.head(10)[['sample_id', 'batch_id', 'analyte_concentration', 'retention_time']]
    add_table_to_slide(slide, summary_df, Inches(0.5), Inches(1.5), Inches(9.0), Inches(4.0))

    # Slide 3: Statistical Process Control (SPC) Chart
    slide = prs.slides.add_slide(content_slide_layout)
    title = slide.shapes.title
    title.text = "Process Stability Analysis (SPC)"
    
    # Generate and save SPC plot to memory
    spc_fig = plot_spc_chart(df, 'analyte_concentration')
    spc_img_stream = io.BytesIO()
    spc_fig.write_image(spc_img_stream, format="png", width=800, height=450, scale=2)
    spc_img_stream.seek(0)
    
    # Add image to slide
    slide.shapes.add_picture(spc_img_stream, Inches(1), Inches(1.5), width=Inches(8))

    # Slide 4: Advanced Analytics - Prophet Forecast
    slide = prs.slides.add_slide(content_slide_layout)
    title = slide.shapes.title
    title.text = "Advanced Analytics: Stability Forecast"
    
    # Prepare data for Prophet
    prophet_df = df[['injection_time', 'retention_time']].copy()
    prophet_df.rename(columns={'injection_time': 'ds', 'retention_time': 'y'}, inplace=True)
    
    # Fit model and make forecast
    m = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False).fit(prophet_df)
    future = m.make_future_dataframe(periods=20, freq='15min') # Forecast next 20 samples
    forecast = m.predict(future)
    
    # Generate and save forecast plot to memory
    forecast_fig = plot_plotly(m, forecast)
    forecast_fig.update_layout(title="Forecast of 'Retention Time' to Predict Drift")
    forecast_img_stream = io.BytesIO()
    forecast_fig.write_image(forecast_img_stream, format="png", width=800, height=400, scale=2)
    forecast_img_stream.seek(0)
    
    # Add image to slide
    slide.shapes.add_picture(forecast_img_stream, Inches(1), Inches(1.8), width=Inches(8))

    # Save presentation to a memory buffer
    pptx_io = io.BytesIO()
    prs.save(pptx_io)
    pptx_io.seek(0)
    return pptx_io.getvalue()


# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Report Assembler")
get_user_role()
st.title("Module 3: Regulatory Package & Report Assembler")
st.markdown("Automate the generation of study reports from the Single Source of Truth.")

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

st.markdown("---")

# --- Generation ---
if st.button("Assemble & Download Report"):
    st.subheader("2. Report Generation")
    
    with st.spinner("Assembling real report... Pulling data, generating plots, and compiling..."):
        # Load fresh data for the report
        report_df = create_mock_hplc_data(50)
        
        # Call the new function to generate the PPTX file in memory
        report_bytes = create_report_pptx(report_df, report_template, data_package)
        
        st.success("✔️ Report Assembled!")
        st.info("Your report is a standard `.pptx` file, ready for internal review or to be saved as a PDF.")
    
        # --- Finalization and Download ---
        st.download_button(
            label="⬇️ Download PowerPoint Report (.pptx)",
            data=report_bytes,
            file_name=f"{report_template.replace(' ', '_')}_{data_package.split(' ')[0]}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
else:
    st.info("Click the button above to generate a downloadable PowerPoint report.")

display_compliance_footer()
