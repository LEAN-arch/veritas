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

# --- PHASE 2: New & Enhanced Analytical Plots ---

def plot_historical_control_chart(df, cqa: str, date_range: tuple):
    """
    Creates a historical I-MR control chart for a selected CQA over a date range.
    This is a significant enhancement for tracking process stability over time.
    """
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    
    df_filtered = df[(df['injection_time'] >= start_date) & (df['injection_time'] <= end_date)].copy()
    
    if len(df_filtered) < 2:
        return go.Figure().update_layout(title_text=f"Not enough data for {cqa} in selected date range.", height=350)

    # I-Chart (Individuals Chart)
    mean = df_filtered[cqa].mean()
    std_dev = df_filtered[cqa].std()
    ucl = mean + 3 * std_dev
    lcl = mean - 3 * std_dev

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered['injection_time'], y=df_filtered[cqa],
        mode='lines+markers', name=cqa, marker_color=VERTEX_COLORS['blue']
    ))
    fig.add_hline(y=mean, line_dash="dash", line_color=VERTEX_COLORS['green'], annotation_text="Mean")
    fig.add_hline(y=ucl, line_dash="dot", line_color=VERTEX_COLORS['red'], annotation_text="UCL")
    fig.add_hline(y=lcl, line_dash="dot", line_color=VERTEX_COLORS['red'], annotation_text="LCL")
    
    fig.update_layout(
        title=f"<b>Historical Control Chart (I-Chart) for {cqa}</b>",
        xaxis_title="Date", yaxis_title="Value", height=350, showlegend=False
    )
    return fig

def plot_process_capability(df, cqa: str, lsl: float, usl: float):
    """
    Calculates and displays a process capability histogram (Cpk).
    """
    data = df[cqa].dropna()
    if data.empty:
         return go.Figure().update_layout(title_text=f"No data for {cqa}.", height=350)
    
    mean = data.mean()
    std_dev = data.std()
    
    # Calculate Cpk
    cpu = (usl - mean) / (3 * std_dev) if usl is not None else np.inf
    cpl = (mean - lsl) / (3 * std_dev) if lsl is not None else np.inf
    cpk = min(cpu, cpl)

    fig = px.histogram(df, x=cqa, nbins=30, title=f"<b>Process Capability for {cqa} | Cpk: {cpk:.2f}</b>",
                       color_discrete_sequence=[VERTEX_COLORS['lightblue']])
    if lsl is not None: fig.add_vline(x=lsl, line_dash="solid", line_color=VERTEX_COLORS['red'], annotation_text="LSL")
    if usl is not None: fig.add_vline(x=usl, line_dash="solid", line_color=VERTEX_COLORS['red'], annotation_text="USL")
    fig.add_vline(x=mean, line_dash="dash", line_color=VERTEX_COLORS['green'], annotation_text="Mean")
    
    fig.update_layout(height=350)
    return fig

def plot_stability_trend(df, assay: str, spec_limits: dict):
    """
    Plots a stability trend chart with specification limits.
    """
    lsl = spec_limits.get('LSL')
    usl = spec_limits.get('USL')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Timepoint (Months)'], y=df[assay], 
        mode='lines+markers', name=assay, marker_color=VERTEX_COLORS['blue']
    ))
    
    # Add specification limit lines
    if lsl is not None:
        fig.add_trace(go.Scatter(x=df['Timepoint (Months)'], y=[lsl]*len(df), mode='lines', name='LSL', line=dict(color=VERTEX_COLORS['red'], dash='solid')))
    if usl is not None:
        fig.add_trace(go.Scatter(x=df['Timepoint (Months)'], y=[usl]*len(df), mode='lines', name='USL', line=dict(color=VERTEX_COLORS['red'], dash='solid')))
        
    fig.update_layout(
        title=f"<b>Stability Trend for {assay}</b>",
        xaxis_title="Timepoint (Months)", yaxis_title="Value", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# --- Existing Plotting Functions (from previous versions, preserved) ---

def render_lineage_timeline(df, record_id):
    """Renders a professional, vertical timeline of events for a specific record."""
    record_df = df[df['Record ID'] == record_id].copy().sort_values('Timestamp', ascending=True)
    if record_df.empty:
        st.warning(f"No audit records found for the selected Record ID: **{record_id}**.")
        return

    st.subheader(f"Lineage for: {record_id}")
    action_icons = {"User Login": "👤", "Data Fetched": "🔍", "Report Generated": "📄", "Deviation Status Changed": "🔄", "Stability Plot Viewed": "📈", "E-Signature Applied": "✍️", "Data Exported": "📤", "Configuration Changed": "⚙️"}
    for index, row in record_df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 10])
            with col1: st.markdown(f"<div style='font-size: 2em; text-align: center;'>{action_icons.get(row['Action'], '⚙️')}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{row['Action']}**")
                st.markdown(f"**By:** {row['User']} | **Timestamp:** {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                with st.expander("Show Details"):
                    st.markdown(f"**Details:** *{row['Details']}*")
            st.markdown("<hr style='margin-top: 0; margin-bottom: 1em;'/>", unsafe_allow_html=True)

def plot_sankey_flow():
    fig = go.Figure(go.Sankey(node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=["Raw Data Ingested", "QC Engine", "Passed QC", "Failed QC", "Regulatory Reporting", "Investigation"], color=[VERTEX_COLORS['blue'], VERTEX_COLORS['lightblue'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['blue'], VERTEX_COLORS['gray']]), link=dict(source=[0, 1, 1, 2, 3], target=[1, 2, 3, 4, 5], value=[100, 85, 15, 85, 15], color=[VERTEX_COLORS['gray'], VERTEX_COLORS['green'], VERTEX_COLORS['orange'], VERTEX_COLORS['lightblue'], 'rgba(243, 112, 33, 0.4)'])))
    fig.update_layout(title_text="<b>Data Package Flow & Yield</b>", font_size=12, height=350)
    return fig

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

def plot_gantt_chart(df):
    color_map = {'Completed': VERTEX_COLORS['green'], 'In Progress': VERTEX_COLORS['orange'], 'On Track': VERTEX_COLORS['lightblue'], 'Planned': VERTEX_COLORS['gray']}
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Program", color="Status", title="<b>Major Data Package Timelines by Program</b>", color_discrete_map=color_map, hover_data=['Risk'])
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_layout(legend_title="Status", height=350)
    return fig
