# pages/2_Stability_Program_Dashboard.py
import streamlit as st
import pandas as pd
import numpy as np

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth
from utils.plotters import plot_stability_trend

# --- Page Configuration ---
st.set_page_config(
    page_title="Stability Program Dashboard",
    page_icon="⏳",
    layout="wide"
)

# --- Authentication and Data Loading ---
user_role = auth.authenticate_user()
db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})
APP_CONFIG = dc.fetch_app_config(db_connection)

# --- Page Header ---
st.title("⏳ Stability Program Dashboard")
st.markdown("Monitor and trend stability data for drug products against defined specification limits.")

with st.expander("ℹ️ SME Overview: The Role of a Stability Program"):
    st.info("""
        - **Purpose:** To provide evidence on how the quality of a drug substance or drug product varies with time under the influence of environmental factors (temperature, humidity, light).
        - **Regulatory Significance (ICH Q1A(R2)):** Stability studies are a prerequisite for determining storage conditions, retest periods, and shelf life, which are critical components of any regulatory submission (IND, BLA, NDA).
        - **How to Use:** Select a product and a specific lot to view its stability profile. The plots show the trend of each Critical Quality Attribute (CQA) over time relative to its approved specification limits. Any trend approaching a limit is a potential risk.
    """)

# --- Sidebar for Filtering ---
st.sidebar.markdown("## Select Stability Lot")
# In a real app, these lists would be populated from a database query
product_filter = st.sidebar.selectbox(
    "Select Product:",
    options=['VX-809 DP', 'VX-561 DS', 'VX-121 DP'],
    key="product_filter"
)
lot_filter = st.sidebar.selectbox(
    "Select Lot:",
    options=['Lot A202301', 'Lot A202302', 'Lot B202301'],
    key="lot_filter"
)

# --- Audit Log Entry ---
dc.write_to_audit_log(
    db_connection,
    user=st.session_state.username,
    action="Stability Plot Viewed",
    details=f"Viewed stability data for Product: {product_filter}, Lot: {lot_filter}"
)

# --- Data Fetching & Display ---
st.header(f"Stability Profile for {product_filter} - {lot_filter}")

# Fetch the stability data for the selected lot
stability_df = dc.fetch_stability_data(db_connection, product_filter, lot_filter)

# Get the relevant specification limits from the external configuration
spec_limits = APP_CONFIG['stability_specs']

col1, col2 = st.columns(2)

with col1:
    # Plot Purity Trend
    assay_purity = 'Purity (%)'
    st.plotly_chart(
        plot_stability_trend(stability_df, assay_purity, spec_limits[assay_purity]),
        use_container_width=True
    )
    # Perform a simple linear regression to predict shelf life
    # Note: Real shelf-life analysis (e.g., ICH Q1E) is more complex. This is a simulation.
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(stability_df['Timepoint (Months)'], stability_df[assay_purity])
    
    # Calculate estimated time to hit the Lower Spec Limit (LSL)
    lsl = spec_limits[assay_purity]['LSL']
    if slope < 0:
        months_to_lsl = (lsl - intercept) / slope
        st.metric(
            "Estimated Time to LSL (Months)",
            f"{months_to_lsl:.1f}",
            help="A simplified linear regression estimate of when the trend line will cross the Lower Specification Limit."
        )
    else:
        st.info("Purity trend is not degrading.")

with col2:
    # Plot Impurity Trend
    assay_impurity = 'Main Impurity (%)'
    st.plotly_chart(
        plot_stability_trend(stability_df, assay_impurity, spec_limits[assay_impurity]),
        use_container_width=True
    )
    slope, intercept, _, _, _ = linregress(stability_df['Timepoint (Months)'], stability_df[assay_impurity])
    
    # Calculate estimated time to hit the Upper Spec Limit (USL)
    usl = spec_limits[assay_impurity]['USL']
    if slope > 0:
        months_to_usl = (usl - intercept) / slope
        st.metric(
            "Estimated Time to USL (Months)",
            f"{months_to_usl:.1f}",
            help="A simplified linear regression estimate of when the trend line will cross the Upper Specification Limit."
        )
    else:
        st.info("Impurity trend is not increasing.")

st.markdown("---")
st.subheader("Raw Stability Data")
st.dataframe(stability_df, use_container_width=True, hide_index=True)

# --- Global Compliance Footer ---
auth.display_compliance_footer()
