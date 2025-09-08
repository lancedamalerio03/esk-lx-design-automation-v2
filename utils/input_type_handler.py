import streamlit as st
from io import BytesIO
from .google_docs_fetcher import get_prompt_content
from .google_drive_manager import create_google_doc
from .google_sheets_logger import log_session_data
from AI.generate_ai_response import generate_ai_response

def render_research_input_options(topic, session_folder_id, session_id, step_name="research", prompt_type='topic_researcher', context_data=None):
    """
    Render research input options UI and handle the selected method
    Args:
        context_data: Optional dict of context data for AI generation
    Returns: (success, research_content, method_used, doc_id)
    """
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
    
    st.markdown("### ✍️ How would you like to provide the input?")
    st.markdown('<div class="seg-card"><div class="seg-inner">', unsafe_allow_html=True)
    mode = st.radio(
        "Choose a method:",
        options=["Paste text", "Upload a PDF", "Ask AI to help"],
        horizontal=True,
        help="Paste notes, upload a PDF, or ask AI to generate the output for you.",
        label_visibility="visible",
        key=f"research_method_{step_name}"
    )
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Handle different research modes
    if mode == "Paste text":
        return handle_paste_input(topic, session_folder_id, session_id, step_name)
    elif mode == "Upload a PDF":
        return handle_pdf_upload(topic, session_folder_id, session_id, step_name)
    elif mode == "Ask AI to help":
        return handle_ai_generation(topic, session_folder_id, session_id, step_name, prompt_type, context_data)
    
    return False, None, None, None

def handle_paste_input(topic, session_folder_id, session_id, step_name):
    """Handle pasted text input"""
    pasted = st.text_area(
        "Paste your input here:",
        height=300,
        placeholder="Drop in your notes, article excerpts, or a brief you already made…",
        key=f"paste_input_{step_name}"
    )
    
    # Check if paste is currently processing for this step
    paste_processing_key = f"paste_processing_{step_name}"
    is_processing = st.session_state.get(paste_processing_key, False)
    
    # Show button only if not processing
    if not is_processing:
        if st.button("💾 Save Input & Continue", use_container_width=True, key=f"save_paste_{step_name}"):
            content = (pasted or "").strip()
            if not content:
                st.error("Please paste input text first.")
                return False, None, None, None
            
            # Set processing state to hide button
            st.session_state[paste_processing_key] = True
            st.rerun()
    else:
        # Show processing state instead of button
        st.info("💾 Saving content... Please wait.")
        
        with st.spinner("💾 Saving content..."):
            try:
                content = (pasted or "").strip()
                
                # Create Google Doc with the research
                doc_title = f"{step_name.title()} Research - {topic}"
                doc_content = f"# {step_name.title()} Research: {topic}\n\n## Research Method: Pasted Content\n\n{content}"
                
                doc_id = create_google_doc(doc_title, doc_content, session_folder_id)
                
                # Log this step to both legacy and detailed logs
                log_session_data(
                    session_id,
                    f'{step_name}_research_completed',
                    {
                        'topic': topic,
                        'method': 'pasted_content',
                        'doc_id': doc_id,
                        'content_length': len(content)
                    }
                )
                
                # Log detailed data for pasted content
                try:
                    from utils.google_sheets_logger import log_detailed_data
                    
                    # Determine module from step_name
                    module = "unknown"
                    if "topic" in step_name.lower():
                        module = "topic_research"
                    elif "client" in step_name.lower():
                        module = "client_conversation"
                    elif "model" in step_name.lower():
                        module = "model_deliverable"
                    elif "prd" in step_name.lower():
                        module = "prd"
                    
                    log_detailed_data(
                        session_id=session_id,
                        doc_id=doc_id,
                        module=module,
                        step=step_name,
                        content=content,
                        ai_model="plaintext",
                        input_tokens=0,
                        output_tokens=0,
                        tokens_used=0,
                        cost_usd=0.0,
                        content_length=len(content)
                    )
                except Exception as e:
                    print(f"Error logging pasted content details: {e}")
                
                # Clear processing state on success
                st.session_state[paste_processing_key] = False
                st.success("✅ Research saved!")
                return True, content, 'pasted_content', doc_id
                
            except Exception as e:
                # Clear processing state on error
                st.session_state[paste_processing_key] = False
                st.error(f"Error saving content: {str(e)}")
                return False, None, None, None
    
    return False, None, None, None

def handle_pdf_upload(topic, session_folder_id, session_id, step_name):
    """Handle PDF file upload"""
    uploaded_file = st.file_uploader(
        "Upload a PDF with the content:", 
        type=["pdf"],
        key=f"pdf_upload_{step_name}"
    )
    
    if uploaded_file is not None:
        st.success(f"📎 Uploaded: {uploaded_file.name}")
        
        # Check if PDF is currently processing for this step
        pdf_processing_key = f"pdf_processing_{step_name}"
        is_processing = st.session_state.get(pdf_processing_key, False)
        
        # Show button only if not processing
        if not is_processing:
            if st.button("📄 Extract & Save PDF Content", use_container_width=True, key=f"extract_pdf_{step_name}"):
                # Set processing state to hide button
                st.session_state[pdf_processing_key] = True
                st.rerun()
        else:
            # Show processing state instead of button
            st.info("📄 Extracting PDF content... Please wait.")
            
            with st.spinner("📄 Extracting PDF content..."):
                try:
                    extracted_text = extract_pdf_text(uploaded_file)
                    
                    if not extracted_text:
                        # Clear processing state on failure
                        st.session_state[pdf_processing_key] = False
                        st.error("❌ Could not extract any text from this PDF. It may be image-only or protected.")
                        return False, None, None, None
                    
                    # Format the research content
                    pdf_research = (
                        f"# PDF Research: {uploaded_file.name}\n\n"
                        f"**Document Information:**\n"
                        f"- Filename: {uploaded_file.name}\n"
                        f"- Characters: {len(extracted_text):,}\n"
                        f"- Words: {len(extracted_text.split()):,}\n\n"
                        f"**Extracted Content:**\n{extracted_text}\n"
                    )
                    
                    # Create Google Doc with the research
                    doc_title = f"{step_name.title()} Research - {topic} (PDF)"
                    doc_id = create_google_doc(doc_title, pdf_research, session_folder_id)
                    
                    # Log this step to both legacy and detailed logs
                    log_session_data(
                        session_id,
                        f'{step_name}_research_completed',
                        {
                            'topic': topic,
                            'method': 'pdf_upload',
                            'filename': uploaded_file.name,
                            'doc_id': doc_id,
                            'content_length': len(extracted_text)
                        }
                    )
                    
                    # Log detailed data for PDF content
                    try:
                        from utils.google_sheets_logger import log_detailed_data
                        
                        # Determine module from step_name
                        module = "unknown"
                        if "topic" in step_name.lower():
                            module = "topic_research"
                        elif "client" in step_name.lower():
                            module = "client_conversation"
                        elif "model" in step_name.lower():
                            module = "model_deliverable"
                        elif "prd" in step_name.lower():
                            module = "prd"
                        
                        log_detailed_data(
                            session_id=session_id,
                            doc_id=doc_id,
                            module=module,
                            step=step_name,
                            content=pdf_research,
                            ai_model="pdf",
                            input_tokens=0,
                            output_tokens=0,
                            tokens_used=0,
                            cost_usd=0.0,
                            content_length=len(extracted_text)
                        )
                    except Exception as e:
                        print(f"Error logging PDF content details: {e}")
                    
                    # Clear processing state on success
                    st.session_state[pdf_processing_key] = False
                    st.success("✅ PDF research processed and saved!")
                    return True, pdf_research, f'pdf_upload:{uploaded_file.name}', doc_id
                    
                except Exception as e:
                    # Clear processing state on error
                    st.session_state[pdf_processing_key] = False
                    st.error(f"Error processing PDF: {str(e)}")
                    return False, None, None, None
    
    return False, None, None, None

def handle_ai_generation(topic, session_folder_id, session_id, step_name, prompt_type='topic_researcher', context_data=None):
    """Handle AI-generated content"""
    st.markdown("Let AI generate content for your request")
    
    # Check if AI is currently processing for this step
    ai_processing_key = f"ai_processing_{step_name}"
    is_processing = st.session_state.get(ai_processing_key, False)
    
    # Show button only if not processing
    if not is_processing:
        if st.button("🤖 Generate with AI", use_container_width=True, key=f"ai_generate_{step_name}"):
            # Set processing state to hide button
            st.session_state[ai_processing_key] = True
            st.rerun()
    else:
        # Show processing state instead of button
        st.info("🧠 AI is generating content... Please wait.")
        
        with st.spinner("🧠 Generating content..."):
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
                
                # Generate AI response with context data if provided
                if context_data:
                    research = generate_ai_response(combined_prompt, context_data, step_name)
                else:
                    research = generate_ai_response(combined_prompt, {'topic': topic}, step_name)
                
                if research:
                    # Create Google Doc with the research
                    doc_title = f"{step_name.title()} Research - {topic} (AI Generated)"
                    doc_content = f"# AI {step_name.title()} Research: {topic}\n\n## Research Method: AI Generated\n\n{research}"
                    
                    doc_id = create_google_doc(doc_title, doc_content, session_folder_id)
                    
                    # Store doc_id for logging
                    st.session_state.current_doc_id = doc_id
                    
                    # Log this step
                    log_session_data(
                        session_id,
                        f'{step_name}_research_completed',
                        {
                            'topic': topic,
                            'method': 'ai_generated',
                            'prompt_type': prompt_type,
                            'doc_id': doc_id,
                            'content_length': len(research)
                        }
                    )
                    
                    # Clear processing state on success
                    st.session_state[ai_processing_key] = False
                    st.success("✅ AI research generated and saved!")
                    return True, research, f'ai_generated:{prompt_type}', doc_id
                else:
                    # Clear processing state on failure
                    st.session_state[ai_processing_key] = False
                    st.error("Failed to generate AI research. Please try again.")
                    return False, None, None, None
                    
            except Exception as e:
                # Clear processing state on error
                st.session_state[ai_processing_key] = False
                st.error(f"Error generating AI research: {str(e)}")
                return False, None, None, None
    
    return False, None, None, None

def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF file"""
    extracted_text = ""
    
    try:
        import pdfplumber
        uploaded_file.seek(0)
        buffer = BytesIO(uploaded_file.read())
        
        parts = []
        with pdfplumber.open(buffer) as pdf:
            total_pages = len(pdf.pages)
            st.info(f"📊 Processing {total_pages} page(s)…")
            
            for i, page in enumerate(pdf.pages, start=1):
                st.progress(i / max(total_pages, 1), text=f"Processing page {i}/{total_pages}")
                text = (page.extract_text() or "").strip()
                if text:
                    parts.append(text)
        
        extracted_text = "\n\n".join(parts).strip()
        
    except Exception as e:
        st.warning(f"pdfplumber error: {e}")
    
    # Fallback to PyPDF2 if pdfplumber fails
    if not extracted_text:
        try:
            import PyPDF2
            st.info("Trying PyPDF2 fallback…")
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(uploaded_file)
            
            parts = []
            for i, page in enumerate(reader.pages, start=1):
                st.progress(i / len(reader.pages), text=f"Processing page {i}/{len(reader.pages)}")
                text = (page.extract_text() or "").strip()
                if text:
                    parts.append(text)
            
            extracted_text = "\n\n".join(parts).strip()
            
        except Exception as e:
            st.error(f"PDF extraction failed: {e}")
    
    return extracted_text

def load_mock_research(mock_type, topic, session_folder_id, session_id, step_name):
    """Load mock research data for testing"""
    from .google_docs_fetcher import get_mock_content
    
    mock_research = get_mock_content(mock_type)
    if mock_research:
        # Create Google Doc with mock research
        doc_title = f"{step_name.title()} Research - {topic} (Mock Data)"
        doc_content = f"# Mock {step_name.title()} Research: {topic}\n\n## Research Method: Mock Data\n\n{mock_research}"
        
        doc_id = create_google_doc(doc_title, doc_content, session_folder_id)
        
        # Log this step to both legacy and detailed logs
        log_session_data(
            session_id,
            f'{step_name}_research_completed',
            {
                'topic': topic,
                'method': 'mock_data',
                'mock_type': mock_type,
                'doc_id': doc_id,
                'content_length': len(mock_research)
            }
        )
        
        # Log detailed data for mock content
        try:
            from utils.google_sheets_logger import log_detailed_data
            
            # Determine module from step_name
            module = "unknown"
            if "topic" in step_name.lower():
                module = "topic_research"
            elif "client" in step_name.lower():
                module = "client_conversation"
            elif "model" in step_name.lower():
                module = "model_deliverable"
            elif "prd" in step_name.lower():
                module = "prd"
            
            log_detailed_data(
                session_id=session_id,
                doc_id=doc_id,
                module=module,
                step=step_name,
                content=mock_research,
                ai_model="mock_data",
                input_tokens=0,
                output_tokens=0,
                tokens_used=0,
                cost_usd=0.0,
                content_length=len(mock_research)
            )
        except Exception as e:
            print(f"Error logging mock content details: {e}")
        
        return True, mock_research, f'mock_data:{mock_type}', doc_id
    
    return False, None, None, None