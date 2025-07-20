# utils/config.py
import plotly.graph_objects as go

VERTEX_COLORS = {
    'blue': '#003DA5', 'lightblue': '#00A3E0', 'green': '#00B140', 
    'orange': '#F37021', 'gray': '#6A737B', 'red': '#D4000F',
    'lightred': '#FFC0CB', 'lightyellow': '#FFFACD', 'lightcyan': '#E0FFFF',
}

VERITAS_THEME = go.layout.Template(
    layout=go.Layout(
        font=dict(family="sans-serif", size=12, color=VERTEX_COLORS['gray']),
        title_font_color=VERTEX_COLORS['blue'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        colorway=[
            VERTEX_COLORS['blue'], VERTEX_COLORS['lightblue'], VERTEX_COLORS['green'], 
            VERTEX_COLORS['orange'], VERTEX_COLORS['gray'], VERTEX_COLORS['red']
        ]
    )
)

AUTH_CONFIG = {
    "role_options": ['DTE Leadership', 'Study Director', 'QC Analyst', 'Scientist'],
    "default_role": "DTE Leadership"
}

APP_CONFIG = {
    "app_version": "v6.0 (Stable & Corrected)",
    "process_capability": {
        "cpk_target": 1.33,
        "available_cqas": ["Purity", "Aggregate Content", "Main Impurity", "Bio-activity"],
        "spec_limits": {
            "Purity": {"LSL": 98.0, "USL": 102.0},
            "Aggregate Content": {"LSL": 0.0, "USL": 1.0},
            "Main Impurity": {"LSL": 0.1, "USL": 0.5},
            "Bio-activity": {"LSL": 90.0, "USL": 110.0}
        }
    },
    "stability_specs": {
        "Purity (%)": {"USL": None, "LSL": 98.0},
        "Main Impurity (%)": {"USL": 0.5, "LSL": None}
    },
    "deviation_management": {
        "kanban_states": ["New", "In Progress", "Pending QA", "Closed"],
        "priority_colors": {
            "High": VERTEX_COLORS['lightred'], "Medium": VERTEX_COLORS['lightyellow'], "Low": VERTEX_COLORS['lightcyan']
        }
    },
    "audit_trail": {
        "action_icons": {
            "User Login": "👤", "Data Fetched": "🔍", "Report Generated": "📄", 
            "Deviation Status Changed": "🔄", "Stability Plot Viewed": "📈", 
            "E-Signature Applied": "✍️", "Data Exported": "📤", "Configuration Changed": "⚙️",
            "File Ingested": "📥", "QC Rule Applied": "🔬", "Data Point Flagged": "🚩",
            "Discrepancy Resolved": "✅", "Permission Changed": "🔐", "Role View Changed": "🎭"
        }
    }
}
