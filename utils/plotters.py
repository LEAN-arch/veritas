# utils/plotters.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

# Vertex brand colors for consistent look and feel
VERTEX_COLORS = {
    'blue': '#003DA5', 'lightblue': '#00A3E0', 'green': '#00B140', 
    'orange': '#F37021', 'gray': '#6A737B', 'red': '#D4000F'
}

def plot_sankey_flow():
    """Creates a Sankey diagram for the DTE Leadership dashboard."""
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=0.5),
            label=["Raw Data Ingested", "QC Engine", "Passed QC", "Failed QC", "Regulatory Reporting", "Investigation"],
            color=[VERTEX_COLORS['blue'], VERTEX_COLORS['lightblue'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['blue'], VERTEX_COLORS['gray']]
        ),
        link=dict(
            source=[0, 1, 1, 2, 3], 
            target=[1, 2, 3, 4, 5],
            value=[100, 85, 15, 85, 15],
            color=[VERTEX_COLORS['gray'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['lightblue'], 'rgba(243, 112, 33, 0.4)']
        )
    ))
    fig.update_layout(title_text="<b>Data Package Flow & Yield</b>", font_size=12, height=350)
    return fig

def plot_gantt_chart(df):
    """Creates a Gantt chart for program timelines."""
    color_map = {'Completed': VERTEX_COLORS['green'], 'In Progress': VERTEX_COLORS['orange'], 
                 'On Track': VERTEX_COLORS['lightblue'], 'Planned': VERTEX_COLORS['gray']}
    fig = px.timeline(
        df, x_start="Start", x_end="Finish", y="Program", color="Status",
        title="<b>Major Data Package Timelines by Program</b>",
        color_discrete_map=color_map, hover_data=['Risk']
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(legend_title="Status", height=350)
    return fig

def plot_levey_jennings(df, value_col='analyte_concentration', time_col='injection_time'):
    """Creates a Levey-Jennings chart, a staple in clinical lab QC."""
    df_sorted = df.sort_values(by=time_col).reset_index()
    mean = df_sorted[value_col].mean()
    std = df_sorted[value_col].std()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted[time_col], y=df_sorted[value_col], mode='lines+markers', name='QC Sample', marker_color=VERTEX_COLORS['blue']))
    
    # Add control limit lines
    for i in range(1, 4):
        fig.add_hline(y=mean + i*std, line_dash="dot", line_color=VERTEX_COLORS['orange'] if i < 3 else VERTEX_COLORS['red'])
        fig.add_hline(y=mean - i*std, line_dash="dot", line_color=VERTEX_COLORS['orange'] if i < 3 else VERTEX_COLORS['red'])
    fig.add_hline(y=mean, line_dash="solid", line_color=VERTEX_COLORS['green'], annotation_text="Mean")

    fig.update_layout(
        title=f"<b>Levey-Jennings Chart for {value_col}</b>",
        xaxis_title="Time", yaxis_title="Value", height=300
    )
    return fig

def plot_pareto_chart(df):
    """Creates a Pareto chart for QC error analysis."""
    df['cumulative_percentage'] = df['Frequency'].cumsum() / df['Frequency'].sum() * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Error Type'], y=df['Frequency'], name='Error Count', marker_color=VERTEX_COLORS['orange']))
    fig.add_trace(go.Scatter(x=df['Error Type'], y=df['cumulative_percentage'], name='Cumulative %', yaxis='y2', mode='lines+markers', line=dict(color=VERTEX_COLORS['blue'])))
    
    fig.update_layout(
        title='<b>Pareto Analysis of QC Failures (80/20 Rule)</b>',
        xaxis_title='Error Type',
        yaxis=dict(title='Frequency'),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=350
    )
    return fig

def plot_dose_response(df):
    """Plots a semi-log dose-response curve."""
    fig = px.scatter(df, x='Dose (M)', y='Response (%)', log_x=True,
                     title='<b>Dose-Response Curve for Lead Compound</b>')
    # Add a smooth line (simple moving average for visualization)
    df_sorted = df.sort_values('Dose (M)')
    fig.add_trace(go.Scatter(x=df_sorted['Dose (M)'], y=df_sorted['Response (%)'].rolling(window=3, center=True).mean(), 
                             mode='lines', name='Trend', line=dict(color=VERTEX_COLORS['red'])))
    fig.update_layout(height=350)
    return fig

def plot_inter_assay_comparison(df, value_col='analyte_concentration', group_col='study_id'):
    """Creates box plots to compare distributions between assays or batches."""
    fig = px.box(df, x=group_col, y=value_col, color=group_col,
                 title=f'<b>Inter-Assay Comparison for {value_col}</b>',
                 labels={value_col: value_col.replace("_", " ").title(), group_col: "Study ID"},
                 color_discrete_map={'VX-809-PK-01': VERTEX_COLORS['blue'], 'VX-561-Tox-03': VERTEX_COLORS['orange'], 'VX-121-Stab-02': VERTEX_COLORS['green']})
    fig.update_layout(showlegend=False, height=350)
    return fig

def plot_qq(data):
    """Generates a Q-Q plot to assess normality."""
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name='Data Quantiles'))
    fig.add_trace(go.Scatter(x=osm, y=slope*osm + intercept, mode='lines', name='Normal Line', line=dict(color=VERTEX_COLORS['red'])))
    fig.update_layout(title="<b>Q-Q Plot vs. Normal Distribution</b>", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", height=350)
    return fig

def plot_ml_anomaly_results(df, preds):
    """Visualizes the results of an anomaly detection algorithm."""
    df_plot = df.copy()
    df_plot['Anomaly'] = preds
    df_plot['Anomaly'] = df_plot['Anomaly'].map({1: 'Inlier', -1: 'Outlier'})
    fig = px.scatter(df_plot, x='retention_time', y='peak_area', color='Anomaly',
                     title='<b>Isolation Forest Anomaly Detection</b>',
                     color_discrete_map={'Inlier': VERTEX_COLORS['blue'], 'Outlier': VERTEX_COLORS['red']},
                     symbol='Anomaly', symbol_map={'Inlier': 'circle', 'Outlier': 'x'})
    fig.update_layout(height=400)
    return fig

def plot_ingestion_trend(df):
    """Plots historical ingestion success rate."""
    fig = px.line(df, x='Date', y='Success Rate (%)', title='<b>Daily Data Ingestion Success Rate Trend</b>',
                  markers=True, labels={'Success Rate (%)': 'Success Rate (%)'})
    fig.update_layout(height=300)
    return fig

def plot_ingestion_volume(df):
    """Plots historical ingestion volume."""
    fig = px.bar(df, x='Date', y='Files Processed', title='<b>Daily Data Ingestion Volume</b>',
                 color_discrete_sequence=[VERTEX_COLORS['lightblue']])
    fig.update_layout(height=300)
    return fig
