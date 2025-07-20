# utils/auth.py
import streamlit as st

# --- PHASE 1 (MODIFIED): User Authentication and Role-Based Access ---
# SME EXPLANATION: This module has been modified to bypass the login screen for
# direct access, per the user's request. Instead of showing a login form, it now
# automatically assigns a default "Demo User" and proceeds directly to the main
# application. This retains the user context necessary for the audit trail and
# role-switching functionality without the friction of a login page.

def authenticate_user():
    """
    Handles user session setup without a login screen.
    - If no user is in the session, it establishes a default user.
    - It always renders the main sidebar with the role-switcher and logout button.
    - Returns the selected user role for use in the main application.
    """
    # If no user is in the session state, establish a default user.
    if 'username' not in st.session_state:
        st.session_state.username = 'Demo User'
        st.session_state.user_role = 'DTE Leadership' # Set a default starting role

    # Directly render the main sidebar for the simulated user.
    render_main_sidebar()
    return st.session_state.user_role

def render_login_screen():
    """
    This function is no longer called in the "no login" workflow but is
    kept here in case login functionality needs to be re-enabled in the future.
    """
    with st.container():
        st.title("VERITAS - Automated QC & Reporting")
        st.header("Please Log In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                if "dir" in username.lower() or "lead" in username.lower():
                    st.session_state.user_role = 'DTE Leadership'
                elif "qc" in username.lower() or "analyst" in username.lower():
                    st.session_state.user_role = 'QC Analyst'
                else:
                    st.session_state.user_role = 'Scientist'
                st.rerun()
            else:
                st.error("Please enter both a username and password.")

def render_main_sidebar():
    """Renders the main application sidebar for an authenticated user."""
    st.sidebar.title("VERITAS")
    st.sidebar.caption("Vertex Ensured Reporting & Integrity Transformation Automation Suite")
    st.sidebar.markdown("---")
    st.sidebar.info(f"Welcome, **{st.session_state.get('username', 'User')}**")

    role_options = ['DTE Leadership', 'Study Director', 'QC Analyst', 'Scientist']
    
    # Allow role switching for demo purposes
    selected_role = st.sidebar.selectbox(
        "Switch Role View",
        options=role_options,
        index=role_options.index(st.session_state.get('user_role', 'Scientist')),
        key="role_selector",
        help="Switch roles to see how dashboards and permissions change."
    )
    st.session_state.user_role = selected_role

    st.sidebar.markdown("---")

    if st.sidebar.button("Reset Session"):
        # The "Logout" button is now a "Reset" button.
        # It clears the session state to return to the default view.
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

def display_compliance_footer():
    """Displays a standardized GxP compliance footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8em; color: grey;">
        <p>VERITAS v3.1 (Direct Access Mode) | For Internal Vertex Use Only</p>
        <p><strong>GxP Compliance Notice:</strong> All actions are logged. Data integrity is enforced per <strong>21 CFR Part 11</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
