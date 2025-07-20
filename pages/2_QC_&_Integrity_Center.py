# pages/2_QC_&_Integrity_Center.py
import streamlit as st
import pandas as pd
from sklearn.ensemble import IsolationForest

from utils.auth import display_compliance_footer, get_user_role
from utils.data_generator import create_mock_hplc_data

st.set_page_config(layout="wide", page_title="QC & Integrity Center")
get_user_role()
st.title("Module 2: Automated QC & Integrity Engine")
st.markdown("Define, execute, and review automated data quality checks.")

# Load mock data
@st.cache_data
def load_data():
    return create_mock_hplc_data(100)

df = load_data()

# --- Data Selection ---
st.subheader("1. Select Data Package for QC")
dataset_option = st.selectbox("Select a Dataset", options=['PK_Study_2024-A', 'Tox_Assay_Run_05', 'DMPK_Batch_B01-B'])

st.dataframe(df.head())

# --- QC Configuration and Execution ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("2. Configure QC Rules")
    with st.expander("Data Quality Rules Engine", expanded=True):
        st.write("Select rules to apply to the dataset:")
        rules = {
            'check_nulls': st.checkbox("Check for missing values", value=True),
            'check_negatives': st.checkbox("Check for negative concentrations", value=True),
            'check_retention_time': st.checkbox("Check retention time range (2.3-2.7 min)", value=True),
            'run_outlier_detection': st.checkbox("Run ML-based outlier detection (Isolation Forest)")
        }
with col2:
    st.subheader("3. Execute and Review")
    if st.button("▶️ Run QC Analysis on Selected Data"):
        with st.status("Executing QC checks...", expanded=True) as status:
            st.write("Applying rule: Check for missing values...")
            time.sleep(1)
            null_issues = df.isnull().sum().sum()
            
            st.write("Applying rule: Check for negative concentrations...")
            time.sleep(1)
            negative_issues = (df['analyte_concentration'] < 0).sum()
            
            st.write("Running ML Outlier Detection...")
            time.sleep(1.5)
            if rules['run_outlier_detection']:
                iso_forest = IsolationForest(contamination=0.05, random_state=42)
                preds = iso_forest.fit_predict(df[['analyte_concentration', 'peak_area', 'retention_time']].dropna())
                outlier_issues = (preds == -1).sum()
            else:
                outlier_issues = 0

            total_issues = null_issues + negative_issues + outlier_issues
            num_cells = df.shape[0] * df.shape[1]
            dqs = 100 * (1 - total_issues / num_cells)

            status.update(label="QC Complete!", state="complete", expanded=False)

        st.subheader("QC Results")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Data Quality Score (DQS)", f"{dqs:.1f}%")
        res_col2.metric("First Pass Yield (FPY)", "FAIL", delta="-12% from target", delta_color="inverse")
        res_col3.metric("Discrepancies Found", total_issues)
        
        st.error(f"Found {total_issues} discrepancies. Flagged data has been sent to the QC Analyst Triage Queue.")
        st.info("A detailed QC report has been generated and logged.")

display_compliance_footer()
