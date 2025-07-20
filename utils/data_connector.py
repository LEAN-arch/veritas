# utils/data_connector.py
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.mock_data_factory import MockDataFactory
from utils.config import APP_CONFIG

def connect_to_db(params: dict):
    return f"Simulated connection to {params.get('database', 'UNKNOWN')}"

@st.cache_data(ttl=3600)
def fetch_app_config(_connection) -> dict:
    return APP_CONFIG

@st.cache_resource
def get_data_factory():
    return MockDataFactory()

def initialize_session_data():
    factory = get_data_factory()
    if 'hplc_df' not in st.session_state:
        st.session_state.hplc_df = factory.hplc_df
    if 'deviations_df' not in st.session_state:
        st.session_state.deviations_df = factory.deviations_df.copy()
    if 'stability_df' not in st.session_state:
        st.session_state.stability_df = factory.stability_df
    if 'audit_df' not in st.session_state:
        st.session_state.audit_df = factory.audit_df.copy()
    if 'gantt_df' not in st.session_state:
        st.session_state.gantt_df = factory.gantt_df
    if 'ingestion_history_df' not in st.session_state:
        st.session_state.ingestion_history_df = factory.ingestion_history_df

def fetch_hplc_data() -> pd.DataFrame:
    return st.session_state.get('hplc_df', pd.DataFrame())

def fetch_deviations_data() -> pd.DataFrame:
    return st.session_state.get('deviations_df', pd.DataFrame())

def fetch_stability_data() -> pd.DataFrame:
    return st.session_state.get('stability_df', pd.DataFrame())

def fetch_audit_log() -> pd.DataFrame:
    return st.session_state.get('audit_df', pd.DataFrame())

def fetch_gantt_data() -> pd.DataFrame:
    return st.session_state.get('gantt_df', pd.DataFrame())

def fetch_ingestion_history() -> pd.DataFrame:
    return st.session_state.get('ingestion_history_df', pd.DataFrame())

# --- THE FIX IS HERE ---
# The function signature is corrected to include the connection parameter, matching the calls.
def write_to_audit_log(_connection, user: str, action: str, details: str, record_id: str = 'N/A'):
    """
    Writes a new entry to the audit_log DataFrame in session state.
    The _connection parameter is kept for API consistency.
    """
    if 'audit_df' not in st.session_state:
        print(f"ERROR: Could not write to audit log. 'audit_df' not in session state.")
        return

    log_entry = {
        'Timestamp': pd.to_datetime(datetime.now()), 'User': user, 'Action': action,
        'Record ID': record_id, 'Details': details
    }
    
    new_row_df = pd.DataFrame([log_entry])
    st.session_state.audit_df = pd.concat([new_row_df, st.session_state.audit_df], ignore_index=True)
    
    print(f"AUDIT LOGGED: User '{user}' -> Action '{action}' for Record '{record_id}'")
    st.toast(f"Action Logged: {action}", icon="📝")
