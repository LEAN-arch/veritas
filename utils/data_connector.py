# utils/data_connector.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- PHASE 1: Connect to Live Database ---
# SME EXPLANATION: This module simulates a connection to a live enterprise data warehouse.
# In a real-world scenario, this would use libraries like snowflake-connector-python or
# psycopg2 to execute SQL queries. For this simulation, the functions return pre-generated
# pandas DataFrames, but the function signatures and comments reflect how a live system
# would be architected. This demonstrates the "database access and query" skill.

@st.cache_data(ttl=3600)  # Cache data for 1 hour to simulate scheduled refreshes
def connect_to_db(connection_params: dict):
    """
    Simulates establishing a connection to a database.
    In a real app, this would return a live connection object.
    Here, it returns a success message to show the concept.
    """
    # Simulate connection latency
    import time
    time.sleep(0.5)
    # st.toast(f"Connected to {connection_params.get('database')} successfully.", icon="🌐")
    return "Simulated Connection Successful"

def fetch_hplc_data(connection) -> pd.DataFrame:
    """
    Simulates executing a SQL query to fetch the primary HPLC dataset.
    This replaces the previous 'create_mock_hplc_data' as the main data source.
    """
    # --- SIMULATED SQL QUERY ---
    # SELECT sample_id, batch_id, study_id, ... FROM prod.hplc_results WHERE injection_time >= '1 year ago'
    return create_mock_hplc_data(num_samples=500) # Using generator to create the data

def fetch_stability_data(connection, product: str, lot: str) -> pd.DataFrame:
    """
    Simulates fetching stability program data for a specific product and lot.
    """
    np.random.seed(hash(f"{product}{lot}") % (2**32 - 1)) # Seed for consistent data
    timepoints = [0, 3, 6, 9, 12, 18, 24]
    purity_start = 99.5
    impurity_start = 0.1
    
    data = []
    for t in timepoints:
        purity = purity_start - (t * np.random.uniform(0.05, 0.08)) - np.random.uniform(0, 0.1)
        impurity = impurity_start + (t * np.random.uniform(0.01, 0.02)) + np.random.uniform(0, 0.05)
        data.append({'Timepoint (Months)': t, 'Purity (%)': purity, 'Main Impurity (%)': impurity})
    
    return pd.DataFrame(data)

def fetch_deviations_data(connection) -> pd.DataFrame:
    """Simulates fetching data for the deviation management Kanban board."""
    return pd.DataFrame([
        {"id": "DEV-001", "title": "OOS Result in VX-561 Purity Assay", "status": "New", "priority": "High"},
        {"id": "DEV-002", "title": "Instrument HPLC-02 Calibration Drift", "status": "In Progress", "priority": "Medium"},
        {"id": "DEV-003", "title": "TAT Breach for Lot B02-A", "status": "In Progress", "priority": "Medium"},
        {"id": "DEV-004", "title": "Contamination in Stability Chamber 3", "status": "Pending QA", "priority": "High"},
        {"id": "DEV-005", "title": "Logbook entry missing for UPLC-01", "status": "New", "priority": "Low"},
    ])

# --- PHASE 1: Configuration Management ---
# SME EXPLANATION: This simulates fetching configuration from an external source (like a
# database table or a YAML file). This is a critical best practice that separates code
# from configuration, making the app maintainable and agile. A scientist could request a
# spec limit change, and it could be updated here without a new software release.

@st.cache_data(ttl=3600)
def fetch_app_config(connection):
    """
    Simulates loading application configuration from a database or config file.
    """
    return {
        "process_capability": {
            "cpk_target": 1.33,
            "available_cqas": ["Purity", "Aggregate Content", "Main Impurity", "Bio-activity"]
        },
        "stability_specs": {
            "Purity (%)": {"USL": None, "LSL": 98.0},
            "Main Impurity (%)": {"USL": 0.5, "LSL": None}
        },
        "tat_sla_days": 5
    }

# --- PHASE 1: Audit Trail Foundation ---
# SME EXPLANATION: These functions simulate writing to and reading from a centralized
# audit log database table. This is the cornerstone of GxP compliance.

def write_to_audit_log(connection, user: str, action: str, details: str):
    """
    Simulates writing a new entry to the audit_log table.
    In a real app, this would execute an INSERT SQL statement.
    """
    # In a real app, you would never show the full log in a toast, but this is for demo.
    log_entry = f"User '{user}' performed action '{action}'. Details: {details}"
    print(f"AUDIT LOGGED: {log_entry}") # Prints to console
    st.toast(f"Action Logged: {action}", icon="📝")

@st.cache_data(ttl=60) # Cache audit log for 1 minute
def fetch_audit_log(connection) -> pd.DataFrame:
    """Simulates fetching the entire audit log."""
    # This uses a generator for simplicity, but in production, it would be a SELECT query.
    return create_mock_audit_trail(num_entries=250)


# Helper function from original data_generator, kept for convenience in this module
def create_mock_hplc_data(num_samples=250):
    np.random.seed(42)
    start_time = datetime(2024, 4, 1)
    data = {
        'sample_id': [f'SMP-{1000+i}' for i in range(num_samples)],
        'batch_id': np.random.choice(['B01-A', 'B01-B', 'B02-A', 'B02-B', 'B03-A'], size=num_samples),
        'study_id': np.random.choice(['VX-809-PK-01', 'VX-561-Tox-03', 'VX-121-Stab-02', 'VX-984-Form-05'], size=num_samples, p=[0.3, 0.3, 0.2, 0.2]),
        'injection_time': pd.to_datetime([start_time + timedelta(hours=1.5*i) for i in range(num_samples)]),
        'Purity': np.random.normal(loc=99.5, scale=0.2, size=num_samples),
        'Aggregate Content': np.random.normal(loc=0.5, scale=0.1, size=num_samples),
        'Main Impurity': np.random.normal(loc=0.2, scale=0.05, size=num_samples),
        'Bio-activity': np.random.normal(loc=105, scale=5, size=num_samples),
        'instrument_id': np.random.choice(['HPLC-01', 'HPLC-02', 'HPLC-03', 'UPLC-01'], size=num_samples, p=[0.4, 0.3, 0.15, 0.15]),
        'analyst': np.random.choice(['A. Turing', 'M. Curie', 'R. Franklin', 'L. Meitner'], size=num_samples)
    }
    df = pd.DataFrame(data)
    # Clip values to be realistic
    df['Purity'] = df['Purity'].clip(98.5, 100)
    df['Aggregate Content'] = df['Aggregate Content'].clip(0, 1)
    df['Main Impurity'] = df['Main Impurity'].clip(0, 0.5)
    return df

def create_mock_audit_trail(num_entries=250):
    users = ['DTE-System', 'A. Turing', 'R. Franklin', 'QA.Bot', 'M. Curie', 'S. Director', 'Admin']
    actions = ['User Login', 'Data Fetched', 'Report Generated', 'Deviation Status Changed', 'Stability Plot Viewed', 'E-Signature Applied', 'Data Exported', 'Configuration Changed']
    records = [f'SMP-{np.random.randint(1000, 1250)}' for _ in range(num_entries)]
    records.extend([f'RPT-{np.random.randint(100, 150)}' for _ in range(num_entries)])
    records.extend(['user_roles', 'system_config', 'DEV-001', 'DEV-002'])
    
    log = []
    for i in range(num_entries):
        log.append({
            'Timestamp': datetime.now() - timedelta(hours=i*1.3, minutes=np.random.randint(0,59)),
            'User': np.random.choice(users),
            'Action': np.random.choice(actions),
            'Record ID': np.random.choice(records),
            'Details': f"Status changed from '{np.random.choice(['New', 'In Progress'])}' to '{np.random.choice(['In Progress', 'Pending QA'])}'."
        })
    return pd.DataFrame(log)
