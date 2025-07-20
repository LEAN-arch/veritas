# utils/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_mock_hplc_data(num_samples=250, drift=True):
    """Generates highly realistic mock HPLC data with multiple studies, anomalies, and instrument drift."""
    np.random.seed(42)
    start_time = datetime(2024, 4, 1)
    data = {
        'sample_id': [f'SMP-{1000+i}' for i in range(num_samples)],
        'study_id': np.random.choice(['VX-809-PK-01', 'VX-561-Tox-03', 'VX-121-Stab-02', 'VX-984-Form-05'], size=num_samples, p=[0.3, 0.3, 0.2, 0.2]),
        'injection_time': [start_time + timedelta(hours=1.5*i) for i in range(num_samples)],
        'analyte_concentration': np.random.normal(loc=100, scale=8, size=num_samples),
        'peak_area': np.random.normal(loc=5000, scale=400, size=num_samples),
        'retention_time': np.random.normal(loc=2.5, scale=0.05, size=num_samples),
        'instrument_id': np.random.choice(['HPLC-01', 'HPLC-02', 'HPLC-03', 'UPLC-01'], size=num_samples, p=[0.4, 0.3, 0.15, 0.15]),
        'analyst': np.random.choice(['A. Turing', 'M. Curie', 'R. Franklin', 'L. Meitner'], size=num_samples)
    }
    df = pd.DataFrame(data)

    if drift:
        hplc03_indices = df[df['instrument_id'] == 'HPLC-03'].index
        drift_factor = np.linspace(0, 0.35, len(hplc03_indices))
        df.loc[hplc03_indices, 'retention_time'] += drift_factor

    df.loc[df.index[5], 'analyte_concentration'] = 180  # Obvious outlier
    df.loc[df.index[10], 'analyte_concentration'] = -12  # Invalid value
    df.loc[df.index[15], 'peak_area'] = np.nan  # Missing value
    df.loc[df.index[25], 'peak_area'] = 7500 # Subtle ML Anomaly
    df.loc[df.index[35], 'retention_time'] = 1.8 # Spec deviation
    return df

def create_plate_heatmap_data():
    """Generates 96-well plate data with edge effects."""
    data = np.random.rand(8, 12) * 100 + 20
    data[0, :] -= 15 # Top edge effect
    data[-1, :] -= 15 # Bottom edge effect
    data[:, 0] -= 15 # Left edge effect
    data[:, -1] -= 15 # Right edge effect
    data = np.clip(data, 0, 150)
    return pd.DataFrame(data, index=[chr(65+i) for i in range(8)], columns=range(1, 13))

def create_mock_audit_trail(num_entries=200):
    """Generates a rich, filterable audit trail."""
    users = ['DTE-System', 'A. Turing', 'R. Franklin', 'QA.Bot', 'M. Curie', 'S. Director', 'Admin']
    actions = ['File Ingested', 'QC Rule Applied', 'Data Point Flagged', 'Discrepancy Resolved', 'Report Generated', 'E-Signature Applied', 'User Login', 'Data Exported', 'Permission Changed']
    records = [f'SMP-{np.random.randint(1000, 1250)}' for _ in range(num_entries)]
    records.extend([f'RPT-{np.random.randint(100, 150)}' for _ in range(num_entries)])
    records.extend(['user_roles', 'system_config'])
    
    log = []
    for i in range(num_entries):
        log.append({
            'Timestamp': datetime.now() - timedelta(hours=i*1.3, minutes=np.random.randint(0,59)),
            'User': np.random.choice(users),
            'Action': np.random.choice(actions),
            'Record ID': np.random.choice(records),
            'Old Value': f'{np.random.rand():.2f}',
            'New Value': f'{np.random.rand():.2f}',
            '21 CFR 11 Justification': np.random.choice(["Routine system operation.", "Analyst correction.", "Scheduled task.", "User action."])
        })
    return pd.DataFrame(log)
    
# Keep other generator functions from previous version: get_program_gantt_data, get_qc_error_data, get_ingestion_history, create_dose_response_data
def get_program_gantt_data():
    data = [dict(Program="VX-770 (CFTR)", Start='2023-01-15', Finish='2023-06-30', Status='Completed', Risk='Low'), dict(Program="VX-809 (CFTR)", Start='2023-03-01', Finish='2023-09-15', Status='Completed', Risk='Low'), dict(Program="VX-561 (AATD)", Start='2023-07-01', Finish='2024-01-20', Status='In Progress', Risk='Medium'), dict(Program="VX-121 (Pain)", Start='2023-10-10', Finish='2024-05-30', Status='In Progress', Risk='High'), dict(Program="VX-984 (DNA Repair)", Start='2024-01-05', Finish='2024-08-01', Status='On Track', Risk='Medium'), dict(Program="NextGen Gene Editing", Start='2024-03-01', Finish='2024-12-31', Status='Planned', Risk='Low')]
    return pd.DataFrame(data)
def get_qc_error_data():
    errors = {'Out of Spec Result': 45, 'Missing Metadata': 22, 'Instrument Drift': 15, 'Invalid File Format': 8, 'Analyst Entry Error': 5, 'Checksum Mismatch': 3}
    return pd.DataFrame(list(errors.items()), columns=['Error Type', 'Frequency']).sort_values(by='Frequency', ascending=False)
def get_ingestion_history():
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    success_rate = 95 + np.random.randn(30).cumsum() * 0.1
    success_rate = np.clip(success_rate, 90, 99.8)
    files_processed = np.random.randint(500, 800, 30)
    return pd.DataFrame({'Date': dates, 'Success Rate (%)': success_rate, 'Files Processed': files_processed})
def create_dose_response_data():
    doses = np.logspace(-9, -4, 15)
    ec50 = 1e-7
    response = 100 / (1 + (ec50 / doses))
    noise = np.random.normal(0, 5, len(doses))
    return pd.DataFrame({'Dose (M)': doses, 'Response (%)': np.clip(response + noise, 0, 105)})
