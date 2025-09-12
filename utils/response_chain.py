import streamlit as st

def get_previous_response_id():
    """Get the current response ID for chaining"""
    return st.session_state.response_chain.get('current_response_id')

def update_response_chain(step_name, response_id):
    """Update the response chain with new response ID"""
    if response_id:
        st.session_state.response_chain['current_response_id'] = response_id
        st.session_state.response_chain['step_history'][step_name] = response_id

def reset_response_chain():
    """Reset response chain for new session"""
    st.session_state.response_chain = {
        'current_response_id': None,
        'step_history': {},
        'manual_inputs': {}
    }

def store_manual_input(step_name, content, method='manual'):
    """Store manual input content for later AI steps to use as context"""
    st.session_state.response_chain['manual_inputs'][step_name] = {
        'content': content,
        'method': method
    }

def get_manual_context_for_ai():
    """Get manual inputs to include as context for AI generation"""
    manual_inputs = st.session_state.response_chain.get('manual_inputs', {})
    if not manual_inputs:
        return {}
    
    context = {}
    for step_name, data in manual_inputs.items():
        # Format step name for context
        context_key = f"manual_{step_name}"
        context[context_key] = f"User provided {data['method']}: {data['content']}"
    
    return context