# utils/auth.py
import streamlit as st

# --- PHASE 1: User Authentication and Role-Based Access ---
# SME EXPLANATION: This module is a critical upgrade for enterprise-readiness.
# It simulates a full authentication workflow. Instead of just selecting a role,
# the user must now "log in". This establishes a user identity (st.session_state.username)
# which is essential for a compliant Audit Trail (to know WHO performed an action).
# In a real-world scenario, the login logic would be replaced with a secure SSO
# integration (e.g., SAML, OAuth with Okta or Azure AD).

def authenticate_user():
    """
    Handles the entire user authentication workflow.
    - If the user is not authenticated, it displays a login screen.
    - If the user is authenticated, it displays the main sidebar with role selection and logout.
    - Returns the selected user role for use in the main application.
    """
    # Initialize session state for authentication status if it doesn't exist
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # If user is not authenticated, show the login screen
    if not st.session_state.authenticated:
        render_login_screen()
        st.stop() # Stop execution of the rest of the app
    
    # If user is authenticated, render the main sidebar
    else:
        render_main_sidebar()
        return st.session_state.user_role

def render_login_screen():
    """Displays the login form in the main area of the page."""
    with st.container():
        st.title("VERITAS - Automated QC & Reporting")
        st.header("Please Log In")

        # In a real app, you would have a list of valid users and roles from a database
        # For this demo, we'll allow any non-empty username/password
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            if username and password:
                # --- Successful Login Simulation ---
                st.session_state.authenticated = True
                st.session_state.username = username
                
                # Assign a default role based on a simulated user directory
                if "dir" in username.lower() or "lead" in username.lower():
                    st.session_state.user_role = 'DTE Leadership'
                elif "qc" in username.lower() or "analyst" in username.lower():
                    st.session_state.user_role = 'QC Analyst'
                else:
                    st.session_state.user_role = 'Scientist'
                
                st.rerun() # Rerun the script to now show the main app
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

    if st.sidebar.button("Logout"):
        # Clear all session state keys to ensure a clean logout
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

def display_compliance_footer():
    """Displays a standardized GxP compliance footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; font-size: 0.8em; color: grey;">
        <p>VERITAS v3.0 (Enterprise Grade) | For Internal Vertex Use Only</p>
        <p><strong>GxP Compliance Notice:</strong> All actions are logged. Data integrity is enforced per <strong>21 CFR Part 11</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
