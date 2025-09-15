import streamlit as st
import json
from utils.input_type_handler import load_mock_research, render_research_input_options
from utils.google_sheets_logger import log_session_data
from utils.google_drive_manager import copy_template_and_fill_placeholders, format_prd_data_for_template
from keys.config import prd_template

def prd_module():
    """PRD Module - Step 4 of the workflow"""
    
    # Initialize session data if not exists
    if 'prd_data' not in st.session_state.session_data:
        st.session_state.session_data['prd_data'] = {}
    
    prd_data = st.session_state.session_data['prd_data']
    
    # Determine current substep
    current_substep = prd_data.get('current_substep', 'executive_summary')
    
    if current_substep == 'executive_summary':
        step_executive_summary(prd_data)
    elif current_substep == 'problem_statement':
        step_problem_statement(prd_data)
    elif current_substep == 'goals_and_success':
        step_goals_and_success(prd_data)
    elif current_substep == 'roles_and_responsibilities':
        step_roles_and_responsibilities(prd_data)
    elif current_substep == 'constraints_and_assumptions':
        step_constraints_and_assumptions(prd_data)
    elif current_substep == 'evaluation_criteria':
        step_evaluation_criteria(prd_data)
    elif current_substep == 'risk_and_mitigations':
        step_risk_and_mitigations(prd_data)
    elif current_substep == 'prd_generator':
        step_prd_generator(prd_data)
    else:
        st.error("Invalid substep in PRD generation")

def step_executive_summary(prd_data):
    """Step 4A: Executive Summary"""
    st.markdown("## 📋 Step 4A: PRD Executive Summary")
    
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
            if st.button("🎭 Load Mock Executive Summary", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'executive_summary'
                )
                if success:
                    prd_data['executive_summary_output'] = mock_content
                    prd_data['executive_summary_method_used'] = method
                    prd_data['executive_summary_doc_id'] = doc_id
                    prd_data['current_substep'] = 'problem_statement'
                    st.success("Mock executive summary loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Create Executive Summary
    Develop a high-level overview that synthesizes all previous research:
    - **Vision Statement:** Clear articulation of the learning experience goal
    - **Key Stakeholders:** Primary audiences and their needs
    - **Success Metrics:** How success will be measured
    - **Implementation Overview:** High-level approach and timeline
    """)
    
    # Prepare context for AI generation - essential foundation context
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_info
    }
    
    # Use enhanced input handler with context
    success, summary_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_executive_summary',
        'prd_executive_summary',
        context_data
    )
    
    if success:
        # Save executive summary data to session
        prd_data['executive_summary_output'] = summary_content
        prd_data['executive_summary_method_used'] = method_used
        prd_data['executive_summary_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'problem_statement'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Model Deliverable"):
        st.session_state.current_step = 3
        st.rerun()

def step_problem_statement(prd_data):
    """Step 4B: Problem Statement"""
    st.markdown("## 🎯 Step 4B: PRD Problem Statement")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous executive summary
    executive_summary = prd_data.get('executive_summary_output', '')
    if executive_summary:
        with st.expander("📋 Executive Summary (for context)", expanded=False):
            st.text_area("Executive summary content:", value=executive_summary[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Problem Statement", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'problem_statement'
                )
                if success:
                    prd_data['problem_statement_output'] = mock_content
                    prd_data['problem_statement_method_used'] = method
                    prd_data['problem_statement_doc_id'] = doc_id
                    prd_data['current_substep'] = 'goals_and_success'
                    st.success("Mock problem statement loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Define Problem Statement
    Clearly articulate the learning challenge this PRD will address:
    - **Current State:** What's the existing situation or gap?
    - **Desired State:** What outcome do we want to achieve?
    - **Impact:** Why is solving this problem important?
    - **Constraints:** What limitations must be considered?
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': executive_summary
    }
    
    # Use enhanced input handler with context
    success, problem_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_problem_statement',
        'prd_problem_statement',
        context_data
    )
    
    if success:
        # Save problem statement data to session
        prd_data['problem_statement_output'] = problem_content
        prd_data['problem_statement_method_used'] = method_used
        prd_data['problem_statement_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'goals_and_success'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Executive Summary"):
            prd_data['current_substep'] = 'executive_summary'
            st.rerun()
    with col2:
        if st.button("⬅️ Back to Model Deliverable"):
            st.session_state.current_step = 3
            st.rerun()

def step_goals_and_success(prd_data):
    """Step 4C: Goals and Success Metrics"""
    st.markdown("## 🎯 Step 4C: Goals and Success Metrics")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous problem statement
    problem_statement = prd_data.get('problem_statement_output', '')
    if problem_statement:
        with st.expander("🎯 Problem Statement (for context)", expanded=False):
            st.text_area("Problem statement content:", value=problem_statement[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Goals and Success", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'goals_and_success'
                )
                if success:
                    prd_data['goals_and_success_output'] = mock_content
                    prd_data['goals_and_success_method_used'] = method
                    prd_data['goals_and_success_doc_id'] = doc_id
                    prd_data['current_substep'] = 'roles_and_responsibilities'
                    st.success("Mock goals and success loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Define Goals and Success Metrics
    Establish clear objectives and how success will be measured:
    - **Learning Objectives:** What learners should achieve
    - **Business Goals:** How this supports organizational objectives
    - **Success Metrics:** Quantifiable measures of success
    - **Key Performance Indicators:** Specific metrics to track
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': problem_statement
    }
    
    # Use enhanced input handler with context
    success, goals_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_goals_and_success',
        'prd_goals_and_success_metrics',
        context_data
    )
    
    if success:
        # Save goals and success data to session
        prd_data['goals_and_success_output'] = goals_content
        prd_data['goals_and_success_method_used'] = method_used
        prd_data['goals_and_success_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'roles_and_responsibilities'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Problem Statement"):
        prd_data['current_substep'] = 'problem_statement'
        st.rerun()

def step_roles_and_responsibilities(prd_data):
    """Step 4D: Roles and Responsibilities"""
    st.markdown("## 👥 Step 4D: Roles and Responsibilities")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous goals and success
    goals_and_success = prd_data.get('goals_and_success_output', '')
    if goals_and_success:
        with st.expander("🎯 Goals and Success Metrics (for context)", expanded=False):
            st.text_area("Goals and success content:", value=goals_and_success[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Roles and Responsibilities", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'roles_and_responsibilities'
                )
                if success:
                    prd_data['roles_and_responsibilities_output'] = mock_content
                    prd_data['roles_and_responsibilities_method_used'] = method
                    prd_data['roles_and_responsibilities_doc_id'] = doc_id
                    prd_data['current_substep'] = 'constraints_and_assumptions'
                    st.success("Mock roles and responsibilities loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Define Roles and Responsibilities
    Identify key stakeholders and their roles in the learning experience:
    - **Project Stakeholders:** Who is involved and their responsibilities
    - **Learning Participants:** Target audience and their expected engagement
    - **Support Roles:** Facilitators, mentors, technical support
    - **Decision Makers:** Who has authority for key decisions
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': prd_data.get('problem_statement_output', ''),
        'goals_and_success': goals_and_success
    }
    
    # Use enhanced input handler with context
    success, roles_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_roles_and_responsibilities',
        'prd_roles_and_responsibilities',
        context_data
    )
    
    if success:
        # Save roles and responsibilities data to session
        prd_data['roles_and_responsibilities_output'] = roles_content
        prd_data['roles_and_responsibilities_method_used'] = method_used
        prd_data['roles_and_responsibilities_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'constraints_and_assumptions'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Goals and Success"):
        prd_data['current_substep'] = 'goals_and_success'
        st.rerun()

def step_constraints_and_assumptions(prd_data):
    """Step 4E: Constraints and Assumptions"""
    st.markdown("## ⚠️ Step 4E: Constraints and Assumptions")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous roles and responsibilities
    roles_and_responsibilities = prd_data.get('roles_and_responsibilities_output', '')
    if roles_and_responsibilities:
        with st.expander("👥 Roles and Responsibilities (for context)", expanded=False):
            st.text_area("Roles and responsibilities content:", value=roles_and_responsibilities[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Constraints and Assumptions", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'constraints_and_assumptions'
                )
                if success:
                    prd_data['constraints_and_assumptions_output'] = mock_content
                    prd_data['constraints_and_assumptions_method_used'] = method
                    prd_data['constraints_and_assumptions_doc_id'] = doc_id
                    prd_data['current_substep'] = 'evaluation_criteria'
                    st.success("Mock constraints and assumptions loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Document Constraints and Assumptions
    Identify limitations and assumptions that will guide the PRD:
    - **Resource Constraints:** Budget, time, personnel limitations
    - **Technical Constraints:** Platform, technology, infrastructure limits
    - **Organizational Constraints:** Policies, compliance, cultural factors
    - **Key Assumptions:** What we're assuming to be true for planning
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': prd_data.get('problem_statement_output', ''),
        'goals_and_success': prd_data.get('goals_and_success_output', ''),
        'roles_and_responsibilities': roles_and_responsibilities
    }
    
    # Use enhanced input handler with context
    success, constraints_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_constraints_and_assumptions',
        'prd_constraints_and_assumptions',
        context_data
    )
    
    if success:
        # Save constraints and assumptions data to session
        prd_data['constraints_and_assumptions_output'] = constraints_content
        prd_data['constraints_and_assumptions_method_used'] = method_used
        prd_data['constraints_and_assumptions_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'evaluation_criteria'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Roles and Responsibilities"):
        prd_data['current_substep'] = 'roles_and_responsibilities'
        st.rerun()

def step_evaluation_criteria(prd_data):
    """Step 4F: Evaluation Criteria"""
    st.markdown("## 📊 Step 4F: Evaluation Criteria")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous constraints and assumptions
    constraints_and_assumptions = prd_data.get('constraints_and_assumptions_output', '')
    if constraints_and_assumptions:
        with st.expander("⚠️ Constraints and Assumptions (for context)", expanded=False):
            st.text_area("Constraints and assumptions content:", value=constraints_and_assumptions[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Evaluation Criteria", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'evaluation_criteria'
                )
                if success:
                    prd_data['evaluation_criteria_output'] = mock_content
                    prd_data['evaluation_criteria_method_used'] = method
                    prd_data['evaluation_criteria_doc_id'] = doc_id
                    prd_data['current_substep'] = 'risk_and_mitigations'
                    st.success("Mock evaluation criteria loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Define Evaluation Criteria
    Establish how the learning experience will be assessed and improved:
    - **Assessment Methods:** How learner progress will be evaluated
    - **Quality Standards:** Criteria for content and delivery quality
    - **Feedback Mechanisms:** How feedback will be collected and used
    - **Continuous Improvement:** Process for ongoing refinement
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': prd_data.get('problem_statement_output', ''),
        'goals_and_success': prd_data.get('goals_and_success_output', ''),
        'roles_and_responsibilities': prd_data.get('roles_and_responsibilities_output', ''),
        'constraints_and_assumptions': constraints_and_assumptions
    }
    
    # Use enhanced input handler with context
    success, evaluation_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_evaluation_criteria',
        'prd_evaluation_criteria',
        context_data
    )
    
    if success:
        # Save evaluation criteria data to session
        prd_data['evaluation_criteria_output'] = evaluation_content
        prd_data['evaluation_criteria_method_used'] = method_used
        prd_data['evaluation_criteria_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'risk_and_mitigations'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Constraints and Assumptions"):
        prd_data['current_substep'] = 'constraints_and_assumptions'
        st.rerun()

def step_risk_and_mitigations(prd_data):
    """Step 4G: Risk and Mitigations"""
    st.markdown("## 🛡️ Step 4G: Risk and Mitigations")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous evaluation criteria
    evaluation_criteria = prd_data.get('evaluation_criteria_output', '')
    if evaluation_criteria:
        with st.expander("📊 Evaluation Criteria (for context)", expanded=False):
            st.text_area("Evaluation criteria content:", value=evaluation_criteria[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Risk and Mitigations", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'risk_and_mitigations'
                )
                if success:
                    prd_data['risk_and_mitigations_output'] = mock_content
                    prd_data['risk_and_mitigations_method_used'] = method
                    prd_data['risk_and_mitigations_doc_id'] = doc_id
                    prd_data['current_substep'] = 'prd_generator'
                    st.success("Mock risk and mitigations loaded!")
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Identify Risks and Mitigations
    Anticipate potential challenges and plan responses:
    - **Technical Risks:** Platform, integration, or delivery issues
    - **Engagement Risks:** Learner participation and completion challenges
    - **Resource Risks:** Budget, timeline, or staffing concerns
    - **Mitigation Strategies:** Specific actions to address each risk
    """)
    
    # Prepare context for AI generation - foundational + cumulative PRD context
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': prd_data.get('problem_statement_output', ''),
        'goals_and_success': prd_data.get('goals_and_success_output', ''),
        'roles_and_responsibilities': prd_data.get('roles_and_responsibilities_output', ''),
        'constraints_and_assumptions': prd_data.get('constraints_and_assumptions_output', ''),
        'evaluation_criteria': evaluation_criteria
    }
    
    # Use enhanced input handler with context
    success, risk_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'prd_risk_and_mitigations',
        'prd_risk_and_mitigations',
        context_data
    )
    
    if success:
        # Save risk and mitigations data to session
        prd_data['risk_and_mitigations_output'] = risk_content
        prd_data['risk_and_mitigations_method_used'] = method_used
        prd_data['risk_and_mitigations_doc_id'] = doc_id
        
        # Move to next substep
        prd_data['current_substep'] = 'prd_generator'
        st.rerun()
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Evaluation Criteria"):
        prd_data['current_substep'] = 'evaluation_criteria'
        st.rerun()

def step_prd_generator(prd_data):
    """Step 4H: Final PRD Generation"""
    st.markdown("## 📄 Step 4H: Final PRD Generation")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous risk and mitigations
    risk_and_mitigations = prd_data.get('risk_and_mitigations_output', '')
    if risk_and_mitigations:
        with st.expander("🛡️ Risk and Mitigations (for context)", expanded=False):
            st.text_area("Risk and mitigations content:", value=risk_and_mitigations[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Handle mock data if in developer mode
    if st.session_state.get('developer_mode', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎭 Load Mock Final PRD", use_container_width=True):
                success, mock_content, method, doc_id = load_mock_research(
                    'prd',
                    topic,
                    st.session_state.session_folder_id,
                    st.session_state.session_id,
                    'final_prd'
                )
                if success:
                    prd_data['final_prd_output'] = mock_content
                    prd_data['final_prd_method_used'] = method
                    prd_data['final_prd_doc_id'] = doc_id
                    st.success("Mock final PRD loaded!")
                    # Move to next workflow step or mark complete
                    st.session_state.current_step = 5
                    st.rerun()
                else:
                    st.error("Could not load mock data")
        with col2:
            pass
        st.markdown("---")
    
    # Show instructions
    st.markdown("""
    ### Generate Complete PRD Document
    Synthesize all previous steps into a comprehensive Product Requirements Document:
    - **Complete Integration:** All 7 previous steps combined
    - **Executive Format:** Professional, stakeholder-ready document
    - **Actionable Content:** Clear next steps and implementation guidance
    - **Quality Review:** Comprehensive and ready for approval
    """)
    
    # Show summary of all completed steps
    st.markdown("### 📋 PRD Components Summary:")
    prd_steps = [
        ('executive_summary_output', 'A. Executive Summary'),
        ('problem_statement_output', 'B. Problem Statement'),
        ('goals_and_success_output', 'C. Goals and Success Metrics'),
        ('roles_and_responsibilities_output', 'D. Roles and Responsibilities'),
        ('constraints_and_assumptions_output', 'E. Constraints and Assumptions'),
        ('evaluation_criteria_output', 'F. Evaluation Criteria'),
        ('risk_and_mitigations_output', 'G. Risk and Mitigations')
    ]
    
    completed_steps = []
    for step_key, step_name in prd_steps:
        if step_key in prd_data:
            completed_steps.append(f"✅ {step_name}")
        else:
            completed_steps.append(f"❌ {step_name}")
    
    for step in completed_steps:
        st.markdown(f"- {step}")
    
    # Check if all previous steps are completed
    all_completed = all(step_key in prd_data for step_key, _ in prd_steps)
    
    if not all_completed:
        st.warning("⚠️ Please complete all previous PRD steps before generating the final document.")
        return
    
    # Prepare context for AI generation - foundational context + all PRD components for final document
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    client_data = st.session_state.session_data.get('client_conversation_data', {})
    model_data = st.session_state.session_data.get('model_deliverable_data', {})
    
    context_data = {
        'topic_research': topic_data.get('research_output', ''),
        'model_deliverable': model_data.get('deliverable_output', ''),
        'client_information': client_data.get('info_output', ''),
        'executive_summary': prd_data.get('executive_summary_output', ''),
        'problem_statement': prd_data.get('problem_statement_output', ''),
        'goals_and_success': prd_data.get('goals_and_success_output', ''),
        'roles_and_responsibilities': prd_data.get('roles_and_responsibilities_output', ''),
        'constraints_and_assumptions': prd_data.get('constraints_and_assumptions_output', ''),
        'evaluation_criteria': prd_data.get('evaluation_criteria_output', ''),
        'risk_and_mitigations': prd_data.get('risk_and_mitigations_output', '')
    }
    
    # Generate final PRD using template
    st.markdown("---")
    
    # Use the consistent input interface pattern
    success, prd_content, method_used, doc_id = render_research_input_options(
        topic,
        st.session_state.session_folder_id,
        st.session_state.session_id,
        'final_prd',
        'prd_generator',
        context_data
    )
    
    if success and prd_content:
        # Handle the PRD content and fill template based on the method
        if method_used == 'pasted_content':
            # User pasted PRD content - try to parse as JSON or use session data
            try:
                if prd_content.strip().startswith('{'):
                    # Content looks like JSON
                    prd_json = json.loads(prd_content)
                else:
                    # Content is text - use session data and add pasted content as context
                    prd_json = create_prd_json_from_session_data(prd_data, topic, context_data)
                    prd_json['Executive_Summary']['Executive_Summary'] = {'Context_and_Identity': [prd_content]}
            except json.JSONDecodeError:
                # If JSON parsing fails, use session data
                prd_json = create_prd_json_from_session_data(prd_data, topic, context_data)
                prd_json['Executive_Summary']['Executive_Summary'] = {'Context_and_Identity': [prd_content]}
        
        elif method_used.startswith('pdf_upload'):
            # User uploaded PDF - use PDF content to enhance session data  
            prd_json = create_prd_json_from_session_data(prd_data, topic, context_data)
            prd_json['Executive_Summary']['Executive_Summary'] = {'Context_and_Identity': [prd_content]}
        
        elif method_used.startswith('ai_generated'):
            # AI generated content - should be complete PRD, use as-is
            try:
                if prd_content.strip().startswith('{'):
                    # AI content is JSON - parse and normalize the structure
                    ai_json = json.loads(prd_content)
                    # Convert AI JSON structure to our expected format
                    prd_json = {
                        "title": ai_json.get("Document_Title", f"PRD - {topic}"),
                        "Executive_Summary": ai_json.get("Executive_Summary", {}),
                        "Problem_Statement": ai_json.get("Problem_Statement", {}),
                        "Goals_and_Success_Metrics": ai_json.get("Goals_and_Success_Metrics", {}),
                        "Roles_and_Responsibilities": ai_json.get("Roles_and_Responsibilities", {}),
                        "Constraints_and_Assumptions": ai_json.get("Constraints_and_Assumptions", {}),
                        "Evaluation_Criteria": ai_json.get("Evaluation_Criteria", {}),
                        "Risks_and_Mitigations": ai_json.get("Risks_and_Mitigations", {})
                    }
                else:
                    # AI content is text - create basic structure
                    prd_json = {
                        "title": f"PRD - {topic}",
                        "Executive_Summary": {
                            "Topic": topic,
                            "Executive_Summary": {"Context_and_Identity": [prd_content]}
                        }
                    }
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as executive summary content
                prd_json = {
                    "title": f"PRD - {topic}",
                    "Executive_Summary": {
                        "Topic": topic,
                        "Executive_Summary": {"Context_and_Identity": [prd_content]}
                    }
                }
        
        else:
            # Fallback - use session data
            prd_json = create_prd_json_from_session_data(prd_data, topic, context_data)
        
        # Now generate the final PRD from template
        with st.spinner("Creating PRD from template..."):
            final_doc_id = generate_prd_from_template(prd_json, topic, st.session_state.session_folder_id)
            
            if final_doc_id:
                # Clean up temporary document if it was created by input handler
                if doc_id and doc_id != final_doc_id:
                    try:
                        from utils.google_drive_manager import get_drive_service
                        drive_service = get_drive_service()
                        if drive_service:
                            drive_service.files().delete(fileId=doc_id).execute()
                    except:
                        pass  # Ignore cleanup errors
                
                # Save final PRD data to session
                prd_data['final_prd_output'] = prd_content
                prd_data['final_prd_method_used'] = f"{method_used}_template"
                prd_data['final_prd_doc_id'] = final_doc_id
                
                st.success("🎉 Complete PRD Generated from Template!")
                st.markdown("### ✅ PRD Generation Complete!")
                st.markdown("Your comprehensive Product Requirements Document has been created from the template and saved.")
                
                # Show document link
                from utils.google_drive_manager import get_document_url
                doc_url = get_document_url(final_doc_id)
                st.markdown(f"📄 [Open PRD Document]({doc_url})")
                
                # Log completion
                log_session_data(
                    st.session_state.session_id,
                    'final_prd_completed',
                    {
                        'topic': topic,
                        'method': f"{method_used}_template",
                        'doc_id': final_doc_id,
                        'content_length': len(prd_content)
                    }
                )
                
                # Move to next step
                st.session_state.current_step = 5
                
            else:
                st.error("❌ Failed to generate PRD from template. Please check your template configuration.")
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to Risk and Mitigations"):
        prd_data['current_substep'] = 'risk_and_mitigations'
        st.rerun()

def create_prd_json_from_session_data(prd_data, topic, context_data):
    """Create PRD JSON structure from session data that matches the expected format"""
    
    def parse_json_or_text(content):
        """Parse content - if it's JSON, use it directly; if text, return as is"""
        if not content:
            return {}
        
        try:
            # Try to parse as JSON first
            if isinstance(content, str) and content.strip().startswith('{'):
                return json.loads(content)
            elif isinstance(content, dict):
                return content
            else:
                # If it's plain text, return as is for now
                return {"content": content}
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, return as text content
            return {"content": content}
    
    # Parse each section's output data
    exec_summary_data = parse_json_or_text(prd_data.get('executive_summary_output', ''))
    problem_data = parse_json_or_text(prd_data.get('problem_statement_output', ''))
    goals_data = parse_json_or_text(prd_data.get('goals_and_success_output', ''))
    roles_data = parse_json_or_text(prd_data.get('roles_and_responsibilities_output', ''))
    constraints_data = parse_json_or_text(prd_data.get('constraints_and_assumptions_output', ''))
    evaluation_data = parse_json_or_text(prd_data.get('evaluation_criteria_output', ''))
    risks_data = parse_json_or_text(prd_data.get('risk_and_mitigations_output', ''))
    
    # Build the complete PRD JSON structure using actual data
    prd_json = {
        "title": f"PRD - {topic}",
        "Executive_Summary": {
            "Topic": topic,
            "Executive_Summary": exec_summary_data.get('Executive_Summary', exec_summary_data)
        },
        "Problem_Statement": {
            "Topic": topic,
            "Problem_Statement": problem_data.get('Problem_Statement', problem_data)
        },
        "Goals_and_Success_Metrics": {
            "Topic": topic,
            "Goals_and_Success_Metrics": goals_data.get('Goals_and_Success_Metrics', goals_data)
        },
        "Roles_and_Responsibilities": {
            "Topic": topic,
            "Roles_and_Responsibilities": roles_data.get('Roles_and_Responsibilities', roles_data)
        },
        "Constraints_and_Assumptions": {
            "Topic": topic,
            "Constraints_and_Assumptions": constraints_data.get('Constraints_and_Assumptions', constraints_data)
        },
        "Evaluation_Criteria": {
            "Topic": topic,
            "Evaluation_Criteria": evaluation_data.get('Evaluation_Criteria', evaluation_data)
        },
        "Risks_and_Mitigations": {
            "Topic": topic,
            "Risks_and_Mitigations": risks_data.get('Risks_and_Mitigations', risks_data)
        }
    }
    
    return prd_json

def create_prd_json_from_ai_content(ai_content, topic, context_data, prd_data):
    """Create PRD JSON structure from AI-generated content and existing session data"""
    
    # Use the existing session data but supplement with AI content where available
    # This creates a more complete JSON structure
    prd_json = create_prd_json_from_session_data(prd_data, topic, context_data)
    
    # If AI content is structured JSON, try to parse and merge it
    try:
        if ai_content.strip().startswith('{') and ai_content.strip().endswith('}'):
            ai_json = json.loads(ai_content)
            # Merge AI-generated structure with session data structure
            # Prioritize AI content where available
            for section, content in ai_json.items():
                if section in prd_json:
                    prd_json[section] = content
        else:
            # AI content is text - use it to enhance the Executive Summary
            prd_json['Executive_Summary']['Executive_Summary']['Context_and_Identity'] = [ai_content]
            
    except (json.JSONDecodeError, KeyError):
        # If parsing fails, treat as general content for Executive Summary
        prd_json['Executive_Summary']['Executive_Summary']['Context_and_Identity'] = [ai_content]
    
    return prd_json

def generate_prd_from_template(prd_json, topic, folder_id):
    """Generate PRD document from template using the structured JSON data"""
    
    if not prd_template:
        st.error("❌ PRD template ID not configured. Please add PRD_TEMPLATE_ID to your secrets.")
        return None
    
    try:
        # Convert JSON to placeholders
        placeholders = format_prd_data_for_template(prd_json, topic)
        
        # Create document title
        doc_title = f"PRD - {topic} - Generated"
        
        # Copy template and fill placeholders
        doc_id = copy_template_and_fill_placeholders(
            prd_template,
            doc_title,
            placeholders,
            folder_id
        )
        
        return doc_id
        
    except Exception as e:
        st.error(f"❌ Error generating PRD from template: {str(e)}")
        print(f"Error in generate_prd_from_template: {e}")
        return None