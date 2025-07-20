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
from utils.plotters import plot_qq, plot_ml_anomaly_results, plot_feature_importance, plot_anova_results, VERTEX_COLORS

st.set_page_config(layout="wide", page_title="QC & Integrity Center")
with st.sidebar:
    st.image("vertex-logo.png", width=200)
    st.title("VERITAS")
get_user_role()
st.title("Module 2: QC & Integrity Center")
st.markdown("A suite of advanced tools for statistical process control, data quality validation, and anomaly detection.")

# --- Data Caching & Selection ---
@st.cache_data
def load_qc_data(): return create_mock_hplc_data(250)
df = load_qc_data()
study_id = st.sidebar.selectbox("Select Study for QC", options=df['study_id'].unique())
selected_df = df[df['study_id'] == study_id]

# --- Main Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 **Rule-Based QC**", "📊 **Statistical Deep Dive**", "🤖 **ML Anomaly Detection**", "🔬 **Cross-Instrument Analysis**"])

with tab1:
    st.subheader("Automated Rule-Based Quality Control")
    # ... (content similar to previous version, but more polished)
    st.info("Define and apply a set of deterministic rules to catch common data errors.")
    
with tab2:
    st.subheader("Statistical Deep Dive")
    with st.expander("ℹ️ SME Overview: The Importance of Distributional Analysis"):
        st.info("""
            Before applying many statistical models, it's crucial to understand the distribution of your data. Normality (a 'bell curve' shape) is a key assumption for tests like t-tests and ANOVA.
            - **Histogram:** Provides a quick visual check of the data's shape and spread.
            - **Q-Q Plot:** A more rigorous test for normality. If points hug the red line, the assumption of normality holds. Deviations suggest skewness or heavy tails.
            - **Shapiro-Wilk Test:** A formal statistical test for normality. A **p-value > 0.05** suggests the data is normally distributed.
        """)
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
    with col1: fig = px.histogram(data_to_test, marginal="box"); st.plotly_chart(fig, use_container_width=True)
    with col2: fig = plot_qq(data_to_test); st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Machine Learning-Powered Anomaly Detection")
    st.info("💡 **SME Insight:** Isolation Forest excels at finding rare, unexpected data points in high-dimensional space. Unlike rule-based checks that look at one variable at a time, this method considers all variables simultaneously to find 'unusual combinations.'")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        contamination = st.slider("Anomaly Sensitivity", 0.01, 0.2, 0.05, 0.01, help="The estimated proportion of outliers in the data. Higher values will flag more points as anomalies.")
        if st.button("🤖 Find Anomalies", type="primary"):
            numeric_cols = selected_df.select_dtypes(include=np.number).dropna()
            model = IsolationForest(contamination=contamination, random_state=42)
            preds = model.fit_predict(numeric_cols)
            st.session_state['ml_preds'] = preds
            st.session_state['ml_cols'] = numeric_cols
            st.session_state['ml_model'] = model
    
    with col2:
        if 'ml_preds' in st.session_state:
            st.plotly_chart(plot_ml_anomaly_results(st.session_state['ml_cols'], st.session_state['ml_preds']), use_container_width=True)

with tab4:
    st.subheader("Cross-Instrument Performance & Bias Detection")
    st.info("💡 **SME Insight:** Ensuring consistency across different instruments is critical for pooling data and validating methods. Use these plots to detect if one instrument is systematically biased (i.e., consistently measures higher or lower) compared to others.")
    value_to_compare = st.selectbox("Select Measurement for Comparison", options=['retention_time', 'peak_area'])
    st.plotly_chart(plot_anova_results(df, value_to_compare, 'instrument_id'), use_container_width=True)

display_compliance_footer()
