# utils/auth.py
import streamlit as st

def get_user_role():
    """Simulates a user login and role selection for demo purposes."""
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'DTE Leadership' # Default role

    role_options = ['DTE Leadership', 'Study Director', 'QC Analyst', 'Scientist']
    
    # In a real app, this would be a secure login flow (e.g., SSO/OAuth)
    # For the demo, we use a sidebar selectbox to switch roles.
    st.sidebar.title("👤 User Role Simulation")
    selected_role = st.sidebar.selectbox(
        "Select Your Role to View a Tailored Dashboard",
        options=role_options,
        index=role_options.index(st.session_state.user_role),
        key="role_selector"
    )
    st.session_state.user_role = selected_role
    st.sidebar.info(f"Viewing VERITAS as: **{st.session_state.user_role}**")
    
    return st.session_state.user_role

def display_compliance_footer():
    """Displays a GxP compliance footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8em; color: grey;">
        <p>VERITAS v1.0 | For Internal Vertex Use Only</p>
        <p><strong>GxP Compliance Notice:</strong> All actions are logged. Data integrity is enforced per <strong>21 CFR Part 11</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
