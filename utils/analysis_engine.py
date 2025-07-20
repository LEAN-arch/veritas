# utils/analysis_engine.py
import pandas as pd
import numpy as np
from scipy.stats import linregress

# --- This module contains pure, non-Streamlit backend analysis functions ---

def calculate_cpk(data_series: pd.Series, lsl: float, usl: float) -> float:
    """
    Calculates the Process Capability Index (Cpk) for a given data series.

    Args:
        data_series (pd.Series): The data to analyze.
        lsl (float): The Lower Specification Limit.
        usl (float): The Upper Specification Limit.

    Returns:
        float: The calculated Cpk value, or 0.0 if calculation is not possible.
    """
    if data_series.empty or data_series.std() == 0:
        return 0.0

    mean = data_series.mean()
    std_dev = data_series.std()
    
    # Handle one-sided specifications
    cpu = (usl - mean) / (3 * std_dev) if usl is not None else np.inf
    cpl = (mean - lsl) / (3 * std_dev) if lsl is not None else np.inf
    
    cpk = min(cpu, cpl)
    return cpk

def calculate_stability_projection(df: pd.DataFrame, time_col: str, value_col: str, spec_limit: float) -> dict:
    """
    Performs a linear regression on stability data to project shelf life.
    NOTE: This is a simplified model for demonstration. Real stability analysis
          (e.g., ICH Q1E) can be more complex.

    Args:
        df (pd.DataFrame): The stability data, containing time and value columns.
        time_col (str): The name of the timepoint column.
        value_col (str): The name of the measurement column (e.g., 'Purity (%)').
        spec_limit (float): The specification limit (LSL or USL) to project against.

    Returns:
        dict: A dictionary containing the slope, intercept, and estimated months to spec limit.
              Returns an empty dict if projection is not possible or meaningful.
    """
    if df.empty or len(df) < 2:
        return {}

    # Ensure data is numeric
    time_data = pd.to_numeric(df[time_col], errors='coerce')
    value_data = pd.to_numeric(df[value_col], errors='coerce')
    
    # Drop any rows where coercion failed
    valid_data = pd.DataFrame({'time': time_data, 'value': value_data}).dropna()
    
    if len(valid_data) < 2:
        return {}

    slope, intercept, _, _, _ = linregress(valid_data['time'], valid_data['value'])

    projection = {}
    
    # Project time to hit a lower spec limit (degrading trend)
    if slope < 0 and value_data.mean() > spec_limit:
        if slope != 0:
            months_to_spec = (spec_limit - intercept) / slope
            projection = {'slope': slope, 'intercept': intercept, 'months_to_spec': months_to_spec}
    # Project time to hit an upper spec limit (increasing trend)
    elif slope > 0 and value_data.mean() < spec_limit:
        if slope != 0:
            months_to_spec = (spec_limit - intercept) / slope
            projection = {'slope': slope, 'intercept': intercept, 'months_to_spec': months_to_spec}

    return projection


def calculate_dqs(df: pd.DataFrame, rules: dict) -> float:
    """
    Calculates a Data Quality Score (DQS) based on a set of rules.
    This example calculates it based on the percentage of purity results passing a threshold.
    
    Args:
        df (pd.DataFrame): The dataframe to score.
        rules (dict): A dictionary defining the rule, e.g., {'purity_threshold': 98.0}
    
    Returns:
        float: The DQS score from 0 to 100.
    """
    if df.empty or 'Purity' not in df.columns or 'purity_threshold' not in rules:
        return 100.0 # Default to 100 if not applicable

    passing_rows = (df['Purity'] >= rules['purity_threshold']).sum()
    total_rows = len(df)
    
    return 100 * (passing_rows / total_rows) if total_rows > 0 else 100.0
