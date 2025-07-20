# utils/data_connector.py
import streamlit as st
import pandas as pd
from datetime import datetime

# Import the factory to act as our "database" and the centralized config
from utils.mock_data_factory import MockDataFactory
from utils.config import APP_CONFIG

# --- Connection and Configuration ---

def connect_to_db(params: dict):
    """
    Simulates establishing a connection to a database. In a real app, this
    would return a live connection object. Here, it's a conceptual placeholder.
    """
    return f"Simulated connection to {params.get('database', 'UNKNOWN')}"

@st.cache_data(ttl=3600) # Cache app config for 1 hour
def fetch_app_config(_connection) -> dict:
    """
    Fetches the application's configuration from the centralized config file.
    The _connection parameter is kept for API consistency.
    """
    return APP_CONFIG

# --- Data Factory as the Data Source ---

@st.cache_resource
def get_data_factory():
    """
    Creates and caches a single instance of the MockDataFactory.
    This acts as our persistent, in-memory database for the session.
    """
    return MockDataFactory()

# --- Data Fetching and Initialization API ---

def initialize_session_data():
    """
    Initializes all necessary data into session state.
    - Read-only data is fetched directly.
    - Mutable data (that will be changed by user actions) is copied.
    This should be called once at the start of the app.
    """
    factory = get_data_factory()
    
    # Place all dataframes into session state for universal access
    if 'hplc_df' not in st.session_state:
        st.session_state.hplc_df = factory.hplc_df
    if 'deviations_df' not in st.session_state:
        st.session_state.deviations_df = factory.deviations_df.copy() # Copy for safe mutation
    if 'stability_df' not in st.session_state:
        st.session_state.stability_df = factory.stability_df
    if 'audit_df' not in st.session_state:
        st.session_state.audit_df = factory.audit_df.copy() # Copy for safe mutation
    if 'gantt_df' not in st.session_state:
        st.session_state.gantt_df = factory.gantt_df
    if 'ingestion_history_df' not in st.session_state:
        st.session_state.ingestion_history_df = factory.ingestion_history_df


def fetch_hplc_data() -> pd.DataFrame:
    """Fetches the primary HPLC dataset from session state."""
    return st.session_state.get('hplc_df', pd.DataFrame())

def fetch_deviations_data() -> pd.DataFrame:
    """Fetches the deviations dataset from session state."""
    return st.session_state.get('deviations_df', pd.DataFrame())

def fetch_stability_data() -> pd.DataFrame:
    """Fetches the stability program dataset from session state."""
    return st.session_state.get('stability_df', pd.DataFrame())

def fetch_audit_log() -> pd.DataFrame:
    """Fetches the audit log from session state."""
    return st.session_state.get('audit_df', pd.DataFrame())

def fetch_gantt_data() -> pd.DataFrame:
    """Fetches the Gantt chart data from session state."""
    return st.session_state.get('gantt_df', pd.DataFrame())

def fetch_ingestion_history() -> pd.DataFrame:
    """Fetches the ingestion history data from session state."""
    return st.session_state.get('ingestion_history_df', pd.DataFrame())


# --- Live Audit Trail Writing ---

def write_to_audit_log(user: str, action: str, details: str, record_id: str = 'N/A'):
    """
    Writes a new entry to the audit_log DataFrame in session state,
    making the audit trail interactive and live.
    """
    if 'audit_df' not in st.session_state:
        print(f"ERROR: Could not write to audit log. 'audit_df' not in session state.")
        return

    log_entry = {
        'Timestamp': pd.to_datetime(datetime.now()),
        'User': user,
        'Action': action,
        'Record ID': record_id,
        'Details': details
    }
    
    new_row_df = pd.DataFrame([log_entry])
    st.session_state.audit_df = pd.concat([new_row_df, st.session_state.audit_df], ignore_index=True)
    
    print(f"AUDIT LOGGED: User '{user}' -> Action '{action}' for Record '{record_id}'")
    st.toast(f"Action Logged: {action}", icon="📝")
