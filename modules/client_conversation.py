import streamlit as st
from utils.input_type_handler import render_research_input_options, load_mock_research
from utils.google_sheets_logger import log_session_data

def client_conversation_module():
    """Client Conversation Module - Step 2 of the workflow"""
    
    # Initialize session data if not exists
    if 'client_conversation_data' not in st.session_state.session_data:
        st.session_state.session_data['client_conversation_data'] = {}
    
    client_data = st.session_state.session_data['client_conversation_data']
    
    # Determine current substep (transcript -> info)
    current_substep = client_data.get('current_substep', 'client_transcript')
    
    if current_substep == 'client_transcript':
        step_client_transcript(client_data)
    elif current_substep == 'client_info':
        step_client_info(client_data)
    else:
        st.error("Invalid substep in client conversation")

def step_client_transcript(client_data):
    """Step 2A: Client Transcript Generation"""
    st.markdown("## 📝 Step 2A: Client Conversation Transcript")

    # Show context from previous step
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')

    st.info(f"**Topic:** {topic}")

    # Model recommendation
    st.info("💡 **Recommended model for best generation results:** ChatGPT-5")
    
    if topic_data.get('research_output'):
        with st.expander("📚 Previous Research (for context)", expanded=False):
            st.text_area("Research content:", value=topic_data['research_output'][:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Transcript", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'client_transcript',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'client_transcript'
                )
                if success:
                    client_data['transcript_output'] = mock_content
                    client_data['transcript_method_used'] = method
                    client_data['transcript_doc_id'] = doc_id
                    client_data['current_substep'] = 'client_info'
                    st.success("Mock transcript loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Generate Client Conversation Transcript
    Create or provide a realistic client conversation that demonstrates:
    - Client needs and pain points
    - Project requirements discussion  
    - Learning objectives and goals
    - Timeline and resource constraints
    """)
    
    # Prepare context for AI generation (including topic research)
    context_data = {
        'topic': topic,
        'topic_research': topic_data.get('research_output', '')
    }
    
    # Use enhanced input handler with context
    success, transcript_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'client_transcript',
        'client_transcript',  # prompt type for AI
        context_data=context_data
    )
    
    if success:
        # Save transcript data to session
        client_data['transcript_output'] = transcript_content
        client_data['transcript_method_used'] = method_used
        client_data['transcript_doc_id'] = doc_id
        
        # Move to next substep
        client_data['current_substep'] = 'client_info'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Topic Research"):
        st.session_state.current_step = 1
        st.rerun()

def step_client_info(client_data):
    """Step 2B: Client Information Extraction"""
    st.markdown("## 📊 Step 2B: Client Information Extraction")

    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')

    st.info(f"**Topic:** {topic}")

    # Model recommendation
    st.info("💡 **Recommended model for best generation results:** ChatGPT-5")
    
    # Show previous transcript
    transcript_content = client_data.get('transcript_output', '')
    if transcript_content:
        with st.expander("📝 Client Transcript (for context)", expanded=False):
            st.text_area("Transcript content:", value=transcript_content[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Client Info", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'client_information',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'client_info'
                )
                if success:
                    client_data['info_output'] = mock_content
                    client_data['info_method_used'] = method
                    client_data['info_doc_id'] = doc_id
                    st.success("Mock client info loaded!")
                    # Move to next module
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Extract Structured Client Information
    Analyze and extract key information from the client conversation:
    - **Client Profile:** Company, industry, size, stakeholders
    - **Project Scope:** Goals, objectives, success metrics
    - **Requirements:** Technical, business, compliance needs
    - **Constraints:** Budget, timeline, resources, limitations
    - **Learning Outcomes:** Skills to develop, knowledge gaps
    """)
    
    # Prepare context for AI generation (only transcript needed)
    context_data = {
        'client_transcript': transcript_content
    }
    
    # Use the centralized input handler with enhanced context
    success, info_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'client_info',
        'client_information',  # prompt type for AI
        context_data=context_data
    )
    
    if success:
        # Save client info data to session
        client_data['info_output'] = info_content
        client_data['info_method_used'] = method_used
        client_data['info_doc_id'] = doc_id
        
        # Move to next workflow step (Model Deliverable)
        st.session_state.current_step = 3
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Transcript"):
            client_data['current_substep'] = 'client_transcript'
            st.rerun()
    with col2:
        if st.button("⬅️ Back to Topic Research"):
            st.session_state.current_step = 1
            st.rerun()

