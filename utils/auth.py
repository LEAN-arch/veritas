# utils/auth.py
import streamlit as st
import os
from utils.config import AUTH_CONFIG, APP_CONFIG

def initialize_session():
    if 'session_initialized' not in st.session_state:
        st.session_state.username = 'Demo User'
        st.session_state.user_role = AUTH_CONFIG['default_role']
        st.session_state.session_initialized = True
        st.session_state.login_audited = False

# --- THE FIX IS HERE ---
def check_page_authorization():
    """
    This is the security gate for each page. It checks if the current user's role
    is in the list of authorized roles for the current page.
    This should be called at the top of every page script in the pages/ directory.
    """
    # Ensure session is initialized, especially on direct page access
    initialize_session() 
    
    current_page_script = os.path.basename(st.current_script_path)
    user_role = st.session_state.get('user_role', '')
    
    authorized_roles = AUTH_CONFIG["page_permissions"].get(current_page_script)
    
    # If page has no permissions defined, or if user's role is not in the list, deny access
    if authorized_roles is None or user_role not in authorized_roles:
        st.error("🔒 Access Denied")
        st.warning(f"Your assigned role ('{user_role}') does not have permission to view this page.")
        st.page_link("VERITAS_app.py", label="Return to Command Center", icon="⬅️")
        st.stop() # Stop the script to prevent any further rendering

def render_main_sidebar():
    st.sidebar.title("VERITAS")
    st.sidebar.caption("Vertex Ensured Reporting & Integrity Transformation Automation Suite")
    st.sidebar.markdown("---")
    st.sidebar.info(f"Welcome, **{st.session_state.get('username', 'User')}**")

    role_options = AUTH_CONFIG['role_options']
    try:
        current_role_index = role_options.index(st.session_state.user_role)
    except ValueError:
        current_role_index = 0
    
    selected_role = st.sidebar.selectbox(
        "Switch Role View", options=role_options, index=current_role_index,
        help="Switch roles to see how dashboards and permissions change."
    )
    
    if selected_role != st.session_state.user_role:
        st.session_state.user_role = selected_role
        from utils.data_connector import write_to_audit_log
        write_to_audit_log(
            _connection=st.session_state.get('db_connection'), user=st.session_state.username,
            action="Role View Changed", details=f"Switched to '{selected_role}' view."
        )
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Reset Session / Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def display_compliance_footer():
    st.markdown("---")
    footer_html = f"""
    <div style="text-align: center; font-size: 0.8em; color: grey; padding-top: 2em;">
        <p>VERITAS {APP_CONFIG['app_version']} | For Internal Vertex Use Only</p>
        <p><strong>GxP Compliance Notice:</strong> All actions are logged. Data integrity is enforced per <strong>21 CFR Part 11</strong>.</p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
