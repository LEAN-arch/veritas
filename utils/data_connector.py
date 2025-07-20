# utils/data_connector.py
import streamlit as st
import pandas as pd
from datetime import datetime

# Import the new factory to act as our "database"
from utils.mock_data_factory import MockDataFactory
# Import the centralized config
from utils.config import APP_CONFIG

# --- Connection and Configuration ---

def connect_to_db(params: dict):
    """
    Simulates establishing a connection to a database. In a real app, this
    would return a live connection object. Here, it's a conceptual placeholder.
    """
    # This function is kept for architectural pattern consistency.
    # The actual "connection" is the cached data factory.
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
    Using @st.cache_resource ensures the factory is created only once per session,
    acting as our persistent, in-memory database for the session.
    """
    return MockDataFactory()

# --- Data Fetching API ---

def initialize_session_data():
    """
    Initializes mutable data (that will be changed by user actions) into
    session state. This should be called once at the start of the app.
    Data that is read-only does not need to be in session state.
    """
    factory = get_data_factory()
    if 'deviations_df' not in st.session_state:
        st.session_state.deviations_df = factory.deviations_df.copy()
    if 'audit_df' not in st.session_state:
        st.session_state.audit_df = factory.audit_df.copy()

def fetch_hplc_data(_connection) -> pd.DataFrame:
    """Fetches the read-only primary HPLC dataset from the data factory."""
    return get_data_factory().hplc_df

def fetch_stability_data(_connection) -> pd.DataFrame:
    """Fetches the read-only stability program dataset from the data factory."""
    return get_data_factory().stability_df
    
def fetch_gantt_data(_connection) -> pd.DataFrame:
    """Fetches the read-only Gantt chart data from the data factory."""
    return get_data_factory().gantt_df

def fetch_deviations_data() -> pd.DataFrame:
    """Fetches the mutable deviations dataset from session state."""
    return st.session_state.get('deviations_df', pd.DataFrame())

def fetch_audit_log() -> pd.DataFrame:
    """Fetches the mutable audit log from session state."""
    return st.session_state.get('audit_df', pd.DataFrame())


# --- Live Audit Trail Writing ---

def write_to_audit_log(_connection, user: str, action: str, details: str, record_id: str = 'N/A'):
    """
    Writes a new entry to the audit_log DataFrame in session state,
    making the audit trail interactive and live.
    
    The _connection parameter is kept for API consistency.
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
    
    # Create a new DataFrame from the single entry and concatenate.
    # For user-driven actions, this is efficient enough and safer than manipulating lists.
    new_row_df = pd.DataFrame([log_entry])
    st.session_state.audit_df = pd.concat([new_row_df, st.session_state.audit_df], ignore_index=True)
    
    # Provide feedback to the user and server logs
    print(f"AUDIT LOGGED: User '{user}' -> Action '{action}' for Record '{record_id}'")
    st.toast(f"Action Logged: {action}", icon="📝")
