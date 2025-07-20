# pages/1_Process_Capability_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import timedelta

# Import from the new, centralized backend modules
from utils.plotters import plot_historical_control_chart, plot_process_capability
from utils.analysis_engine import calculate_cpk

def render_page():
    """
    Renders the Process Capability Dashboard.
    This function acts as the main entry point for the page.
    """
    st.title("📈 Process Capability Dashboard")
    st.markdown("Analyze historical process stability and capability (Cpk) for any product or assay.")
    
    # --- Load data from session state ---
    # This assumes the main app has already loaded the data.
    hplc_df = st.session_state.get('hplc_df', pd.DataFrame())
    app_config = st.session_state.get('app_config', {})
    
    if hplc_df.empty or not app_config:
        st.warning("Data not loaded. Please return to the main Command Center.")
        return

    # --- Configuration from central config file ---
    cpk_config = app_config.get('process_capability', {})
    cpk_target = cpk_config.get('cpk_target', 1.33)
    available_cqas = cpk_config.get('available_cqas', [])
    spec_limits_config = cpk_config.get('spec_limits', {})

    with st.expander("ℹ️ SME Overview: Understanding Process Capability"):
        st.info(f"""
            - **Process Capability (Cpk):** A statistical measure of a process's ability to produce output within specification limits. A Cpk of **{cpk_target}** or greater is generally considered capable.
            - **Control Charts (I-Chart):** A graphical tool used to monitor a process over time, distinguishing between common and special cause variation.
            - **How to Use:** Use the sidebar filters to select a data subset, then choose a CQA to analyze its stability and capability.
        """)

    # --- Sidebar for Filtering ---
    # This will now appear on the page-specific sidebar defined by Streamlit's multi-page app feature
    st.sidebar.markdown("## Filter Data")
    
    # Filter by Study
    study_options = ['All'] + sorted(hplc_df['study_id'].unique())
    study_id_filter = st.sidebar.selectbox("Filter by Study:", options=study_options, key="cap_study_filter")
    
    # Filter by Instrument
    instrument_options = ['All'] + sorted(hplc_df['instrument_id'].unique())
    instrument_id_filter = st.sidebar.selectbox("Filter by Instrument:", options=instrument_options, key="cap_instrument_filter")
    
    # --- Apply Filters to Data ---
    filtered_df = hplc_df.copy()
    if study_id_filter != 'All':
        filtered_df = filtered_df[filtered_df['study_id'] == study_id_filter]
    if instrument_id_filter != 'All':
        filtered_df = filtered_df[filtered_df['instrument_id'] == instrument_id_filter]

    st.sidebar.success(f"{len(filtered_df)} data points selected.")

    # --- Main Page Content ---
    st.subheader("Analysis Configuration")

    col1, col2 = st.columns([2,3])
    with col1:
        selected_cqa = st.selectbox(
            "Select a Critical Quality Attribute (CQA) to Analyze:",
            options=available_cqas
        )

    with col2:
        # Define date range slider
        min_date = hplc_df['injection_time'].min().date()
        max_date = hplc_df['injection_time'].max().date()
        date_range = st.slider(
            "Select Date Range for Analysis:",
            min_value=min_date,
            max_value=max_date,
            value=(max_date - timedelta(days=90), max_date),
            format="YYYY-MM-DD"
        )
    
    st.markdown("---")

    # --- Display Analytics ---
    if len(filtered_df) > 2:
        # Get spec limits for the selected CQA from the central config
        lsl = spec_limits_config.get(selected_cqa, {}).get('LSL')
        usl = spec_limits_config.get(selected_cqa, {}).get('USL')

        # Perform Cpk calculation using the backend analysis engine
        cpk_value = calculate_cpk(filtered_df[selected_cqa], lsl, usl)
        
        # Display charts
        plot_col1, plot_col2 = st.columns(2)
        with plot_col1:
            st.plotly_chart(
                plot_historical_control_chart(filtered_df, selected_cqa, date_range),
                use_container_width=True
            )
        with plot_col2:
            st.plotly_chart(
                plot_process_capability(filtered_df, selected_cqa, lsl, usl, cpk_value),
                use_container_width=True
            )
    else:
        st.warning("Not enough data available for the selected filters to perform analysis.")

# --- This check ensures the page is run correctly from the main app ---
if __name__ == "__main__":
    # You would need to mock st.session_state for direct execution
    # For a real app, direct execution of a page is discouraged.
    # The user should always start from VERITAS_app.py
    st.error("This page should be run from the main VERITAS Command Center app.")
