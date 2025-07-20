# pages/2_qc_and_integrity_center.py
import streamlit as st
import pandas as pd
import numpy as np

# Import from the centralized backend modules
from utils import qc_engine, plotters, auth

# Set the page configuration for this specific page
st.set_page_config(page_title="QC & Integrity Center", page_icon="🔬", layout="wide")

st.title("🔬 QC & Integrity Center")
st.markdown("A suite of advanced tools for data quality validation and anomaly detection.")

# --- Load data and config from session state ---
hplc_df = st.session_state.get('hplc_df', pd.DataFrame())
app_config = st.session_state.get('app_config', {})

# Stop execution if the main app hasn't initialized the session properly
if hplc_df.empty or not app_config:
    st.warning("Session not initialized. Please start from the main VERITAS Command Center.")
    st.stop()
    
# --- Sidebar for Data Selection ---
st.sidebar.markdown("## QC Data Selection")
study_id_options = sorted(hplc_df['study_id'].unique())
study_id = st.sidebar.selectbox("Select Study for QC", options=study_id_options, key="qc_study_selector")
selected_df = hplc_df[hplc_df['study_id'] == study_id].copy()
st.sidebar.info(f"{len(selected_df)} data points in study '{study_id}'.")

# --- Main Tabs for different QC workflows ---
tab1, tab2, tab3 = st.tabs(["📋 **Rule-Based QC**", "📊 **Statistical Deep Dive**", "🤖 **ML Anomaly Detection**"])

with tab1:
    st.subheader("Automated Rule-Based Quality Control")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Configure QC Rules")
        rules_config = {
            'check_nulls': st.checkbox("Check for missing values", value=True),
            'check_negatives': st.checkbox("Check for negative values", value=True),
            'check_spec_limits': st.checkbox("Check against CQA specifications", value=True),
        }
        if st.button("▶️ Execute QC Analysis", type="primary"):
            with st.spinner("Running QC checks..."):
                # Call the backend QC engine
                discrepancy_report = qc_engine.apply_qc_rules(selected_df, rules_config, app_config)
                st.session_state['discrepancy_report'] = discrepancy_report
    
    with col2:
        st.markdown("#### QC Analysis Results")
        if 'discrepancy_report' in st.session_state:
            report_df = st.session_state['discrepancy_report']
            st.metric("Discrepancies Found", len(report_df))
            
            if not report_df.empty:
                st.error(f"Found {len(report_df)} issues requiring attention.")
                st.dataframe(report_df, use_container_width=True, hide_index=True)
            else:
                st.success("Congratulations! No rule-based discrepancies were found in this dataset.")
        else:
            st.info("Configure rules and click 'Execute QC Analysis' to see results.")

with tab2:
    st.subheader("Statistical Deep Dive")
    numeric_cols = selected_df.select_dtypes(include=np.number).columns.tolist()
    param = st.selectbox("Select Parameter", options=numeric_cols)
    data_to_test = selected_df[param].dropna()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Shapiro-Wilk Normality Test")
        # Call backend analysis engine
        normality_results = qc_engine.perform_normality_test(data_to_test)
        if normality_results['p_value'] is not None:
            st.metric("P-value", f"{normality_results['p_value']:.4f}")
            if normality_results['p_value'] > 0.05:
                st.success(normality_results['conclusion'])
            else:
                st.warning(normality_results['conclusion'])
        else:
            st.info(normality_results['conclusion'])
    with col2:
        st.markdown("#### Descriptive Statistics")
        st.dataframe(data_to_test.describe())
        
    st.plotly_chart(plotters.plot_qq(data_to_test), use_container_width=True)

with tab3:
    st.subheader("Machine Learning-Powered Anomaly Detection")
    st.info("Use an Isolation Forest model to find unusual data points in 2D space.")
    
    col1, col2, col3 = st.columns(3)
    numeric_cols_ml = selected_df.select_dtypes(include=np.number).columns.tolist()
    # Ensure there are at least 2 numeric columns for selection
    if len(numeric_cols_ml) >= 2:
        with col1:
            x_col = st.selectbox("Select X-axis variable", numeric_cols_ml, index=numeric_cols_ml.index('Purity') if 'Purity' in numeric_cols_ml else 0)
        with col2:
            y_col = st.selectbox("Select Y-axis variable", numeric_cols_ml, index=numeric_cols_ml.index('Bio-activity') if 'Bio-activity' in numeric_cols_ml else 1)
        with col3:
            contamination = st.slider("Anomaly Sensitivity", 0.01, 0.2, 0.05, 0.01, help="The estimated proportion of outliers in the data.")
        
        if st.button("🤖 Find Anomalies", type="primary"):
            # Call backend ML engine
            predictions, data_fitted = qc_engine.run_anomaly_detection(selected_df, x_col, y_col, contamination)
            st.session_state['ml_preds'] = predictions
            st.session_state['ml_data_fitted'] = data_fitted
            st.session_state['ml_x_col'] = x_col
            st.session_state['ml_y_col'] = y_col

        if 'ml_preds' in st.session_state and st.session_state['ml_preds'] is not None:
            st.plotly_chart(plotters.plot_ml_anomaly_results(
                st.session_state['ml_data_fitted'], 
                st.session_state['ml_x_col'], 
                st.session_state['ml_y_col'], 
                st.session_state['ml_preds']), 
                use_container_width=True
            )
            anomaly_count = (st.session_state['ml_preds'] == -1).sum()
            st.info(f"Analysis complete. Found {anomaly_count} potential anomalies for review.")
    else:
        st.warning("This dataset does not have enough numeric columns (at least 2 required) for ML anomaly detection.")

# Add the compliance footer
auth.display_compliance_footer()
