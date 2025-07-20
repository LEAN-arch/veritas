# utils/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_mock_hplc_data(num_samples=50):
    """Generates realistic mock HPLC data with potential anomalies."""
    np.random.seed(42)
    data = {
        'sample_id': [f'SMP-{1000+i}' for i in range(num_samples)],
        'batch_id': np.random.choice(['B01-A', 'B01-B', 'B02-A'], size=num_samples),
        'injection_time': [datetime.now() - timedelta(minutes=15*i) for i in range(num_samples)],
        'analyte_concentration': np.random.normal(loc=100, scale=10, size=num_samples),
        'peak_area': np.random.normal(loc=5000, scale=500, size=num_samples),
        'retention_time': np.random.normal(loc=2.5, scale=0.1, size=num_samples),
        'instrument_id': np.random.choice(['HPLC-01', 'HPLC-02', 'HPLC-03'], size=num_samples),
        'analyst': np.random.choice(['A. Turing', 'M. Curie', 'R. Franklin'], size=num_samples)
    }
    df = pd.DataFrame(data)
    
    # Introduce some anomalies for QC to catch
    df.loc[5, 'analyte_concentration'] = 150 # Outlier
    df.loc[10, 'analyte_concentration'] = -5 # Invalid value
    df.loc[15, 'peak_area'] = np.nan # Missing value
    df.loc[20, 'retention_time'] = 3.1 # Process drift
    df.loc[25, 'batch_id'] = 'B01-C' # New batch
    
    return df

def get_program_gantt_data():
    """Generates mock data for the program management Gantt chart."""
    data = [
        dict(Program="VX-770 (CFTR)", Start='2023-01-15', Finish='2023-06-30', Status='Completed'),
        dict(Program="VX-809 (CFTR)", Start='2023-03-01', Finish='2023-09-15', Status='Completed'),
        dict(Program="VX-561 (AATD)", Start='2023-07-01', Finish='2024-01-20', Status='In Progress'),
        dict(Program="VX-121 (Pain)", Start='2023-10-10', Finish='2024-05-30', Status='In Progress'),
        dict(Program="VX-984 (DNA Repair)", Start='2024-01-05', Finish='2024-08-01', Status='On Track'),
        dict(Program="NextGen Gene Editing", Start='2024-03-01', Finish='2024-12-31', Status='Planned'),
    ]
    return pd.DataFrame(data)

def get_qc_error_data():
    """Generates mock data for the Pareto chart."""
    errors = {
        'Out of Spec Result': 45, 'Missing Metadata': 22, 'Instrument Drift': 15,
        'Invalid File Format': 8, 'Analyst Entry Error': 5, 'Checksum Mismatch': 3
    }
    return pd.DataFrame(list(errors.items()), columns=['Error Type', 'Frequency']).sort_values(by='Frequency', ascending=False)

def create_mock_audit_trail():
    """Generates a mock audit trail log."""
    users = ['DTE-System', 'A. Turing', 'R. Franklin', 'QA.Bot', 'M. Curie']
    actions = ['File Ingested', 'QC Rule Applied', 'Data Point Flagged', 'Discrepancy Resolved', 'Report Generated', 'E-Signature Applied']
    reasons = ['Routine processing', 'Value out of spec', 'Investigation required', 'Approved by Study Director', 'Scheduled run', 'End of study report']
    
    log = []
    for i in range(50):
        log.append({
            'Timestamp': datetime.now() - timedelta(hours=i*2.3),
            'User': np.random.choice(users),
            'Action': np.random.choice(actions),
            'Record ID': f'SMP-{np.random.randint(1000, 1050)}',
            'Details': f"Action performed on record.",
            '21 CFR 11 Justification': np.random.choice(reasons)
        })
    return pd.DataFrame(log)
