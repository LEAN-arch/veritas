# pages/4_stability_program_dashboard.py
import streamlit as st
import pandas as pd
from utils import auth
# Import from the centralized backend modules
from utils import data_connector as dc, plotters, analysis_engine, auth
auth.check_page_authorization()
# Set the page configuration for this specific page
st.set_page_config(page_title="Stability Dashboard", page_icon="⏳", layout="wide")

st.title("⏳ Stability Program Dashboard")
st.markdown("Monitor and trend stability data for drug products against defined specification limits.")

# --- Load data and config from session state ---
stability_df = st.session_state.get('stability_df', pd.DataFrame())
app_config = st.session_state.get('app_config', {})
username = st.session_state.get('username', 'Unknown User')

# Stop execution if the main app hasn't initialized the session properly
if stability_df.empty or not app_config or username == 'Unknown User':
    st.warning("Session not initialized. Please start from the main VERITAS Command Center.")
    st.stop()

spec_limits_config = app_config.get('stability_specs', {})

with st.expander("ℹ️ SME Overview: The Role of a Stability Program"):
    st.info("""
        - **Purpose:** To provide evidence on how the quality of a drug substance or drug product varies with time under the influence of environmental factors (temperature, humidity, light).
        - **Regulatory Significance (ICH Q1A(R2)):** Stability studies are a prerequisite for determining storage conditions, retest periods, and shelf life.
        - **How to Use:** Select a product and lot from the sidebar to view its stability profile and trend analysis.
    """)
    
# --- Sidebar for Filtering (Dynamically Populated) ---
st.sidebar.markdown("## Select Stability Lot")

# Get unique products and lots from the loaded data
product_options = sorted(stability_df['product_id'].unique())
product_filter = st.sidebar.selectbox("Select Product:", options=product_options, key="stab_product_filter")

# Filter lots based on selected product
lot_options = sorted(stability_df[stability_df['product_id'] == product_filter]['lot_id'].unique())
lot_filter = st.sidebar.selectbox("Select Lot:", options=lot_options, key="stab_lot_filter")

# --- Apply Filters ---
filtered_df = stability_df[(stability_df['product_id'] == product_filter) & (stability_df['lot_id'] == lot_filter)]

# --- Smart Auditing: Log only when the view changes ---
last_viewed_key = 'last_viewed_stability_lot'
current_view = f"{product_filter}-{lot_filter}"
if st.session_state.get(last_viewed_key) != current_view:
    dc.write_to_audit_log(
        user=username,
        action="Stability Plot Viewed",
        details=f"Viewed stability data for Product: {product_filter}, Lot: {lot_filter}",
        record_id=lot_filter
    )
    st.session_state[last_viewed_key] = current_view

# --- Main Page Content ---
st.header(f"Stability Profile for {product_filter} - {lot_filter}")

if not filtered_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        assay_purity = 'Purity (%)'
        if assay_purity in spec_limits_config and assay_purity in filtered_df.columns:
            st.plotly_chart(
                plotters.plot_stability_trend(filtered_df, assay_purity, spec_limits_config[assay_purity]),
                use_container_width=True
            )
            # Call analysis engine for projection
            lsl = spec_limits_config[assay_purity]['LSL']
            projection = analysis_engine.calculate_stability_projection(filtered_df, 'Timepoint (Months)', assay_purity, lsl)
            if projection and 'months_to_spec' in projection:
                st.metric(
                    "Estimated Time to LSL (Months)",
                    f"{projection['months_to_spec']:.1f}",
                    f"Trend: {projection['slope']:.3f} / month",
                    help="A simplified linear regression estimate of when the trend line will cross the Lower Specification Limit."
                )
            else:
                st.info("Purity trend is stable or improving.")

    with col2:
        assay_impurity = 'Main Impurity (%)'
        if assay_impurity in spec_limits_config and assay_impurity in filtered_df.columns:
            st.plotly_chart(
                plotters.plot_stability_trend(filtered_df, assay_impurity, spec_limits_config[assay_impurity]),
                use_container_width=True
            )
            # Call analysis engine for projection
            usl = spec_limits_config[assay_impurity]['USL']
            projection = analysis_engine.calculate_stability_projection(filtered_df, 'Timepoint (Months)', assay_impurity, usl)
            if projection and 'months_to_spec' in projection:
                 st.metric(
                    "Estimated Time to USL (Months)",
                    f"{projection['months_to_spec']:.1f}",
                    f"Trend: +{projection['slope']:.3f} / month",
                    help="A simplified linear regression estimate of when the trend line will cross the Upper Specification Limit."
                )
            else:
                st.info("Impurity trend is stable or decreasing.")

    st.markdown("---")
    st.subheader("Raw Stability Data")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
else:
    st.warning("No stability data available for the selected product and lot.")

# Add the compliance footer
auth.display_compliance_footer()
