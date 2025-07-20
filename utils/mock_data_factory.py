# utils/mock_data_factory.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MockDataFactory:
    """
    A centralized factory for generating a complete, cohesive, and realistic
    set of mock data for the entire VERITAS application.
    
    Attributes:
        hplc_df (pd.DataFrame): Core HPLC results data with injected anomalies.
        deviations_df (pd.DataFrame): Deviations linked to anomalies in hplc_df.
        stability_df (pd.DataFrame): Comprehensive stability data for multiple lots.
        audit_df (pd.DataFrame): Rich audit trail referencing real records.
        gantt_df (pd.DataFrame): Data for program management Gantt charts.
    """
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
        
        # Generate data in a dependent sequence for cohesion
        self.hplc_df = self._generate_hplc_data(num_samples=500)
        self.deviations_df = self._generate_deviations_data(self.hplc_df)
        self.stability_df = self._generate_stability_data()
        self.audit_df = self._generate_audit_trail(self.hplc_df, self.deviations_df)
        self.gantt_df = self._generate_gantt_data()

    def _generate_hplc_data(self, num_samples=500):
        """Generates realistic HPLC data with intentional anomalies for QC."""
        start_time = datetime(2024, 4, 1)
        data = {
            'sample_id': [f'SMP-{1000+i}' for i in range(num_samples)],
            'batch_id': self.rng.choice(['B01-A', 'B01-B', 'B02-A', 'B02-B', 'B03-A'], size=num_samples),
            'study_id': self.rng.choice(['VX-809-PK-01', 'VX-561-Tox-03', 'VX-121-Stab-02', 'VX-984-Form-05'], size=num_samples, p=[0.3, 0.3, 0.2, 0.2]),
            'injection_time': pd.to_datetime([start_time + timedelta(hours=1.5*i) for i in range(num_samples)]),
            'Purity': self.rng.normal(loc=99.5, scale=0.2, size=num_samples),
            'Aggregate Content': self.rng.normal(loc=0.5, scale=0.1, size=num_samples),
            'Main Impurity': self.rng.normal(loc=0.2, scale=0.05, size=num_samples),
            'Bio-activity': self.rng.normal(loc=105, scale=5, size=num_samples),
            'instrument_id': self.rng.choice(['HPLC-01', 'HPLC-02', 'HPLC-03', 'UPLC-01'], size=num_samples, p=[0.4, 0.3, 0.15, 0.15]),
            'analyst': self.rng.choice(['A. Turing', 'M. Curie', 'R. Franklin', 'L. Meitner'], size=num_samples)
        }
        df = pd.DataFrame(data)

        # --- Inject Realistic Anomalies ---
        # 1. Out-of-Spec (OOS) result
        df.loc[10, 'Purity'] = 97.8 
        # 2. Missing metadata
        df.loc[25, 'batch_id'] = np.nan
        # 3. Instrument drift simulation
        hplc03_indices = df[df['instrument_id'] == 'HPLC-03'].index
        drift_factor = np.linspace(0, 0.35, len(hplc03_indices))
        df.loc[hplc03_indices, 'Main Impurity'] += drift_factor
        # 4. Analyst entry error
        df.loc[50, 'Bio-activity'] = 205.0
        
        # Clip values to be realistic post-anomaly injection
        df['Purity'] = df['Purity'].clip(97.0, 100)
        df['Aggregate Content'] = df['Aggregate Content'].clip(0, 1)
        df['Main Impurity'] = df['Main Impurity'].clip(0, 1.0)
        return df

    def _generate_deviations_data(self, hplc_df):
        """Generates deviation records linked to actual anomalies in HPLC data."""
        deviations = []
        
        # Deviation for the OOS Purity result
        oos_sample = hplc_df.iloc[10]
        deviations.append({
            "id": "DEV-001", "title": f"OOS Result in {oos_sample['study_id']} Purity Assay", 
            "status": "New", "priority": "High", "linked_record": oos_sample['sample_id']
        })

        # Deviation for instrument drift
        deviations.append({
            "id": "DEV-002", "title": "Instrument HPLC-03 Calibration Drift Detected", 
            "status": "In Progress", "priority": "Medium", "linked_record": "HPLC-03"
        })
        
        # A few generic deviations
        deviations.append({
            "id": "DEV-003", "title": "TAT Breach for Lot B02-A", 
            "status": "In Progress", "priority": "Medium", "linked_record": "B02-A"
        })
        deviations.append({
            "id": "DEV-004", "title": "Contamination in Stability Chamber 3", 
            "status": "Pending QA", "priority": "High", "linked_record": "STAB-CH-03"
        })
        deviations.append({
            "id": "DEV-005", "title": "Logbook entry missing for UPLC-01", 
            "status": "New", "priority": "Low", "linked_record": "UPLC-01"
        })
        
        return pd.DataFrame(deviations)

    def _generate_stability_data(self):
        """Generates a single, comprehensive stability dataset for multiple lots."""
        data = []
        products = {'VX-561': (99.5, 0.1), 'VX-809': (99.8, 0.05)}
        lots = ['A202301', 'A202302', 'B202301']
        timepoints = [0, 3, 6, 9, 12, 18, 24]

        for product, (p_start, i_start) in products.items():
            for lot in lots:
                seed = hash(f"{product}{lot}") % (2**32 - 1)
                lot_rng = np.random.default_rng(seed)
                for t in timepoints:
                    purity = p_start - (t * lot_rng.uniform(0.05, 0.08)) - lot_rng.uniform(0, 0.1)
                    impurity = i_start + (t * lot_rng.uniform(0.01, 0.02)) + lot_rng.uniform(0, 0.05)
                    data.append({
                        'product_id': product,
                        'lot_id': lot,
                        'Timepoint (Months)': t, 
                        'Purity (%)': purity, 
                        'Main Impurity (%)': impurity
                    })
        return pd.DataFrame(data)

    def _generate_audit_trail(self, hplc_df, deviations_df, num_entries=300):
        """Generates a rich audit trail linked to actual data records."""
        users = ['DTE-System', 'A. Turing', 'R. Franklin', 'QA.Bot', 'M. Curie', 'S. Director', 'Admin']
        actions = ['User Login', 'Data Fetched', 'Report Generated', 'Deviation Status Changed', 
                   'Stability Plot Viewed', 'E-Signature Applied', 'Data Exported', 'File Ingested']
        
        # Create a pool of realistic record IDs from actual data
        record_ids = hplc_df['sample_id'].tolist() + deviations_df['id'].tolist() + ['system_config', 'user_roles']
        
        log = []
        for i in range(num_entries):
            action = self.rng.choice(actions)
            user = self.rng.choice(users)
            record_id = self.rng.choice(record_ids)
            details = ""
            if action == 'Deviation Status Changed' and 'DEV' in record_id:
                details = f"Status changed from 'In Progress' to 'Pending QA'."
            elif action == 'Report Generated':
                details = f"Generated PDF summary for Study: {self.rng.choice(hplc_df['study_id'].unique())}"
            elif action == 'E-Signature Applied':
                details = "User signed off on report 'RPT-101' for Author Approval."
            
            log.append({
                'Timestamp': datetime.now() - timedelta(hours=i * 1.3, minutes=self.rng.integers(0, 59)),
                'User': user,
                'Action': action,
                'Record ID': record_id,
                'Details': details if details else f"Routine system operation for {record_id}."
            })
        return pd.DataFrame(log).sort_values('Timestamp', ascending=False).reset_index(drop=True)

    def _generate_gantt_data(self):
        """Generates mock data for the program management Gantt chart."""
        data = [
            dict(Program="VX-770 (CFTR)", Start='2023-01-15', Finish='2023-06-30', Status='Completed', Risk='Low'),
            dict(Program="VX-809 (CFTR)", Start='2023-03-01', Finish='2023-09-15', Status='Completed', Risk='Low'),
            dict(Program="VX-561 (AATD)", Start='2023-07-01', Finish='2024-01-20', Status='In Progress', Risk='Medium'),
            dict(Program="VX-121 (Pain)", Start='2023-10-10', Finish='2024-05-30', Status='In Progress', Risk='High'),
        ]
        return pd.DataFrame(data)
