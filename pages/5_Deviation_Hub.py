# pages/5_Deviation_Hub.py
import streamlit as st
import pandas as pd

# Import the new foundational modules
from utils import data_connector as dc
from utils import auth

# --- Page Configuration ---
st.set_page_config(
    page_title="Deviation Hub",
    page_icon="📌",
    layout="wide"
)

# --- Authentication and Data Loading ---
user_role = auth.authenticate_user()
db_connection = dc.connect_to_db({"database": "PROD_DATA_WAREHOUSE"})

# --- Session State Initialization for Kanban ---
# SME EXPLANATION: We use st.session_state to hold the Kanban data. This is crucial
# because it allows us to modify the data (e.g., move a card) and have that change
# persist without having to re-fetch from the "database" on every interaction.
if 'deviations_df' not in st.session_state:
    st.session_state.deviations_df = dc.fetch_deviations_data(db_connection)

# --- Page Header ---
st.title("📌 Deviation Management Hub")
st.markdown("An interactive Kanban board to manage the lifecycle of deviations, OOS, and OOT investigations.")

with st.expander("ℹ️ SME Overview: Digitalizing the Deviation Workflow"):
    st.info("""
        - **Purpose:** To provide a single source of truth for all active investigations, replacing offline spreadsheets and trackers.
        - **Actionability:** This is not just a view; it's an interactive tool. The "▶️ Advance" button simulates updating the deviation's status in the backend database and provides an auditable record of the action.
        - **Commercial Value:** This digitalizes a core QC workflow, improving transparency, reducing resolution time, and ensuring that no investigation is forgotten. It provides managers with a real-time overview of the team's workload and bottlenecks.
    """)

# --- PHASE 3: Actionable Kanban Board ---
# Define the columns for the Kanban board
status_columns = ["New", "In Progress", "Pending QA", "Closed"]

# Create the layout for the Kanban board
kanban_cols = st.columns(len(status_columns))

for i, status in enumerate(status_columns):
    with kanban_cols[i]:
        st.subheader(status)
        st.markdown("---")
        
        # Filter the deviations for the current status column
        cards = st.session_state.deviations_df[st.session_state.deviations_df['status'] == status]
        
        for index, card in cards.iterrows():
            # Use a color-coded container for each card based on priority
            priority_color = {
                "High": "#FFC0CB", # Light Red
                "Medium": "#FFFACD", # Lemon Chiffon
                "Low": "#E0FFFF" # Light Cyan
            }.get(card['priority'], "#FFFFFF")

            with st.container(border=True):
                st.markdown(f"<div style='background-color:{priority_color}; padding: 10px; border-radius: 5px;'>"
                            f"<strong>{card['id']}</strong><br>"
                            f"{card['title']}"
                            "</div>", unsafe_allow_html=True)
                
                # Add the "Advance" button for all statuses except the last one
                if status != "Closed":
                    # Use the card's unique ID in the button's key to make it unique
                    if st.button(f"▶️ Advance", key=f"advance_{card['id']}"):
                        
                        # --- Workflow Automation Logic ---
                        current_status_index = status_columns.index(status)
                        new_status = status_columns[current_status_index + 1]
                        
                        # Update the DataFrame in session state
                        st.session_state.deviations_df.loc[
                            st.session_state.deviations_df['id'] == card['id'], 'status'
                        ] = new_status
                        
                        # --- Audit Log Entry ---
                        dc.write_to_audit_log(
                            db_connection,
                            user=st.session_state.username,
                            action="Deviation Status Changed",
                            details=f"Status for {card['id']} changed from '{status}' to '{new_status}'."
                        )
                        
                        # Rerun the app to show the card in its new column
                        st.rerun()

# --- Global Compliance Footer ---
auth.display_compliance_footer()
