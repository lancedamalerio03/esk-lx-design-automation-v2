import streamlit as st
import uuid
from datetime import datetime
from utils.google_auth import authenticate_user
from utils.google_drive_manager import create_session_folder, get_folder_url
from utils.google_sheets_logger import log_session_data, create_session_log_sheet
from modules.topic_research import topic_research_module
from modules.client_conversation import client_conversation_module
from modules.model_deliverable import model_deliverable_module
from modules.prd import prd_module

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="LX Design Automation v2",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Authenticate user first
    if not authenticate_user():
        st.stop()  # Stop execution if not authenticated
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.current_step = 1
        st.session_state.session_data = {}
        st.session_state.session_folder_id = None
        st.session_state.session_log_sheet_id = None
    
    # Create session folder in OUTPUTS automatically
    if not st.session_state.session_folder_id:
        folder_id = create_session_folder(st.session_state.session_id)
        if folder_id:
            st.session_state.session_folder_id = folder_id
            # Clear LAST CREATED folder for new session
            from utils.google_drive_manager import clear_last_created_folder
            clear_last_created_folder()
            # Create session log sheet
            log_sheet_id = create_session_log_sheet(st.session_state.session_id)
            if log_sheet_id:
                st.session_state.session_log_sheet_id = log_sheet_id
    
    # Sidebar navigation
    render_sidebar()
    
    # Main content area
    render_main_content()

def render_sidebar():
    """Render the sidebar with navigation and session info"""
    with st.sidebar:
        st.header("LX Design v2")
        
        # Session info
        st.markdown("### 📋 Session Info")
        st.info(f"**Session ID:** {st.session_state.session_id}")
        
        # Display folder link
        if st.session_state.session_folder_id:
            folder_url = get_folder_url(st.session_state.session_folder_id)
            st.markdown(f"📁 [Session Folder]({folder_url})")
        else:
            st.info("Creating session folder in OUTPUTS...")
        
        st.markdown("---")
        
        # Workflow steps
        st.markdown("### Workflow Steps")
        
        steps = [
            "1. Topic Research",
            "2. Client Conversation", 
            "3. Model Deliverable",
            "4. PRD Generation"
        ]
        
        for i, step in enumerate(steps, 1):
            if st.button(
                step,
                key=f"nav_step_{i}",
                type="primary" if st.session_state.current_step == i else "secondary",
                use_container_width=True
            ):
                st.session_state.current_step = i
                st.rerun()
        
        st.markdown("---")
        
        # Developer mode toggle
        st.markdown("### Developer Mode")
        developer_mode = st.toggle("Enable Developer Mode", value=False)
        st.session_state.developer_mode = developer_mode
        
        if developer_mode:
            st.markdown("#### Quick Actions")
            if st.button("Reset Session", use_container_width=True):
                # Clear session state
                for key in list(st.session_state.keys()):
                    if key not in ['credentials']:  # Keep authentication
                        del st.session_state[key]
                st.rerun()
            
            if st.button("=� View Session Data", use_container_width=True):
                st.session_state.show_debug = not st.session_state.get('show_debug', False)

def render_main_content():
    """Render the main content based on current step"""
    
    # Debug panel (if developer mode is enabled)
    if st.session_state.get('developer_mode', False) and st.session_state.get('show_debug', False):
        with st.expander("Debug Info", expanded=True):
            st.json(st.session_state.session_data)
    
    # Route to appropriate module based on current step
    if st.session_state.current_step == 1:
        topic_research_module()
    elif st.session_state.current_step == 2:
        client_conversation_module()
    elif st.session_state.current_step == 3:
        model_deliverable_module()
    elif st.session_state.current_step == 4:
        prd_module()
    else:
        st.error("Invalid step selected")

def log_step_completion(step_name, data):
    """Log completion of a workflow step"""
    if st.session_state.session_log_sheet_id:
        log_session_data(
            st.session_state.session_id,
            step_name,
            data,
            st.session_state.session_log_sheet_id
        )

if __name__ == "__main__":
    main()