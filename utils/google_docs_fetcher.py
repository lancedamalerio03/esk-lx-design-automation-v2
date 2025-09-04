from .google_auth import get_docs_service
from keys.config import (
    meta_prompt, topic_researcher, client_transcript, client_information,
    model_deliverable_researcher, model_deliverable_generation, 
    prd_meta_prompt, prd_executive_summary, prd_problem_statement, prd_goals_and_success_metrics,
    prd_roles_and_responsibilities, prd_constraints_and_assumptions, prd_evaluation_criteria,
    prd_risk_and_mitigations, prd_generator,
    mock_topic, mock_topic_research, mock_client_transcript, mock_client_information,
    mock_model_deliverable_research, mock_model_deliverable, mock_prd
)

def get_document_content(document_id):
    """Fetch content from a Google Doc"""
    docs_service = get_docs_service()
    if not docs_service:
        return None
    
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        content = ""
        
        # Extract text content from the document
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        content += text_run['textRun'].get('content', '')
        
        return content.strip()
        
    except Exception as e:
        print(f"Error fetching document {document_id}: {e}")
        return None

def get_prompt_content(prompt_type):
    """Get prompt content based on prompt type"""
    prompt_map = {
        'meta_prompt': meta_prompt,
        'topic_researcher': topic_researcher,
        'client_transcript': client_transcript,
        'client_information': client_information,
        'model_deliverable_researcher': model_deliverable_researcher,
        'model_deliverable_generation': model_deliverable_generation,
        'prd_meta_prompt': prd_meta_prompt,
        'prd_executive_summary': prd_executive_summary,
        'prd_problem_statement': prd_problem_statement,
        'prd_goals_and_success_metrics': prd_goals_and_success_metrics,
        'prd_roles_and_responsibilities': prd_roles_and_responsibilities,
        'prd_constraints_and_assumptions': prd_constraints_and_assumptions,
        'prd_evaluation_criteria': prd_evaluation_criteria,
        'prd_risk_and_mitigations': prd_risk_and_mitigations,
        'prd_generator': prd_generator
    }
    
    document_id = prompt_map.get(prompt_type)
    if not document_id:
        return f"Prompt type '{prompt_type}' not found"
    
    return get_document_content(document_id)

def get_mock_content(mock_type):
    """Get mock data content based on mock type"""
    mock_map = {
        'topic': mock_topic,
        'topic_research': mock_topic_research,
        'client_transcript': mock_client_transcript,
        'client_information': mock_client_information,
        'model_deliverable_research': mock_model_deliverable_research,
        'model_deliverable': mock_model_deliverable,
        'prd': mock_prd
    }
    
    document_id = mock_map.get(mock_type)
    if not document_id:
        return f"Mock type '{mock_type}' not found"
    
    return get_document_content(document_id)

def update_document_content(document_id, new_content):
    """Update the content of a Google Doc"""
    docs_service = get_docs_service()
    if not docs_service:
        return False
    
    try:
        # First, get the current document to find the end index
        document = docs_service.documents().get(documentId=document_id).execute()
        
        # Clear existing content and insert new content
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': len(document.get('body', {}).get('content', [{}])[0].get('paragraph', {}).get('elements', [{}])[0].get('textRun', {}).get('content', '')) + 1
                    }
                }
            },
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': new_content
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"Error updating document {document_id}: {e}")
        return False