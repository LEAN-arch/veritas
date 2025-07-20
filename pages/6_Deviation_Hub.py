# pages/6_deviation_hub.py
import streamlit as st
import pandas as pd

# Import from the centralized backend modules
from utils import ui_components, data_connector as dc, auth

# Set the page configuration for this specific page
st.set_page_config(page_title="Deviation Hub", page_icon="📌", layout="wide")

st.title("📌 Deviation Management Hub")
st.markdown("An interactive Kanban board to manage the lifecycle of deviations, OOS, and OOT investigations.")

# --- Load data and config from session state ---
deviations_df = st.session_state.get('deviations_df', pd.DataFrame())
app_config = st.session_state.get('app_config', {})
username = st.session_state.get('username', 'Unknown User')

# Stop execution if the main app hasn't initialized the session properly
if deviations_df.empty or not app_config or username == 'Unknown User':
    st.warning("Session not initialized. Please start from the main VERITAS Command Center.")
    st.stop()

# --- Get Kanban config from central file ---
dev_config = app_config.get('deviation_management', {})
kanban_states = dev_config.get('kanban_states', [])

with st.expander("ℹ️ SME Overview: Digitalizing the Deviation Workflow"):
    st.info("""
        - **Purpose:** To provide a single source of truth for all active investigations, replacing offline trackers.
        - **Actionability:** The "▶️ Advance" button updates the deviation's status in real-time (within the app session) and creates an auditable record of the action.
        - **Value:** This digitalizes a core QC workflow, improving transparency, reducing resolution time, and providing a live overview of team workload and bottlenecks.
    """)
    
# --- Actionable Kanban Board (Dynamically Generated) ---
kanban_cols = st.columns(len(kanban_states))

for i, status in enumerate(kanban_states):
    with kanban_cols[i]:
        st.subheader(status)
        st.markdown("---")
        
        # Filter the deviations for the current status column
        cards_in_column = deviations_df[deviations_df['status'] == status]
        
        for index, card_data in cards_in_column.iterrows():
            # Call the reusable UI component to render the card.
            # The component returns True if its "Advance" button was clicked.
            if ui_components.render_kanban_card(card_data):
                # If the button was clicked, this page (the "controller") handles the logic.
                current_status_index = kanban_states.index(status)
                new_status = kanban_states[current_status_index + 1]
                
                # Update the DataFrame in session state
                st.session_state.deviations_df.loc[
                    st.session_state.deviations_df['id'] == card_data['id'], 'status'
                ] = new_status
                
                # Write to the central audit log
                dc.write_to_audit_log(
                    user=username,
                    action="Deviation Status Changed",
                    details=f"Status for {card_data['id']} changed from '{status}' to '{new_status}'.",
                    record_id=card_data['id']
                )
                
                # Rerun to show the card in its new column
                st.rerun()

# Add the compliance footer
auth.display_compliance_footer()
