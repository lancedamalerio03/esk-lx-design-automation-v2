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
    success, transcript_content, method_used, doc_id = render_research_input_options_with_context(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'client_transcript',
        'client_transcript',  # prompt type for AI
        context_data
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
    success, info_content, method_used, doc_id = render_research_input_options_with_context(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'client_info',
        'client_information',  # prompt type for AI
        context_data
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

def render_research_input_options_with_context(topic, session_folder_id, session_id, step_name, prompt_type, context_data):
    """Enhanced version of input handler that passes context data for AI generation"""
    
    # Styling for the research options
    st.markdown(
        """
        <style>
        .seg-card {
        background: linear-gradient(135deg, #2ba7a0 0%, #3ac0a2 100%);
        padding: 18px 20px; border-radius: 20px; margin-top: 8px; margin-bottom: 12px;
        }
        .seg-inner {
        background: rgba(255,255,255,0.10);
        border-radius: 14px; padding: 10px 12px;
        }
        .seg-inner div[data-baseweb="radio"] > div { gap: 14px !important; flex-wrap: nowrap; }
        .seg-inner label {
        border-radius: 999px !important; padding: 6px 12px !important;
        background: rgba(255,255,255,0.06); transition: background .15s ease;
        }
        .seg-inner label:hover { background: rgba(255,255,255,0.12); }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### ✍️ How would you like to provide the information?")
    st.markdown('<div class="seg-card"><div class="seg-inner">', unsafe_allow_html=True)
    mode = st.radio(
        "Choose a method:",
        options=["Paste text", "Upload a PDF", "Ask AI to help"],
        horizontal=True,
        help="Paste notes, upload a PDF, or let AI generate structured information.",
        label_visibility="visible",
        key=f"info_method_{step_name}"
    )
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Handle different input modes
    if mode == "Paste text":
        return handle_paste_input(topic, session_folder_id, session_id, step_name)
    elif mode == "Upload a PDF":
        return handle_pdf_upload(topic, session_folder_id, session_id, step_name)
    elif mode == "Ask AI to help":
        return handle_ai_generation_with_context(topic, session_folder_id, session_id, step_name, prompt_type, context_data)
    
    return False, None, None, None

def handle_paste_input(topic, session_folder_id, session_id, step_name):
    """Handle pasted text input"""
    from utils.input_type_handler import handle_paste_input as base_handler
    return base_handler(topic, session_folder_id, session_id, step_name)

def handle_pdf_upload(topic, session_folder_id, session_id, step_name):
    """Handle PDF upload"""
    from utils.input_type_handler import handle_pdf_upload as base_handler
    return base_handler(topic, session_folder_id, session_id, step_name)

def handle_ai_generation_with_context(topic, session_folder_id, session_id, step_name, prompt_type, context_data):
    """Handle AI generation with enhanced context"""
    if step_name == 'client_transcript':
        description = "Let AI create a realistic client conversation based on your topic and research."
        button_text = "🤖 Generate Client Transcript"
        spinner_text = "🧠 Creating client conversation..."
    else:
        description = "Let AI analyze the client conversation and extract structured information."
        button_text = "🤖 Generate Client Information" 
        spinner_text = "🧠 Analyzing client conversation..."
    
    st.markdown(description)
    
    if st.button(button_text, use_container_width=True, key=f"ai_generate_{step_name}"):
        with st.spinner(spinner_text):
            try:
                # Get the meta prompt and module prompt from Google Docs
                from utils.google_docs_fetcher import get_prompt_content
                meta_prompt = get_prompt_content('meta_prompt')
                module_prompt = get_prompt_content(prompt_type)
                
                if not meta_prompt or not module_prompt:
                    st.error("Could not retrieve AI prompts. Please check your Google Docs access.")
                    return False, None, None, None
                
                # Combine meta prompt with module prompt
                combined_prompt = f"{meta_prompt}\n\n{module_prompt}"
                
                # Generate AI response with context
                from AI.generate_ai_response import generate_ai_response
                client_info = generate_ai_response(combined_prompt, context_data)
                
                if client_info:
                    # Create Google Doc with the information
                    from utils.google_drive_manager import create_google_doc
                    doc_title = f"{step_name.title().replace('_', ' ')} - {topic} (AI Generated)"
                    doc_content = f"# AI {step_name.title().replace('_', ' ')}: {topic}\n\n## Method: AI Generated\n\n{client_info}"
                    
                    doc_id = create_google_doc(doc_title, doc_content, session_folder_id)
                    
                    # Log this step
                    from utils.google_sheets_logger import log_session_data
                    log_session_data(
                        session_id,
                        f'{step_name}_completed',
                        {
                            'topic': topic,
                            'method': 'ai_generated',
                            'prompt_type': prompt_type,
                            'doc_id': doc_id,
                            'content_length': len(client_info),
                            'context_provided': list(context_data.keys())
                        }
                    )
                    
                    st.success("✅ Client information generated and saved!")
                    return True, client_info, f'ai_generated:{prompt_type}', doc_id
                else:
                    st.error("Failed to generate client information. Please try again.")
                    return False, None, None, None
                    
            except Exception as e:
                st.error(f"Error generating client information: {str(e)}")
                return False, None, None, None
    
    return False, None, None, None