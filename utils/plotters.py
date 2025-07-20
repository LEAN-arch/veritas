# utils/plotters.py
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

# Import the centralized theme and color palette
from utils.config import VERITAS_THEME, VERTEX_COLORS

# --- Universal Helper ---
def create_empty_figure(message: str) -> go.Figure:
    """Creates a standardized empty figure with a message."""
    fig = go.Figure()
    fig.update_layout(
        template=VERITAS_THEME,
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{'text': message, 'xref': 'paper', 'yref': 'paper', 'showarrow': False, 'font': {'size': 16}}]
    )
    return fig

# --- Leadership & KPI Plots ---

def plot_kpi_sankey(data: dict) -> go.Figure:
    """Creates a Sankey diagram from a dictionary of flow data."""
    if not all(k in data for k in ['ingested', 'passed', 'failed']):
        return create_empty_figure("Sankey data is missing.")

    passed_to_report = data['passed'] * 0.9  # 90% of passed data goes to reporting
    
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=0.5),
            label=["Raw Data Ingested", "QC Engine", "Passed QC", "Failed QC", "Regulatory Reporting", "Investigation"],
            color=[VERTEX_COLORS['blue'], VERTEX_COLORS['lightblue'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['blue'], VERTEX_COLORS['gray']]
        ),
        link=dict(
            source=[0, 1, 1, 2, 3],
            target=[1, 2, 3, 4, 5],
            value=[data['ingested'], data['passed'], data['failed'], passed_to_report, data['failed']],
            color=[VERTEX_COLORS['gray'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['lightblue'], f"rgba({int(VERTEX_COLORS['orange'][1:3], 16)}, {int(VERTEX_COLORS['orange'][3:5], 16)}, {int(VERTEX_COLORS['orange'][5:7], 16)}, 0.4)"]
        )
    ))
    fig.update_layout(title_text="<b>Data Package Flow & Yield</b>", template=VERITAS_THEME, height=350)
    return fig

def plot_gantt_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a Gantt chart for program timelines."""
    if df.empty:
        return create_empty_figure("No Gantt chart data.")
    
    color_map = {
        'Completed': VERTEX_COLORS['green'], 
        'In Progress': VERTEX_COLORS['orange'], 
        'On Track': VERTEX_COLORS['lightblue'], 
        'Planned': VERTEX_COLORS['gray']
    }
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Program", color="Status", 
                      title="<b>Major Program Timelines & Submission Risk</b>", 
                      color_discrete_map=color_map, hover_data=['Risk'])
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(template=VERITAS_THEME, height=350)
    return fig

def plot_pareto_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a Pareto chart from a frequency DataFrame."""
    if df.empty or 'Frequency' not in df.columns or 'Error Type' not in df.columns:
        return create_empty_figure("Invalid data for Pareto chart.")
        
    df_sorted = df.sort_values(by='Frequency', ascending=False)
    df_sorted['cumulative_percentage'] = df_sorted['Frequency'].cumsum() / df_sorted['Frequency'].sum() * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_sorted['Error Type'], y=df_sorted['Frequency'], name='Error Count', marker_color=VERTEX_COLORS['orange']))
    fig.add_trace(go.Scatter(x=df_sorted['Error Type'], y=df_sorted['cumulative_percentage'], name='Cumulative %', yaxis='y2', mode='lines+markers'))
    
    fig.update_layout(
        title='<b>Pareto Analysis of QC Failure Hotspots</b>',
        xaxis_title='Error Type',
        yaxis=dict(title='Frequency'),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', range=[0, 105]),
        template=VERITAS_THEME, height=350
    )
    return fig

# --- Statistical & QC Plots ---

def plot_historical_control_chart(df: pd.DataFrame, cqa: str, date_range: tuple) -> go.Figure:
    """Creates a historical I-MR control chart for a selected CQA."""
    df_filtered = df[(df['injection_time'] >= pd.to_datetime(date_range[0])) & (df['injection_time'] <= pd.to_datetime(date_range[1]))].copy()
    
    if len(df_filtered) < 2:
        return create_empty_figure(f"Not enough data for {cqa} in selected range.")

    mean = df_filtered[cqa].mean()
    std_dev = df_filtered[cqa].std()
    ucl = mean + 3 * std_dev
    lcl = mean - 3 * std_dev

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered['injection_time'], y=df_filtered[cqa], mode='lines+markers', name=cqa))
    fig.add_hline(y=mean, line_dash="dash", line_color=VERTEX_COLORS['green'], annotation_text="Mean")
    fig.add_hline(y=ucl, line_dash="dot", line_color=VERTEX_COLORS['red'], annotation_text="UCL (3σ)")
    fig.add_hline(y=lcl, line_dash="dot", line_color=VERTEX_COLORS['red'], annotation_text="LCL (3σ)")
    
    fig.update_layout(title=f"<b>Control Chart (I-Chart) for {cqa}</b>", xaxis_title="Date", yaxis_title="Value", showlegend=False, template=VERITAS_THEME, height=350)
    return fig

def plot_process_capability(df: pd.DataFrame, cqa: str, lsl: float, usl: float, cpk: float) -> go.Figure:
    """Displays a process capability histogram with calculated Cpk."""
    if cqa not in df.columns:
        return create_empty_figure(f"CQA '{cqa}' not in data.")
        
    data = df[cqa].dropna()
    if data.empty:
        return create_empty_figure(f"No data for {cqa}.")
    
    mean = data.mean()
    fig = px.histogram(df, x=cqa, nbins=30, title=f"<b>Process Capability for {cqa} | Cpk: {cpk:.2f}</b>")
    
    if lsl is not None: fig.add_vline(x=lsl, line_dash="solid", line_color=VERTEX_COLORS['red'], annotation_text="LSL")
    if usl is not None: fig.add_vline(x=usl, line_dash="solid", line_color=VERTEX_COLORS['red'], annotation_text="USL")
    fig.add_vline(x=mean, line_dash="dash", line_color=VERTEX_COLORS['green'], annotation_text="Mean")
    
    fig.update_layout(template=VERITAS_THEME, height=350)
    return fig

def plot_stability_trend(df: pd.DataFrame, assay: str, spec_limits: dict) -> go.Figure:
    """Plots a stability trend chart with specification limits."""
    if df.empty or assay not in df.columns:
        return create_empty_figure(f"No data to plot for {assay}.")

    lsl = spec_limits.get('LSL')
    usl = spec_limits.get('USL')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Timepoint (Months)'], y=df[assay], mode='lines+markers', name=assay))
    
    if lsl is not None:
        fig.add_trace(go.Scatter(x=df['Timepoint (Months)'], y=[lsl]*len(df), mode='lines', name='LSL', line=dict(color=VERTEX_COLORS['red'], dash='solid')))
    if usl is not None:
        fig.add_trace(go.Scatter(x=df['Timepoint (Months)'], y=[usl]*len(df), mode='lines', name='USL', line=dict(color=VERTEX_COLORS['red'], dash='solid')))
        
    fig.update_layout(title=f"<b>Stability Trend for {assay}</b>", xaxis_title="Timepoint (Months)", yaxis_title="Value", template=VERITAS_THEME, height=400)
    return fig

# --- Missing Plot Functions (Now Implemented) ---

def plot_anova_results(df: pd.DataFrame, value_col: str, group_col: str) -> go.Figure:
    """Creates a box plot for ANOVA analysis."""
    if df.empty or value_col not in df.columns or group_col not in df.columns:
        return create_empty_figure("Invalid data for ANOVA plot.")
    fig = px.box(df, x=group_col, y=value_col, title=f"<b>Comparison of {value_col} by {group_col}</b>", points="all")
    fig.update_layout(template=VERITAS_THEME)
    return fig

def plot_qq(data: pd.Series) -> go.Figure:
    """Generates a Q-Q plot to test for normality."""
    if data.empty:
        return create_empty_figure("No data for Q-Q plot.")
    qq_data = stats.probplot(data, dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qq_data[0][0], y=qq_data[0][1], mode='markers', name='Data'))
    fig.add_trace(go.Scatter(x=qq_data[0][0], y=qq_data[1][1] + qq_data[1][0]*qq_data[0][0], mode='lines', name='Fit'))
    fig.update_layout(title="<b>Q-Q Plot for Normality</b>", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", template=VERITAS_THEME)
    return fig

def plot_ml_anomaly_results(df: pd.DataFrame, x_col: str, y_col: str, labels: np.ndarray) -> go.Figure:
    """Plots the results of an anomaly detection model."""
    if df.empty:
        return create_empty_figure("No data for anomaly plot.")
    df_plot = df.copy()
    df_plot['Anomaly'] = labels
    df_plot['Anomaly'] = df_plot['Anomaly'].astype(str).replace({'1': 'Normal', '-1': 'Anomaly'})
    
    fig = px.scatter(df_plot, x=x_col, y=y_col, color='Anomaly',
                     color_discrete_map={'Normal': VERTEX_COLORS['blue'], 'Anomaly': VERTEX_COLORS['red']},
                     title=f"<b>Isolation Forest Anomaly Detection</b>",
                     hover_data=df.columns)
    fig.update_layout(template=VERITAS_THEME)
    return fig
    
def plot_spc_chart(df: pd.DataFrame, value_col: str) -> go.Figure:
    """Creates a simple SPC (I-MR) chart."""
    return plot_historical_control_chart(df, value_col, (df['injection_time'].min(), df['injection_time'].max()))
