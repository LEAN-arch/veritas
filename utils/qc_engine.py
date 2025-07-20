# utils/qc_engine.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats

# --- This module contains pure, non-Streamlit backend QC/ML functions ---

def apply_qc_rules(df: pd.DataFrame, rules_config: dict, app_config: dict) -> pd.DataFrame:
    """
    Applies a set of deterministic rules to a dataframe and returns a report of discrepancies.
    This is the core of the rule-based QC engine.

    Args:
        df (pd.DataFrame): The data to validate.
        rules_config (dict): A dictionary of booleans indicating which rules to apply.
        app_config (dict): The central application configuration dictionary for spec limits.

    Returns:
        pd.DataFrame: A DataFrame of found discrepancies.
    """
    discrepancies = []
    
    # Rule 1: Check for any missing (null) values in key columns
    if rules_config.get('check_nulls', False):
        key_cols = ['sample_id', 'batch_id', 'Purity', 'Bio-activity']
        nulls = df[df[key_cols].isnull().any(axis=1)]
        for _, row in nulls.iterrows():
            discrepancies.append({
                'sample_id': row['sample_id'], 
                'Issue': 'Missing Value', 
                'Details': f"Null found in column(s): {row[key_cols].index[row[key_cols].isnull()].tolist()}"
            })
            
    # Rule 2: Check for physically impossible negative values
    if rules_config.get('check_negatives', False) and 'Bio-activity' in df.columns:
        negatives = df[df['Bio-activity'] < 0]
        for _, row in negatives.iterrows():
            discrepancies.append({
                'sample_id': row['sample_id'], 
                'Issue': 'Negative Value', 
                'Details': f"Bio-activity is {row['Bio-activity']:.2f}"
            })

    # Rule 3: Check CQA is within spec limits defined in the central config
    if rules_config.get('check_spec_limits', False):
        # Example check for 'Main Impurity'
        cqa_to_check = 'Main Impurity'
        spec_limits_all = app_config.get('process_capability', {}).get('spec_limits', {})
        specs = spec_limits_all.get(cqa_to_check)
        
        if specs and cqa_to_check in df.columns:
            lsl = specs.get('LSL')
            usl = specs.get('USL')
            
            # Filter for values outside the defined range (handles one-sided specs)
            oor_conditions = []
            if lsl is not None:
                oor_conditions.append(df[cqa_to_check] < lsl)
            if usl is not None:
                oor_conditions.append(df[cqa_to_check] > usl)
            
            if oor_conditions:
                # Combine conditions with OR logic
                oor_mask = pd.concat(oor_conditions, axis=1).any(axis=1)
                oor_df = df[oor_mask]
                
                for _, row in oor_df.iterrows():
                    details = f"{cqa_to_check} is {row[cqa_to_check]:.2f}, outside spec of LSL: {lsl}, USL: {usl}"
                    discrepancies.append({
                        'sample_id': row['sample_id'],
                        'Issue': 'Out of Specification',
                        'Details': details
                    })

    return pd.DataFrame(discrepancies) if discrepancies else pd.DataFrame(columns=['sample_id', 'Issue', 'Details'])


def perform_normality_test(data_series: pd.Series) -> dict:
    """
    Performs a Shapiro-Wilk test for normality on a data series.

    Args:
        data_series (pd.Series): The data to test.

    Returns:
        dict: A dictionary with the test statistic, p-value, and conclusion.
    """
    if data_series.empty or len(data_series.dropna()) < 3:
        return {'statistic': None, 'p_value': None, 'conclusion': 'Not enough data'}
    
    stat, p_value = stats.shapiro(data_series.dropna())
    conclusion = "Data appears to be normally distributed (p > 0.05)." if p_value > 0.05 \
                 else "Data does not appear to be normally distributed (p <= 0.05)."
                 
    return {'statistic': stat, 'p_value': p_value, 'conclusion': conclusion}


def run_anomaly_detection(df: pd.DataFrame, x_col: str, y_col: str, contamination: float) -> tuple:
    """
    Runs the IsolationForest ML model on two specified columns.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        x_col (str): The column name for the x-axis.
        y_col (str): The column name for the y-axis.
        contamination (float): The estimated proportion of outliers in the data.

    Returns:
        tuple: A tuple containing the prediction labels and the DataFrame used for fitting.
    """
    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return None, None

    data_to_fit = df[[x_col, y_col]].dropna()
    
    if len(data_to_fit) < 2:
        return None, None
        
    model = IsolationForest(contamination=contamination, random_state=42)
    predictions = model.fit_predict(data_to_fit)
    
    return predictions, data_to_fit
