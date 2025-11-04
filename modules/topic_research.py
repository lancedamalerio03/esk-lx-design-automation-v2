import streamlit as st
from utils.input_type_handler import render_research_input_options, load_mock_research
from utils.google_sheets_logger import log_session_data

def topic_research_module():
    """Topic Research Module - Step 1 of the workflow"""
    
    # Initialize session data if not exists
    if 'topic_research_data' not in st.session_state.session_data:
        st.session_state.session_data['topic_research_data'] = {}
    
    topic_data = st.session_state.session_data['topic_research_data']
    
    # Determine current substep
    current_substep = topic_data.get('current_substep', 'topic_entry')
    
    if current_substep == 'topic_entry':
        step_topic_entry(topic_data)
    elif current_substep == 'research_options':
        step_research_options(topic_data)
    else:
        st.error("Invalid substep in topic research")

def step_topic_entry(topic_data):
    """Step 1: Topic Entry"""
    st.markdown("## 🔍 LX Design and Sprint Generator")
    
    # One-time welcome message
    if not topic_data.get('welcome_shown'):
        welcome = (
            "Welcome to the LX Design and Sprint Generator! 🚀\n\n"
            "We'll work together to transform your ideas into comprehensive learning sprints."
        )
        st.markdown(welcome)
        topic_data['welcome_shown'] = True
    
    st.markdown("---")

    # Get existing topic if any
    current_topic = topic_data.get('user_topic', '')

    # Instructions for topic entry
    st.markdown("""
    ### How to formulate your topic

    Enter your topic or area of interest and you can follow this formula as a guide to improve your prompt results:

    **[Topic/Outcome you want to explore] + [Industry/Company/Context] + [Location]**

    *Optional: you can include information on who your target audience is to add more specificity!*

    **Examples:**
    - AI agents for banking analytics in the Philippines
    - Effective internal communication in the age of AI for globally remote workplaces
    - Modern product management for global banking
    - Introducing AI to Human Resources practice in the Philippines
    - Implementing ethical AI practices within secondary education in the Philippines for high school students
    """)

    st.markdown("---")

    # Topic input
    topic = st.text_area(
        "Enter your topic or area of interest:",
        height=150,
        placeholder="e.g. AI agents for banking analytics in the Philippines",
        value=current_topic,
        key="topic_input_key"
    )
    
    # Continue button
    if st.button("🚀 Continue to Research Options", use_container_width=True):
        if topic and topic.strip():
            # Save topic to session data
            topic_data['user_topic'] = topic.strip()
            topic_data['current_substep'] = 'research_options'
            
            # Log this step
            log_session_data(
                st.session_state.session_id,
                'topic_entry_completed',
                {'topic': topic.strip()}
            )
            
            st.success(f"✅ Topic saved: {topic.strip()}")
            st.rerun()
        else:
            st.error("Please enter a topic to continue.")

def step_research_options(topic_data):
    """Step 2: Research Options"""
    st.markdown("## 📚 Topic Research")

    topic = topic_data.get('user_topic', 'Unknown topic')
    st.info(f"**Your Topic:** {topic}")

    # Model recommendation
    st.info("💡 **Recommended model for best research results:** Perplexity Sonar Reasoning Pro")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Data", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'topic_research',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'topic'
                )
                if success:
                    topic_data['research_output'] = mock_content
                    topic_data['research_method_used'] = method
                    topic_data['research_doc_id'] = doc_id
                    st.success("Mock research data loaded!")
                    # Move to next step
                    st.session_state.current_step = 2
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Use the centralized input handler
    success, research_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'topic'
    )
    
    if success:
        # Save research data to session
        topic_data['research_output'] = research_content
        topic_data['research_method_used'] = method_used
        topic_data['research_doc_id'] = doc_id
        
        # Move to next workflow step (Client Conversation)
        st.session_state.current_step = 2
        st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Topic Entry"):
        topic_data['current_substep'] = 'topic_entry'
        st.rerun()