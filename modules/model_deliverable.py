import streamlit as st
from utils.input_type_handler import load_mock_research, render_research_input_options
from utils.google_sheets_logger import log_session_data

def model_deliverable_module():
    """Model Deliverable Module - Step 3 of the workflow"""
    
    # Initialize session data if not exists
    if 'model_deliverable_data' not in st.session_state.session_data:
        st.session_state.session_data['model_deliverable_data'] = {}
    
    model_data = st.session_state.session_data['model_deliverable_data']
    
    # Determine current substep (model_research -> model_deliverable)
    current_substep = model_data.get('current_substep', 'model_research')
    
    if current_substep == 'model_research':
        step_model_research(model_data)
    elif current_substep == 'model_deliverable':
        step_model_deliverable(model_data)
    else:
        st.error("Invalid substep in model deliverable")

def step_model_research(model_data):
    """Step 3A: Model Research"""
    st.markdown("## 🔬 Step 3A: Model Research")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous client info
    client_info = client_data.get('info_output', '')
    if client_info:
        with st.expander("📊 Client Information (for context)", expanded=False):
            st.text_area("Client info content:", value=client_info[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Model Research", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'model_research',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'model_research'
                )
                if success:
                    model_data['research_output'] = mock_content
                    model_data['research_method_used'] = method
                    model_data['research_doc_id'] = doc_id
                    model_data['current_substep'] = 'model_deliverable'
                    st.success("Mock model research loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Conduct Model Research
    Research and analyze existing learning models and approaches relevant to your topic:
    - **Best Practices:** Industry standards and proven methodologies
    - **Learning Models:** Theoretical frameworks and pedagogical approaches
    - **Case Studies:** Successful implementations and lessons learned
    - **Tools & Technologies:** Relevant platforms and delivery methods
    """)
    
    # Prepare context for AI generation
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'client_information': client_info
    }
    
    # Use enhanced input handler with context
    success, research_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'model_research',
        'model_deliverable_researcher',  # prompt type for AI
        context_data=context_data
    )
    
    if success:
        # Save model research data to session
        model_data['research_output'] = research_content
        model_data['research_method_used'] = method_used
        model_data['research_doc_id'] = doc_id
        
        # Move to next substep
        model_data['current_substep'] = 'model_deliverable'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Client Conversation"):
        st.session_state.current_step = 2
        st.rerun()

def step_model_deliverable(model_data):
    """Step 3B: Model Deliverable Creation"""
    st.markdown("## 🎯 Step 3B: Model Deliverable Creation")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous model research
    research_content = model_data.get('research_output', '')
    if research_content:
        with st.expander("🔬 Model Research (for context)", expanded=False):
            st.text_area("Research content:", value=research_content[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Model Deliverable", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'model_deliverable',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'model_deliverable'
                )
                if success:
                    model_data['deliverable_output'] = mock_content
                    model_data['deliverable_method_used'] = method
                    model_data['deliverable_doc_id'] = doc_id
                    st.success("Mock model deliverable loaded!")
                    # Move to next module
                    st.session_state.current_step = 4
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Create Model Deliverable
    Design the complete learning experience model based on research and client needs:
    - **Learning Architecture:** Structure, flow, and delivery approach
    - **Content Framework:** Modules, lessons, and learning objectives
    - **Assessment Strategy:** Evaluation methods and success metrics
    - **Implementation Plan:** Timeline, resources, and delivery methods
    """)
    
    # Prepare context for AI generation
    context_data = {
        'model_deliverable_research': research_content,
        'client_information': client_data.get('info_output', '')
    }
    
    # Use the centralized input handler with enhanced context
    success, deliverable_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'model_deliverable',
        'model_deliverable_generation',  # prompt type for AI
        context_data=context_data
    )
    
    if success:
        # Save model deliverable data to session
        model_data['deliverable_output'] = deliverable_content
        model_data['deliverable_method_used'] = method_used
        model_data['deliverable_doc_id'] = doc_id
        
        # Move to next workflow step (PRD Generation)
        st.session_state.current_step = 4
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Model Research"):
            model_data['current_substep'] = 'model_research'
            st.rerun()
    with col2:
        if st.button("⬅️ Back to Client Conversation"):
            st.session_state.current_step = 2
            st.rerun()