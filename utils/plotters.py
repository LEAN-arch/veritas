# utils/plotters.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Vertex brand colors for consistent look and feel
VERTEX_COLORS = {
    'blue': '#003DA5', 'lightblue': '#00A3E0', 'green': '#00B140', 
    'orange': '#F37021', 'gray': '#6A737B'
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
            source=[0, 1, 1, 3], 
            target=[1, 2, 3, 5],
            value=[100, 85, 15, 15],
            color=[VERTEX_COLORS['gray'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], 'rgba(243, 112, 33, 0.4)']
        )
    ))
    fig.update_layout(title_text="<b>Data Package Flow & Yield</b>", font_size=12)
    return fig

def plot_gantt_chart(df):
    """Creates a Gantt chart for program timelines."""
    color_map = {'Completed': VERTEX_COLORS['green'], 'In Progress': VERTEX_COLORS['orange'], 
                 'On Track': VERTEX_COLORS['lightblue'], 'Planned': VERTEX_COLORS['gray']}
    fig = px.timeline(
        df, x_start="Start", x_end="Finish", y="Program", color="Status",
        title="<b>Major Data Package Timelines by Program</b>",
        color_discrete_map=color_map
    )
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(legend_title="Status")
    return fig

def plot_spc_chart(df, value_col='analyte_concentration', group_col='injection_time'):
    """Creates a Statistical Process Control (I-MR) chart."""
    df_sorted = df.sort_values(by=group_col).reset_index()
    
    mean = df_sorted[value_col].mean()
    std_dev = df_sorted[value_col].std()
    ucl = mean + 3 * std_dev
    lcl = mean - 3 * std_dev
    
    df_sorted['outlier'] = (df_sorted[value_col] > ucl) | (df_sorted[value_col] < lcl)
    
    fig = go.Figure()
    # Add traces for data points
    fig.add_trace(go.Scatter(
        x=df_sorted[group_col], y=df_sorted[value_col], mode='lines+markers',
        name='Measurement', marker_color=VERTEX_COLORS['blue']
    ))
    # Highlight outliers
    fig.add_trace(go.Scatter(
        x=df_sorted[df_sorted['outlier']][group_col],
        y=df_sorted[df_sorted['outlier']][value_col],
        mode='markers', name='Out of Control',
        marker=dict(color='red', size=10, symbol='x')
    ))
    
    # Add control lines
    fig.add_hline(y=mean, line_dash="dash", line_color="green", annotation_text="Center Line")
    fig.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="UCL")
    fig.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="LCL")
    
    fig.update_layout(
        title=f'<b>SPC Chart for {value_col}</b>',
        xaxis_title='Injection Time', yaxis_title='Concentration',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_pareto_chart(df):
    """Creates a Pareto chart for QC error analysis."""
    df['cumulative_percentage'] = df['Frequency'].cumsum() / df['Frequency'].sum() * 100
    
    fig = go.Figure()
    # Bar chart for frequency
    fig.add_trace(go.Bar(
        x=df['Error Type'], y=df['Frequency'], name='Error Count',
        marker_color=VERTEX_COLORS['orange']
    ))
    # Line chart for cumulative percentage
    fig.add_trace(go.Scatter(
        x=df['Error Type'], y=df['cumulative_percentage'], name='Cumulative %',
        yaxis='y2', mode='lines+markers', line=dict(color=VERTEX_COLORS['blue'])
    ))
    
    fig.update_layout(
        title='<b>Pareto Analysis of QC Failures</b>',
        xaxis_title='Error Type',
        yaxis=dict(title='Frequency'),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_data_lineage():
    """Creates a visual data lineage graph."""
    fig = go.Figure(go.Sankey(
        arrangement="freeform",
        node={
            "label": ["Raw .dat File (HPLC-01)", "Parsed Data Table", "QC Engine Run #123", "Flagged Outliers", "Cleaned Dataset", "IND Study Report (Sec 4.1)"],
            "x": [0.1, 0.3, 0.3, 0.5, 0.7, 0.9],
            "y": [0.1, 0.2, 0.4, 0.5, 0.3, 0.3],
            'pad': 10,
        },
        link={
            "source": [0, 1, 2, 2, 4],
            "target": [1, 2, 3, 4, 5],
            "value": [8, 8, 2, 6, 6] # Arbitrary values for link thickness
        }))
    fig.update_layout(title_text="<b>Interactive Data Lineage for 'SMP-1005'</b>", font_size=12)
    return fig
