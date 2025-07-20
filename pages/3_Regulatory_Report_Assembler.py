# pages/3_Regulatory_Report_Assembler.py
import streamlit as st
import pandas as pd
import time
import io
from pptx import Presentation
from pptx.util import Inches, Pt
import plotly.graph_objects as go

# Import the new forecasting library
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA

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
    
    summary_df = df.head(10)[['sample_id', 'batch_id', 'analyte_concentration', 'retention_time']]
    add_table_to_slide(slide, summary_df, Inches(0.5), Inches(1.5), Inches(9.0), Inches(4.0))

    # Slide 3: Statistical Process Control (SPC) Chart
    slide = prs.slides.add_slide(content_slide_layout)
    title = slide.shapes.title
    title.text = "Process Stability Analysis (SPC)"
    
    spc_fig = plot_spc_chart(df, 'analyte_concentration')
    spc_img_stream = io.BytesIO()
    spc_fig.write_image(spc_img_stream, format="png", width=800, height=450, scale=2)
    spc_img_stream.seek(0)
    slide.shapes.add_picture(spc_img_stream, Inches(1), Inches(1.5), width=Inches(8))

    # Slide 4: Advanced Analytics - StatsForecast
    slide = prs.slides.add_slide(content_slide_layout)
    title = slide.shapes.title
    title.text = "Advanced Analytics: Stability Forecast (AutoARIMA)"
    
    # Prepare data for StatsForecast
    fcst_df = df[['injection_time', 'retention_time']].copy()
    fcst_df.rename(columns={'injection_time': 'ds', 'retention_time': 'y'}, inplace=True)
    fcst_df['unique_id'] = 'instrument_1' # Add a required unique_id column
    fcst_df = fcst_df.sort_values('ds').reset_index(drop=True)

    # Fit model and make forecast
    sf = StatsForecast(models=[AutoARIMA()], freq='15min')
    sf.fit(fcst_df)
    forecast_df = sf.predict(h=20) # Forecast next 20 samples
    
    # Generate and save forecast plot to memory
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fcst_df['ds'], y=fcst_df['y'], mode='lines', name='Historical Data'))
    fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['AutoARIMA'], mode='lines', name='Forecast', line={'dash': 'dash'}))
    fig.update_layout(title="Forecast of 'Retention Time' to Predict Drift", xaxis_title="Time", yaxis_title="Retention Time")
    
    forecast_img_stream = io.BytesIO()
    fig.write_image(forecast_img_stream, format="png", width=800, height=400, scale=2)
    forecast_img_stream.seek(0)
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

st.subheader("1. Report Configuration")
col1, col2 = st.columns(2)
with col1:
    report_template = st.selectbox("Select Report Template", ("IND Study Report", "PK Analysis Summary"))
with col2:
    data_package = st.selectbox("Select Approved QC'd Data Package", ("PK_Study_2024-A (v2.1)", "Tox_Assay_Run_05 (v1.0)"))

st.markdown("---")

if st.button("Assemble & Download Report"):
    with st.spinner("Assembling real report... This may take a moment."):
        report_df = create_mock_hplc_data(50)
        report_bytes = create_report_pptx(report_df, report_template, data_package)
        
    st.success("✔️ Report Assembled!")
    st.download_button(
        label="⬇️ Download PowerPoint Report (.pptx)",
        data=report_bytes,
        file_name=f"{report_template.replace(' ', '_')}.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

display_compliance_footer()
