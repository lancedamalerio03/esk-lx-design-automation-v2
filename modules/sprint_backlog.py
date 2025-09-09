import streamlit as st

def sprint_backlog_module():
    """Sprint Backlog Module - Step 5 of the workflow (Coming Soon)"""
    
    st.markdown("## 🚀 Step 5: Sprint Backlog Generation")
    
    # Show context from previous steps
    topic_data = st.session_state.session_data.get('topic_research_data', {})
    prd_data = st.session_state.session_data.get('prd_data', {})
    topic = topic_data.get('user_topic', 'Unknown topic')
    
    st.info(f"**Topic:** {topic}")
    
    # Show previous final PRD
    final_prd = prd_data.get('final_prd_output', '')
    if final_prd:
        with st.expander("📋 Final PRD (for context)", expanded=False):
            st.text_area("Final PRD content:", value=final_prd[:500] + "...", height=100, disabled=True)
    
    st.markdown("---")
    
    # Coming Soon Content
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h1 style="font-size: 4rem; margin-bottom: 1rem;">🚧</h1>
        <h2 style="color: #666; margin-bottom: 2rem;">Coming Soon</h2>
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
            <h3 style="color: #333; margin-bottom: 1rem;">Sprint Backlog Generation</h3>
            <p style="color: #666; font-size: 1.1rem; line-height: 1.6;">
                Transform your PRD into actionable development items with AI-powered sprint planning:
            </p>
            <ul style="text-align: left; max-width: 500px; margin: 1rem auto; color: #555;">
                <li><strong>Epic Breakdown:</strong> Major features and initiatives</li>
                <li><strong>User Stories:</strong> Detailed requirements from user perspective</li>
                <li><strong>Acceptance Criteria:</strong> Clear success conditions</li>
                <li><strong>Priority Ranking:</strong> Ordered by business value</li>
                <li><strong>Sprint Planning:</strong> Recommended structure and timeline</li>
            </ul>
        </div>
        <p style="color: #999; font-style: italic;">
            This feature is currently under development and will be available in a future release.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show completion status
    if final_prd:
        st.success("✅ Your PRD is complete! The Sprint Backlog feature will transform this into actionable development tasks.")
    else:
        st.info("Complete your PRD first, then return here for sprint backlog generation.")
    
    # Navigation buttons
    st.markdown("---")
    if st.button("⬅️ Back to PRD"):
        st.session_state.current_step = 4
        st.rerun()