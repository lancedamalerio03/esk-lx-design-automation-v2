import streamlit as st
import uuid
from datetime import datetime
from utils.google_auth import authenticate_user
from utils.google_drive_manager import create_session_folder, get_folder_url, get_document_url
from utils.google_sheets_logger import log_session_data, create_session_log_sheet, log_session_update, get_user_email
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

def render_document_links():
    """Render document links for created documents"""
    st.markdown("### 📄 Generated Documents")
    
    session_data = st.session_state.get('session_data', {})
    
    # Topic Research documents
    topic_data = session_data.get('topic_research_data', {})
    if topic_data.get('research_doc_id'):
        doc_url = get_document_url(topic_data['research_doc_id'])
        st.markdown(f"📝 [Topic Research]({doc_url})")
    
    # Client Conversation documents
    client_data = session_data.get('client_conversation_data', {})
    if client_data.get('transcript_doc_id'):
        doc_url = get_document_url(client_data['transcript_doc_id'])
        st.markdown(f"🎤 [Client Transcript]({doc_url})")
    if client_data.get('info_doc_id'):
        doc_url = get_document_url(client_data['info_doc_id'])
        st.markdown(f"ℹ️ [Client Information]({doc_url})")
    
    # Model Deliverable documents
    model_data = session_data.get('model_deliverable_data', {})
    if model_data.get('research_doc_id'):
        doc_url = get_document_url(model_data['research_doc_id'])
        st.markdown(f"🔬 [Model Research]({doc_url})")
    if model_data.get('deliverable_doc_id'):
        doc_url = get_document_url(model_data['deliverable_doc_id'])
        st.markdown(f"📦 [Model Deliverable]({doc_url})")
    
    # PRD documents
    prd_data = session_data.get('prd_data', {})
    if prd_data.get('executive_summary_doc_id'):
        doc_url = get_document_url(prd_data['executive_summary_doc_id'])
        st.markdown(f"📊 [Executive Summary]({doc_url})")
    if prd_data.get('problem_statement_doc_id'):
        doc_url = get_document_url(prd_data['problem_statement_doc_id'])
        st.markdown(f"❓ [Problem Statement]({doc_url})")
    if prd_data.get('goals_and_success_doc_id'):
        doc_url = get_document_url(prd_data['goals_and_success_doc_id'])
        st.markdown(f"🎯 [Goals & Success]({doc_url})")
    if prd_data.get('roles_and_responsibilities_doc_id'):
        doc_url = get_document_url(prd_data['roles_and_responsibilities_doc_id'])
        st.markdown(f"👥 [Roles & Responsibilities]({doc_url})")
    if prd_data.get('constraints_and_assumptions_doc_id'):
        doc_url = get_document_url(prd_data['constraints_and_assumptions_doc_id'])
        st.markdown(f"⚠️ [Constraints & Assumptions]({doc_url})")
    if prd_data.get('evaluation_criteria_doc_id'):
        doc_url = get_document_url(prd_data['evaluation_criteria_doc_id'])
        st.markdown(f"✅ [Evaluation Criteria]({doc_url})")
    if prd_data.get('risk_and_mitigations_doc_id'):
        doc_url = get_document_url(prd_data['risk_and_mitigations_doc_id'])
        st.markdown(f"⚠️ [Risk & Mitigations]({doc_url})")
    if prd_data.get('final_prd_doc_id'):
        doc_url = get_document_url(prd_data['final_prd_doc_id'])
        st.markdown(f"📋 [Final PRD]({doc_url})")
    
    # Show message if no documents yet
    if not any([
        topic_data.get('research_doc_id'),
        client_data.get('transcript_doc_id'), client_data.get('info_doc_id'),
        model_data.get('research_doc_id'), model_data.get('deliverable_doc_id'),
        prd_data.get('executive_summary_doc_id'), prd_data.get('problem_statement_doc_id'),
        prd_data.get('goals_and_success_doc_id'), prd_data.get('roles_and_responsibilities_doc_id'),
        prd_data.get('constraints_and_assumptions_doc_id'), prd_data.get('evaluation_criteria_doc_id'),
        prd_data.get('risk_and_mitigations_doc_id'), prd_data.get('final_prd_doc_id')
    ]):
        st.info("No documents created yet")

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
        
        # Document Links
        render_document_links()
        
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
                # Log step change
                log_session_status_update()
                st.rerun()
        
        st.markdown("---")
        
        # Model Selection
        st.markdown("### 🤖 AI Model")
        available_models = [
            "gpt-5", "gpt-5-mini", "gpt-5-nano",
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", 
            "gpt-4o", "gpt-4o-mini",
            "o3", "o3-mini"
        ]
        
        # Get previous model to detect changes
        previous_model = st.session_state.get('previous_ai_model', 'gpt-5')
        
        selected_model = st.selectbox(
            "Choose AI Model:",
            options=available_models,
            index=0,  # Default to gpt-5
            key="selected_ai_model",
            disabled=False,  # Strict dropdown - no typing allowed
            help="Select from available OpenAI models. Model applies to next AI generation."
        )
        
        # Check if model changed and show notification
        if selected_model != previous_model:
            st.success(f"🔄 Model changed to **{selected_model}**")
            st.session_state.previous_ai_model = selected_model
        
        st.markdown("---")
        
        # Token usage tracking (always visible)
        st.markdown("### 📊 Token Usage")
        try:
            from AI.generate_ai_response import get_session_token_summary
            token_summary = get_session_token_summary()
            
            if token_summary and token_summary.get('steps_completed', 0) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Tokens", f"{token_summary['total_tokens']:,}")
                with col2:
                    st.metric("Total Cost", f"${token_summary['total_cost_usd']:.4f}")
                
                with st.expander("📈 Token Details"):
                    st.write(f"**Input Tokens:** {token_summary['input_tokens']:,}")
                    st.write(f"**Output Tokens:** {token_summary['output_tokens']:,}")
                    st.write(f"**Steps Completed:** {token_summary['steps_completed']}")
                    st.write(f"**Avg Tokens/Step:** {token_summary['avg_tokens_per_step']:.0f}")
                    st.write(f"**Avg Cost/Step:** ${token_summary['avg_cost_per_step']:.4f}")
            else:
                st.info("No AI calls yet this session")
        except ImportError as e:
            st.warning(f"Token tracking not available: {e}")
        except Exception as e:
            st.warning(f"Token tracking error: {e}")
        
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
            
            if st.button("🔍 View Session Data", use_container_width=True):
                st.session_state.show_debug = not st.session_state.get('show_debug', False)
            
            # Simple debug info (always visible when dev mode is on)
            st.markdown("#### Debug Info")
            st.write(f"Session ID: {st.session_state.get('session_id', 'None')}")
            st.write(f"User Email: {get_user_email()}")
            
            try:
                from keys.config import lx_design_logger_sheet
                st.write(f"Sheet ID: {lx_design_logger_sheet}")
            except Exception as e:
                st.write(f"Sheet ID Error: {e}")
                
            # Very simple test
            if st.button("🧪 Simple Test"):
                st.success("Button clicked successfully!")
                # Try one simple log call
                try:
                    result = log_session_update(
                        session_id="SIMPLE_TEST",
                        user_path="test_user", 
                        current_step="test",
                        status="button_test",
                        api_calls=1,
                        total_tokens=0
                    )
                    st.write(f"Log result: {result}")
                    if result:
                        st.success("✅ Logging function returned True - check your sheet!")
                    else:
                        st.error("❌ Logging function returned False")
                except Exception as e:
                    st.error(f"Logging error: {e}")

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

def log_session_status_update():
    """Log session status updates to Session_Logs"""
    try:
        from AI.generate_ai_response import get_session_token_summary
        from utils.google_sheets_logger import get_session_logs
        
        token_summary = get_session_token_summary()
        
        # Get count of all detailed logs (including non-AI) for this session
        try:
            logs = get_session_logs(st.session_state.session_id)
            total_actions = len(logs.get('detailed_logs', []))
        except:
            total_actions = token_summary.get('steps_completed', 0)
        
        user_path = get_user_email()
        current_step = str(st.session_state.current_step)
        
        # Determine status based on current step and completion
        status = "in_progress"
        completed_at = None
        
        # Check if workflow is completed (step 4 and PRD is done)
        if st.session_state.current_step == 4:
            prd_data = st.session_state.session_data.get('prd_data', {})
            if prd_data.get('current_substep') == 'completed':
                status = "completed"
                completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_session_update(
            session_id=st.session_state.session_id,
            user_path=user_path,
            current_step=current_step,
            status=status,
            api_calls=total_actions,  # Now includes all actions, not just AI
            total_tokens=token_summary.get('total_tokens', 0),
            completed_at=completed_at
        )
    except Exception as e:
        print(f"Error logging session update: {e}")

if __name__ == "__main__":
    main()