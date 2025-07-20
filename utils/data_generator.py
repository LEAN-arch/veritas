# utils/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_mock_hplc_data(num_samples=100, drift=True):
    """Generates realistic mock HPLC data with potential anomalies and long-term drift."""
    np.random.seed(42)
    start_time = datetime(2024, 5, 1)
    data = {
        'sample_id': [f'SMP-{1000+i}' for i in range(num_samples)],
        'study_id': np.random.choice(['VX-809-PK-01', 'VX-561-Tox-03', 'VX-121-Stab-02'], size=num_samples),
        'injection_time': [start_time + timedelta(hours=2*i) for i in range(num_samples)],
        'analyte_concentration': np.random.normal(loc=100, scale=8, size=num_samples),
        'peak_area': np.random.normal(loc=5000, scale=400, size=num_samples),
        'retention_time': np.random.normal(loc=2.5, scale=0.05, size=num_samples),
        'instrument_id': np.random.choice(['HPLC-01', 'HPLC-02', 'HPLC-03'], size=num_samples, p=[0.5, 0.3, 0.2]),
        'analyst': np.random.choice(['A. Turing', 'M. Curie', 'R. Franklin'], size=num_samples)
    }
    df = pd.DataFrame(data)

    # Introduce long-term instrument drift for HPLC-03 (a common real-world problem)
    if drift:
        hplc03_indices = df[df['instrument_id'] == 'HPLC-03'].index
        drift_factor = np.linspace(0, 0.25, len(hplc03_indices))
        df.loc[hplc03_indices, 'retention_time'] += drift_factor

    # Introduce specific anomalies for QC to catch
    df.loc[df.index[5], 'analyte_concentration'] = 150  # Outlier
    df.loc[df.index[10], 'analyte_concentration'] = -5  # Invalid value
    df.loc[df.index[15], 'peak_area'] = np.nan  # Missing value
    df.loc[df.index[25], 'peak_area'] = 6500 # ML Anomaly
    
    return df

def create_dose_response_data():
    """Generates data for a classic dose-response curve."""
    doses = np.logspace(-9, -4, 15)
    ec50 = 1e-7
    response = 100 / (1 + (ec50 / doses))
    noise = np.random.normal(0, 5, len(doses))
    return pd.DataFrame({'Dose (M)': doses, 'Response (%)': np.clip(response + noise, 0, 105)})

def get_program_gantt_data():
    """Generates mock data for the program management Gantt chart."""
    data = [
        dict(Program="VX-770 (CFTR)", Start='2023-01-15', Finish='2023-06-30', Status='Completed', Risk='Low'),
        dict(Program="VX-809 (CFTR)", Start='2023-03-01', Finish='2023-09-15', Status='Completed', Risk='Low'),
        dict(Program="VX-561 (AATD)", Start='2023-07-01', Finish='2024-01-20', Status='In Progress', Risk='Medium'),
        dict(Program="VX-121 (Pain)", Start='2023-10-10', Finish='2024-05-30', Status='In Progress', Risk='High'),
        dict(Program="VX-984 (DNA Repair)", Start='2024-01-05', Finish='2024-08-01', Status='On Track', Risk='Medium'),
        dict(Program="NextGen Gene Editing", Start='2024-03-01', Finish='2024-12-31', Status='Planned', Risk='Low'),
    ]
    return pd.DataFrame(data)

def get_qc_error_data():
    """Generates mock data for the Pareto chart."""
    errors = {
        'Out of Spec Result': 45, 'Missing Metadata': 22, 'Instrument Drift': 15,
        'Invalid File Format': 8, 'Analyst Entry Error': 5, 'Checksum Mismatch': 3
    }
    return pd.DataFrame(list(errors.items()), columns=['Error Type', 'Frequency']).sort_values(by='Frequency', ascending=False)

def create_mock_audit_trail(num_entries=100):
    """Generates a richer mock audit trail log."""
    users = ['DTE-System', 'A. Turing', 'R. Franklin', 'QA.Bot', 'M. Curie', 'S. Director']
    actions = ['File Ingested', 'QC Rule Applied', 'Data Point Flagged', 'Discrepancy Resolved', 'Report Generated', 'E-Signature Applied', 'User Login', 'Data Exported']
    records = [f'SMP-{np.random.randint(1000, 1050)}' for _ in range(num_entries)]
    records.extend([f'RPT-{np.random.randint(100, 150)}' for _ in range(num_entries)])
    
    log = []
    for i in range(num_entries):
        log.append({
            'Timestamp': datetime.now() - timedelta(hours=i*1.3, minutes=np.random.randint(0,59)),
            'User': np.random.choice(users),
            'Action': np.random.choice(actions),
            'Record ID': np.random.choice(records),
            'Details': f"Change from 'N/A' to '{np.random.rand():.2f}'.",
            '21 CFR 11 Justification': "Routine system operation."
        })
    return pd.DataFrame(log)

def get_ingestion_history():
    """Generates data for historical ingestion metrics."""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    success_rate = 95 + np.random.randn(30).cumsum() * 0.1
    success_rate = np.clip(success_rate, 90, 99.8)
    files_processed = np.random.randint(500, 800, 30)
    return pd.DataFrame({'Date': dates, 'Success Rate (%)': success_rate, 'Files Processed': files_processed})
