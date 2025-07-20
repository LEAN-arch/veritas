# utils/plotters.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

# Official Vertex branding for a commercial-grade feel
VERTEX_COLORS = {'blue': '#003DA5', 'lightblue': '#00A3E0', 'green': '#00B140', 'orange': '#F37021', 'gray': '#6A737B', 'red': '#D4000F'}

def plot_kpi_card(title, value, delta, help_text):
    """A standardized function to create KPI metric cards."""
    st.metric(label=title, value=value, delta=delta, help=help_text)

def plot_plate_heatmap(df, title):
    """Generates an interactive heatmap of 96-well plate data."""
    fig = px.imshow(df, color_continuous_scale='viridis', aspect="auto", title=title,
                    labels=dict(x="Column", y="Row", color="Value"))
    fig.update_layout(height=400)
    return fig

def plot_anova_results(df, value_col, group_col):
    """Performs ANOVA and visualizes the results with boxplots."""
    groups = [df[group_col] == g for g in df[group_col].unique()]
    f_val, p_val = stats.f_oneway(*[df.loc[g, value_col] for g in groups])
    
    fig = px.box(df, x=group_col, y=value_col, color=group_col, title=f"<b>ANOVA Results for {value_col} by {group_col}</b>")
    fig.update_layout(showlegend=False, height=350,
                      annotations=[dict(x=0.5, y=1.05, showarrow=False,
                                        text=f"<b>F-statistic: {f_val:.2f}, p-value: {p_val:.3g}</b>",
                                        xref="paper", yref="paper")])
    return fig

def plot_feature_importance(model, feature_names):
    """Plots feature importances from a trained tree-based model."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)
        fig = go.Figure(go.Bar(x=importances[sorted_idx], y=[feature_names[i] for i in sorted_idx], orientation='h'))
        fig.update_layout(title="<b>Feature Importance for Anomaly Detection</b>",
                          xaxis_title="Importance Score", yaxis_title="Feature", height=300)
        return fig
    return None

def plot_audit_timeline(df, record_id):
    """Creates a timeline of actions for a specific record."""
    record_df = df[df['Record ID'] == record_id].sort_values('Timestamp')
    if record_df.empty:
        return go.Figure().update_layout(title=f"No actions found for {record_id}", height=200)
    
    fig = px.timeline(record_df, x_start="Timestamp", x_end="Timestamp", y="User", color="Action",
                      title=f"<b>Timeline of Actions for Record: {record_id}</b>",
                      hover_data=['Details', '21 CFR 11 Justification'])
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(height=400)
    return fig
    
# Keep and refine other plotting functions
from .data_generator import get_program_gantt_data, get_qc_error_data, create_dose_response_data, create_mock_hplc_data
def plot_sankey_flow():
    fig = go.Figure(go.Sankey(node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=["Raw Data Ingested", "QC Engine", "Passed QC", "Failed QC", "Regulatory Reporting", "Investigation"], color=[VERTEX_COLORS['blue'], VERTEX_COLORS['lightblue'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['blue'], VERTEX_COLORS['gray']]), link=dict(source=[0, 1, 1, 2, 3], target=[1, 2, 3, 4, 5], value=[100, 85, 15, 85, 15], color=[VERTEX_COLORS['gray'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['lightblue'], 'rgba(243, 112, 33, 0.4)'])))
    fig.update_layout(title_text="<b>Data Package Flow & Yield</b>", font_size=12, height=350)
    return fig
def plot_gantt_chart(df):
    color_map = {'Completed': VERTEX_COLORS['green'], 'In Progress': VERTEX_COLORS['orange'], 'On Track': VERTEX_COLORS['lightblue'], 'Planned': VERTEX_COLORS['gray']}
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Program", color="Status", title="<b>Major Data Package Timelines by Program</b>", color_discrete_map=color_map, hover_data=['Risk'])
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(legend_title="Status", height=350)
    return fig
def plot_levey_jennings(df, value_col='analyte_concentration', time_col='injection_time'):
    df_sorted = df.sort_values(by=time_col).reset_index()
    mean = df_sorted[value_col].mean()
    std = df_sorted[value_col].std()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted[time_col], y=df_sorted[value_col], mode='lines+markers', name='QC Sample', marker_color=VERTEX_COLORS['blue']))
    for i in range(1, 4):
        fig.add_hline(y=mean + i*std, line_dash="dot", line_color=VERTEX_COLORS['orange'] if i < 3 else VERTEX_COLORS['red'])
        fig.add_hline(y=mean - i*std, line_dash="dot", line_color=VERTEX_COLORS['orange'] if i < 3 else VERTEX_COLORS['red'])
    fig.add_hline(y=mean, line_dash="solid", line_color=VERTEX_COLORS['green'], annotation_text="Mean")
    fig.update_layout(title=f"<b>Levey-Jennings Chart for {value_col}</b>", xaxis_title="Time", yaxis_title="Value", height=300)
    return fig
def plot_pareto_chart(df):
    df['cumulative_percentage'] = df['Frequency'].cumsum() / df['Frequency'].sum() * 100
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Error Type'], y=df['Frequency'], name='Error Count', marker_color=VERTEX_COLORS['orange']))
    fig.add_trace(go.Scatter(x=df['Error Type'], y=df['cumulative_percentage'], name='Cumulative %', yaxis='y2', mode='lines+markers', line=dict(color=VERTEX_COLORS['blue'])))
    fig.update_layout(title='<b>Pareto Analysis of QC Failures (80/20 Rule)</b>', xaxis_title='Error Type', yaxis=dict(title='Frequency'), yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', range=[0, 105]), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=350)
    return fig
def plot_dose_response(df):
    fig = px.scatter(df, x='Dose (M)', y='Response (%)', log_x=True, title='<b>Dose-Response Curve for Lead Compound</b>')
    df_sorted = df.sort_values('Dose (M)')
    fig.add_trace(go.Scatter(x=df_sorted['Dose (M)'], y=df_sorted['Response (%)'].rolling(window=3, center=True).mean(), mode='lines', name='Trend', line=dict(color=VERTEX_COLORS['red'])))
    fig.update_layout(height=350)
    return fig
def plot_qq(data):
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name='Data Quantiles'))
    fig.add_trace(go.Scatter(x=osm, y=slope*osm + intercept, mode='lines', name='Normal Line', line=dict(color=VERTEX_COLORS['red'])))
    fig.update_layout(title="<b>Q-Q Plot vs. Normal Distribution</b>", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles", height=350)
    return fig
def plot_ml_anomaly_results(df, preds):
    df_plot = df.copy()
    df_plot['Anomaly'] = preds
    df_plot['Anomaly'] = df_plot['Anomaly'].map({1: 'Inlier', -1: 'Outlier'})
    fig = px.scatter(df_plot, x='retention_time', y='peak_area', color='Anomaly', title='<b>Isolation Forest Anomaly Detection</b>', color_discrete_map={'Inlier': VERTEX_COLORS['blue'], 'Outlier': VERTEX_COLORS['red']}, symbol='Anomaly', symbol_map={'Inlier': 'circle', 'Outlier': 'x'})
    fig.update_layout(height=400)
    return fig
def plot_ingestion_trend(df):
    fig = px.line(df, x='Date', y='Success Rate (%)', title='<b>Daily Data Ingestion Success Rate Trend</b>', markers=True, labels={'Success Rate (%)': 'Success Rate (%)'})
    fig.update_layout(height=300)
    return fig
def plot_ingestion_volume(df):
    fig = px.bar(df, x='Date', y='Files Processed', title='<b>Daily Data Ingestion Volume</b>', color_discrete_sequence=[VERTEX_COLORS['lightblue']])
    fig.update_layout(height=300)
    return fig
