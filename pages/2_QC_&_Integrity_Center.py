# pages/2_QC_&_Integrity_Center.py
import streamlit as st
import pandas as pd
import time
from sklearn.ensemble import IsolationForest
import numpy as np
import plotly.express as px
from scipy import stats

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_hplc_data
from utils.plotters import plot_qq, plot_ml_anomaly_results, plot_anova_results

def apply_qc_rules(df, rules_config):
    """
    Applies a set of deterministic rules to a dataframe and returns a report of discrepancies.
    This function is the core of the rule-based QC engine.
    """
    discrepancies = []
    
    # Rule 1: Check for any missing (null) values in any column
    if rules_config['check_nulls']:
        nulls = df[df.isnull().any(axis=1)]
        for index, row in nulls.iterrows():
            discrepancies.append({
                'sample_id': row['sample_id'], 
                'Issue': 'Missing Value', 
                'Details': f"Null found in column(s): {row.index[row.isnull()].tolist()}"
            })
            
    # Rule 2: Check for physically impossible negative concentration values
    if rules_config['check_negatives']:
        negatives = df[df['analyte_concentration'] < 0]
        for index, row in negatives.iterrows():
            discrepancies.append({
                'sample_id': row['sample_id'], 
                'Issue': 'Negative Value', 
                'Details': f"Analyte concentration is {row['analyte_concentration']:.2f}"
            })

    # Rule 3: Check if retention time is within the validated method's specification
    if rules_config['check_retention_range']:
        oor = df[~df['retention_time'].between(2.4, 2.8)]
        for index, row in oor.iterrows():
             discrepancies.append({
                'sample_id': row['sample_id'], 
                'Issue': 'Out of Spec', 
                'Details': f"Retention time is {row['retention_time']:.2f}, outside 2.4-2.8 min spec."
            })
            
    return pd.DataFrame(discrepancies) if discrepancies else pd.DataFrame(columns=['sample_id', 'Issue', 'Details'])


# --- Page Configuration and Sidebar ---
st.set_page_config(layout="wide", page_title="QC & Integrity Center", page_icon="🧪")
with st.sidebar:
    st.title("VERITAS")
    get_user_role()

# --- Page Header ---
st.title("Module 2: QC & Integrity Center")
st.markdown("A suite of advanced tools for statistical process control, data quality validation, and anomaly detection.")

# --- Data Loading and Selection ---
@st.cache_data
def load_qc_data(): return create_mock_hplc_data(250)
df = load_qc_data()

study_id = st.sidebar.selectbox("Select Study for QC", options=df['study_id'].unique(), key="qc_study_selector")
selected_df = df[df['study_id'] == study_id].copy()

# --- Main Tabs for different QC workflows ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 **Rule-Based QC**", "📊 **Statistical Deep Dive**", "🤖 **ML Anomaly Detection**", "🔬 **Cross-Instrument Analysis**"])

with tab1:
    st.subheader("Automated Rule-Based Quality Control")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Configure QC Rules")
        rules_config = {
            'check_nulls': st.checkbox("Check for missing values", value=True),
            'check_negatives': st.checkbox("Check for negative concentrations", value=True),
            'check_retention_range': st.checkbox("Check retention time spec (2.4-2.8 min)", value=True),
        }
        if st.button("▶️ Execute QC Analysis", type="primary"):
            st.session_state['discrepancy_report'] = apply_qc_rules(selected_df, rules_config)
            st.session_state['qc_run_complete'] = True
            
    with col2:
        st.markdown("#### QC Analysis Results")
        if st.session_state.get('qc_run_complete', False):
            report_df = st.session_state['discrepancy_report']
            total_issues = len(report_df)
            total_points = selected_df.shape[0] * selected_df.shape[1]
            dqs = 100 * (1 - (total_issues / total_points))
            
            st.metric("Data Quality Score (DQS)", f"{dqs:.2f}%", f"-{total_issues} issues found")
            
            if not report_df.empty:
                st.error(f"Found {len(report_df)} discrepancies requiring attention.")
                st.dataframe(report_df, use_container_width=True, hide_index=True)
            else:
                st.success("Congratulations! No rule-based discrepancies were found in this dataset.")
        else:
            st.info("Configure rules and click 'Execute QC Analysis' to see results.")

with tab2:
    st.subheader("Statistical Deep Dive")
    param = st.selectbox("Select Parameter", options=['analyte_concentration', 'peak_area', 'retention_time'])
    data_to_test = selected_df[param].dropna()
    
    col1, col2 = st.columns(2)
    with col1:
        stat, p_value = stats.shapiro(data_to_test)
        st.markdown("#### Shapiro-Wilk Normality Test")
        st.metric("P-value", f"{p_value:.4f}")
        if p_value > 0.05: st.success("Conclusion: Data appears to be normally distributed (p > 0.05).")
        else: st.warning("Conclusion: Data does not appear to be normally distributed (p <= 0.05).")
    with col2:
        st.markdown("#### Descriptive Statistics")
        st.dataframe(data_to_test.describe())
        
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(data_to_test, marginal="box", title=f"Distribution of {param}")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = plot_qq(data_to_test)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Machine Learning-Powered Anomaly Detection")
    col1, col2 = st.columns([1, 2])
    with col1:
        contamination = st.slider("Anomaly Sensitivity", 0.01, 0.2, 0.05, 0.01, help="The estimated proportion of outliers in the data.")
        if st.button("🤖 Find Anomalies", type="primary"):
            numeric_cols = selected_df.select_dtypes(include=np.number).dropna()
            model = IsolationForest(contamination=contamination, random_state=42)
            preds = model.fit_predict(numeric_cols)
            st.session_state['ml_preds'] = preds
            st.session_state['ml_cols'] = numeric_cols
    with col2:
        if 'ml_preds' in st.session_state:
            st.plotly_chart(plot_ml_anomaly_results(st.session_state['ml_cols'], st.session_state['ml_preds']), use_container_width=True)
            st.info(f"Analysis complete. Found {(st.session_state['ml_preds'] == -1).sum()} potential anomalies for review.")

with tab4:
    st.subheader("Cross-Instrument Performance & Bias Detection")
    st.info("💡 **SME Insight:** Ensuring consistency across different instruments is critical for pooling data and validating methods. Use ANOVA to detect if one instrument is systematically biased (i.e., consistently measures higher or lower) compared to others.")
    value_to_compare = st.selectbox("Select Measurement for Comparison", options=['retention_time', 'peak_area'])
    st.plotly_chart(plot_anova_results(df, value_to_compare, 'instrument_id'), use_container_width=True)

display_compliance_footer()
