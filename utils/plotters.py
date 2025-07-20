# utils/plotters.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

VERTEX_COLORS = {
    'blue': '#003DA5', 'lightblue': '#00A3E0', 'green': '#00B140', 
    'orange': '#F37021', 'gray': '#6A737B', 'red': '#D4000F'
}

def plot_data_lineage_sankey(df, record_id):
    """
    Creates a Sankey diagram to visualize the data lineage for a specific record.
    This is the superior, industry-standard method for showing flow.
    """
    record_df = df[df['Record ID'] == record_id].copy().sort_values('Timestamp', ascending=True)

    if len(record_df) < 2:
        return None # Not enough data points to create a flow diagram

    # Create more descriptive labels for nodes
    record_df['NodeLabel'] = record_df['Action'] + ' by ' + record_df['User']
    all_nodes = record_df['NodeLabel'].unique().tolist()
    
    source_indices = []
    target_indices = []
    
    # Create links by connecting sequential events
    for i in range(len(record_df) - 1):
        source_label = record_df.iloc[i]['NodeLabel']
        target_label = record_df.iloc[i+1]['NodeLabel']
        
        source_indices.append(all_nodes.index(source_label))
        target_indices.append(all_nodes.index(target_label))
        
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node={
            "pad": 25,
            "thickness": 20,
            "line": dict(color="black", width=0.5),
            "label": all_nodes,
        },
        link={
            "source": source_indices,
            "target": target_indices,
            "value": [1] * len(source_indices), # All flows have equal weight for lineage
        }
    ))
    
    fig.update_layout(
        title_text=f"<b>Data Lineage Flow for Record: {record_id}</b>",
        font_size=12,
        height=500
    )
    return fig

# --- ALL OTHER PLOTTING FUNCTIONS REMAIN THE SAME ---

def plot_plate_heatmap(df, title):
    fig = px.imshow(df, color_continuous_scale='viridis', aspect="auto", title=title, labels=dict(x="Column", y="Row", color="Value"))
    fig.update_layout(height=400)
    return fig

def plot_anova_results(df, value_col, group_col):
    unique_groups = df[group_col].unique()
    if len(unique_groups) < 2:
        return go.Figure().update_layout(title=f"<b>Not enough groups to perform ANOVA</b>", height=350)
    groups = [df.loc[df[group_col] == g, value_col].dropna() for g in unique_groups]
    f_val, p_val = stats.f_oneway(*groups)
    fig = px.box(df, x=group_col, y=value_col, color=group_col, title=f"<b>ANOVA Results for {value_col} by {group_col}</b>")
    fig.update_layout(showlegend=False, height=350, annotations=[dict(x=0.5, y=1.05, showarrow=False, text=f"<b>F-statistic: {f_val:.2f}, p-value: {p_val:.3g}</b>", xref="paper", yref="paper")])
    return fig

def plot_spc_chart(df, value_col, time_col='injection_time'):
    df_sorted = df.sort_values(by=time_col).reset_index()
    mean = df_sorted[value_col].mean()
    std_dev = df_sorted[value_col].std()
    ucl = mean + 3 * std_dev; lcl = mean - 3 * std_dev
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted[time_col], y=df_sorted[value_col], mode='lines+markers', name='Measurement', marker_color=VERTEX_COLORS['blue']))
    fig.add_hline(y=mean, line_dash="dash", line_color="green", annotation_text="Center Line (CL)")
    fig.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="Upper Control Limit (UCL)")
    fig.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="Lower Control Limit (LCL)")
    fig.update_layout(title=f'<b>SPC Chart for {value_col}</b>', xaxis_title='Time', yaxis_title='Value', height=300)
    return fig

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

def plot_inter_assay_comparison(df, value_col='analyte_concentration', group_col='study_id'):
    fig = px.box(df, x=group_col, y=value_col, color=group_col, title=f'<b>Inter-Assay Comparison for {value_col}</b>', labels={value_col: value_col.replace("_", " ").title(), group_col: "Study ID"})
    fig.update_layout(showlegend=False, height=350)
    return fig

def plot_qq(data):
    (osm, osr), (slope, intercept, r) = stats.probplot(data.dropna(), dist="norm")
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
