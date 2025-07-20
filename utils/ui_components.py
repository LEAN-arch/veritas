# utils/ui_components.py
import streamlit as st
import pandas as pd

# Import centralized configuration for consistency
from utils.config import APP_CONFIG

def render_lineage_timeline(df: pd.DataFrame, record_id: str):
    """
    Renders a professional, vertical timeline of events for a specific record.
    This is a pure UI component.
    
    Args:
        df (pd.DataFrame): The full audit trail DataFrame.
        record_id (str): The specific record ID to trace.
    """
    record_df = df[df['Record ID'] == record_id].copy().sort_values('Timestamp', ascending=True)
    
    if record_df.empty:
        st.warning(f"No audit records found for the selected Record ID: **{record_id}**.")
        return

    st.subheader(f"Lineage for: {record_id}")
    action_icons = APP_CONFIG['audit_trail']['action_icons']
    
    for _, row in record_df.iterrows():
        col1, col2 = st.columns([1, 10])
        
        with col1:
            icon = action_icons.get(row['Action'], '⚙️')
            st.markdown(f"<p style='font-size: 2em; text-align: center;'>{icon}</p>", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"**{row['Action']}**")
            st.caption(f"By: {row['User']} | Timestamp: {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            if pd.notna(row['Details']) and row['Details']:
                with st.expander("Show Details"):
                    st.markdown(f"*{row['Details']}*")

        st.markdown("<hr style='margin-top: 0; margin-bottom: 1em;'/>", unsafe_allow_html=True)


def render_kanban_card(card_data: pd.Series) -> bool:
    """
    Renders a single card for the Kanban board and its 'Advance' button.
    This component is now stateless and only handles rendering.

    Args:
        card_data (pd.Series): A row from the deviations DataFrame.
        
    Returns:
        bool: True if the 'Advance' button for this card was clicked, False otherwise.
    """
    priority_colors = APP_CONFIG['deviation_management']['priority_colors']
    kanban_states = APP_CONFIG['deviation_management']['kanban_states']
    
    button_clicked = False
    
    # Use a color-coded container for each card based on priority
    color = priority_colors.get(card_data['priority'], "#FFFFFF")
    
    with st.container(border=True):
        st.markdown(
            f"""
            <div style='background-color:{color}; padding: 10px; border-radius: 5px; border-left: 5px solid {priority_colors.get(card_data['priority'], '#CCCCCC')};'>
                <strong>{card_data['id']}</strong><br>
                <small>{card_data['title']}</small>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Add the "Advance" button if the card is not in the final state
        current_status = card_data['status']
        if current_status != kanban_states[-1]:
            if st.button("▶️ Advance", key=f"advance_{card_data['id']}", help=f"Move from {current_status} to next stage"):
                button_clicked = True
                
    return button_clicked
