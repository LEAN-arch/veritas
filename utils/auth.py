# utils/auth.py
import streamlit as st
# Import centralized configuration for roles and app version
from utils.config import AUTH_CONFIG, APP_CONFIG

def initialize_session():
    """
    Initializes the user session state if it's not already set up.
    This should be called once at the beginning of the main app script.
    - Sets a default username and role.
    - Ensures a consistent session state for the demo.
    """
    if 'session_initialized' not in st.session_state:
        st.session_state.username = 'Demo User'
        st.session_state.user_role = AUTH_CONFIG['default_role']
        st.session_state.session_initialized = True
        st.session_state.login_audited = False

def render_main_sidebar():
    """
    Renders the main application sidebar for the current user.
    Assumes that the session has already been initialized.
    """
    st.sidebar.title("VERITAS")
    st.sidebar.caption("Vertex Ensured Reporting & Integrity Transformation Automation Suite")
    st.sidebar.markdown("---")
    st.sidebar.info(f"Welcome, **{st.session_state.get('username', 'User')}**")

    # Get role options from the central config
    role_options = AUTH_CONFIG['role_options']
    
    # Use the current role from session state to set the index
    current_role_index = role_options.index(st.session_state.user_role)
    
    selected_role = st.sidebar.selectbox(
        "Switch Role View",
        options=role_options,
        index=current_role_index,
        key="role_selector",
        help="Switch roles to see how dashboards and permissions change."
    )
    
    # Update the session state if the role has been changed
    if selected_role != st.session_state.user_role:
        st.session_state.user_role = selected_role
        st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("Reset Session / Logout"):
        # Clear the entire session state to start fresh
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

def display_compliance_footer():
    """
    Displays a standardized GxP compliance footer.
    Pulls the version number from the central config.
    """
    st.markdown("---")
    footer_html = f"""
    <div style="text-align: center; font-size: 0.8em; color: grey;">
        <p>VERITAS {APP_CONFIG['app_version']} | For Internal Vertex Use Only</p>
        <p><strong>GxP Compliance Notice:</strong> All actions are logged. Data integrity is enforced per <strong>21 CFR Part 11</strong>.</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def render_login_screen():
    """
    This function is dormant in the "no login" workflow but is kept for future use.
    It demonstrates what a potential login screen could look like.
    NOTE: In a real enterprise app, this would integrate with an Identity Provider (e.g., SAML/OAuth).
    """
    with st.container():
        st.title("VERITAS - Automated QC & Reporting")
        st.header("Please Log In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if username and password:
                # This is a placeholder for a real authentication check
                st.session_state.username = username
                if "lead" in username.lower() or "dir" in username.lower():
                    st.session_state.user_role = 'DTE Leadership'
                elif "qc" in username.lower():
                    st.session_state.user_role = 'QC Analyst'
                else:
                    st.session_state.user_role = 'Scientist'
                
                st.session_state.session_initialized = True
                st.session_state.login_audited = False
                st.rerun()
            else:
                st.error("Please enter both a username and password.")
