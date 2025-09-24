from googleapiclient.discovery import build
from .google_auth import get_drive_service, get_docs_service, get_user_credentials
from keys.config import lx_design_folder, last_created_folder_name
import datetime
import re

def get_outputs_folder_id():
    """Extract folder ID from the OUTPUTS folder URL"""
    if lx_design_folder:
        # Extract folder ID from URL like: https://drive.google.com/drive/u/1/folders/1Uevx7U8clK0HOOjWi2g2upj-M7HPJPga
        match = re.search(r'/folders/([a-zA-Z0-9-_]+)', lx_design_folder)
        if match:
            return match.group(1)
    return None

def get_last_created_folder_id():
    """Find or create the LAST CREATED folder in OUTPUTS"""
    drive_service = get_drive_service()
    if not drive_service:
        return None
        
    outputs_folder_id = get_outputs_folder_id()
    if not outputs_folder_id:
        return None
    
    try:
        # Search for LAST CREATED folder in OUTPUTS folder
        results = drive_service.files().list(
            q=f"name='{last_created_folder_name}' and '{outputs_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        if folders:
            return folders[0]['id']
        
        # Create LAST CREATED folder if it doesn't exist
        folder_metadata = {
            'name': last_created_folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [outputs_folder_id]
        }
        
        folder = drive_service.files().create(body=folder_metadata).execute()
        return folder.get('id')
        
    except Exception as e:
        print(f"Error finding/creating LAST CREATED folder: {e}")
        return None

def clear_last_created_folder():
    """Clear all files from the LAST CREATED folder"""
    drive_service = get_drive_service()
    if not drive_service:
        return False
    
    last_created_folder_id = get_last_created_folder_id()
    if not last_created_folder_id:
        return False
    
    try:
        # Get all files in LAST CREATED folder
        results = drive_service.files().list(
            q=f"'{last_created_folder_id}' in parents and trashed=false",
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        # Delete all files
        for file in files:
            drive_service.files().delete(fileId=file['id']).execute()
        
        return True
        
    except Exception as e:
        print(f"Error clearing LAST CREATED folder: {e}")
        return False

def copy_file_to_last_created(file_id):
    """Copy a file to the LAST CREATED folder (replacing existing files)"""
    drive_service = get_drive_service()
    if not drive_service or not file_id:
        return None
    
    last_created_folder_id = get_last_created_folder_id()
    if not last_created_folder_id:
        return None
    
    try:
        # Get original file info
        original_file = drive_service.files().get(fileId=file_id, fields='name').execute()
        
        # Create copy in LAST CREATED folder
        copied_file = {
            'name': original_file['name'],
            'parents': [last_created_folder_id]
        }
        
        copy_result = drive_service.files().copy(
            fileId=file_id,
            body=copied_file
        ).execute()
        
        return copy_result.get('id')
        
    except Exception as e:
        print(f"Error copying file to LAST CREATED: {e}")
        return None

def list_folders():
    """List folders in user's Google Drive"""
    drive_service = get_drive_service()
    if not drive_service:
        return []
    
    try:
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name, parents)'
        ).execute()
        
        folders = results.get('files', [])
        
        # Add "My Drive" as root option
        folder_options = [{'id': 'root', 'name': 'My Drive (Root)', 'parents': []}]
        
        # Add other folders
        for folder in folders:
            folder_options.append({
                'id': folder['id'],
                'name': folder['name'],
                'parents': folder.get('parents', [])
            })
        
        return folder_options
        
    except Exception as e:
        print(f"Error listing folders: {e}")
        return [{'id': 'root', 'name': 'My Drive (Root)', 'parents': []}]

def create_session_folder(session_id):
    """Create a new folder for the session inside the OUTPUTS folder"""
    drive_service = get_drive_service()
    if not drive_service:
        return None
    
    outputs_folder_id = get_outputs_folder_id()
    if not outputs_folder_id:
        print("Error: OUTPUTS folder ID not found")
        return None
    
    folder_name = f"LX Design Session - {session_id}"
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [outputs_folder_id]
    }
    
    try:
        folder = drive_service.files().create(body=folder_metadata).execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error creating folder: {e}")
        return None

def find_existing_document(title, folder_id=None):
    """Find existing document with the same title in the specified folder"""
    drive_service = get_drive_service()
    if not drive_service:
        return None
    
    try:
        # Get all documents in the folder first, then filter by name
        # This avoids issues with special characters in search queries
        query_parts = [
            "mimeType='application/vnd.google-apps.document'",
            "trashed=false"
        ]
        
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        
        query = " and ".join(query_parts)
        
        print(f"DEBUG: Searching in folder with query: {query}")
        print(f"DEBUG: Looking for document titled: '{title}'")
        
        results = drive_service.files().list(
            q=query,
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        print(f"DEBUG: Found {len(files)} total documents in folder")
        
        # Look for exact name match
        for file in files:
            print(f"DEBUG: Comparing '{file['name']}' with '{title}'")
            if file['name'] == title:
                print(f"DEBUG: Found exact match! Returning document ID: {file['id']}")
                return file['id']
        
        print(f"DEBUG: No exact match found for '{title}'")
        return None
        
    except Exception as e:
        print(f"Error searching for existing document: {e}")
        return None

def update_google_doc(document_id, content):
    """Update existing Google Doc with new content"""
    docs_service = get_docs_service()
    if not docs_service:
        return False
    
    try:
        # Get current document to find content length
        document = docs_service.documents().get(documentId=document_id).execute()
        
        # Calculate content length (excluding title)
        content_length = 1
        if 'body' in document and 'content' in document['body']:
            for element in document['body']['content']:
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph'].get('elements', []):
                        if 'textRun' in paragraph_element:
                            content_length += len(paragraph_element['textRun'].get('content', ''))
        
        # Clear existing content and add new content
        requests = [
            {
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': content_length
                    }
                }
            },
            {
                'insertText': {
                    'location': {
                        'index': 1,
                    },
                    'text': content
                }
            }
        ]
        
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"Error updating document: {e}")
        return False

def create_or_update_google_doc(title, content, folder_id=None):
    """Create a new Google Doc or update existing one with the same title"""
    docs_service = get_docs_service()
    drive_service = get_drive_service()
    
    if not docs_service or not drive_service:
        return None
    
    try:
        # First, check if document already exists
        existing_doc_id = find_existing_document(title, folder_id)
        
        if existing_doc_id:
            # Update existing document
            if update_google_doc(existing_doc_id, content):
                # Copy updated document to LAST CREATED folder
                copy_file_to_last_created(existing_doc_id)
                return existing_doc_id
            else:
                # If update failed, fall back to creating new document
                pass
        
        # Create new document
        document = {
            'title': title
        }
        doc = docs_service.documents().create(body=document).execute()
        document_id = doc.get('documentId')
        
        # Add content if provided
        if content:
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]
            docs_service.documents().batchUpdate(
                documentId=document_id, 
                body={'requests': requests}
            ).execute()
        
        # Move to folder if specified
        if folder_id:
            drive_service.files().update(
                fileId=document_id,
                addParents=folder_id,
                removeParents='root'
            ).execute()
        
        # Always copy to LAST CREATED folder
        copy_file_to_last_created(document_id)
        
        return document_id
        
    except Exception as e:
        print(f"Error creating/updating document: {e}")
        return None

def create_google_doc(title, content, folder_id=None):
    """Wrapper function to maintain compatibility - creates or updates document"""
    return create_or_update_google_doc(title, content, folder_id)

def get_document_url(document_id):
    """Get the URL for a Google Doc"""
    return f"https://docs.google.com/document/d/{document_id}/edit"

def get_folder_url(folder_id):
    """Get the URL for a Google Drive folder"""
    return f"https://drive.google.com/drive/folders/{folder_id}"

def copy_template_and_fill_placeholders(template_id, title, placeholders_dict, folder_id=None):
    """Copy a template document and fill placeholders with actual content"""
    print(f"DEBUG: Starting template copy with template_id={template_id}, title={title}, folder_id={folder_id}")
    
    drive_service = get_drive_service()
    docs_service = get_docs_service()
    
    if not drive_service:
        print("ERROR: Could not get drive service")
        return None
    if not docs_service:
        print("ERROR: Could not get docs service")
        return None
    if not template_id:
        print("ERROR: No template_id provided")
        return None
    
    try:
        print(f"DEBUG: Copying template {template_id}...")
        
        # First copy the template
        copied_file = {
            'name': title,
            'parents': [folder_id] if folder_id else ['root']
        }
        
        copy_result = drive_service.files().copy(
            fileId=template_id,
            body=copied_file
        ).execute()
        
        document_id = copy_result.get('id')
        print(f"DEBUG: Template copied successfully, new document_id={document_id}")
        
        if not document_id:
            print("ERROR: Copy operation succeeded but no document_id returned")
            return None
        
        # Now fill the placeholders
        print(f"DEBUG: Filling {len(placeholders_dict)} placeholders...")
        requests = []
        
        for placeholder, content in placeholders_dict.items():
            # Find and replace all instances of the placeholder
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': placeholder,
                        'matchCase': False
                    },
                    'replaceText': content or ''
                }
            })
        
        print(f"DEBUG: Created {len(requests)} replacement requests")
        
        # Execute all replacements in batches (Google Docs has request limits)
        batch_size = 100
        for i in range(0, len(requests), batch_size):
            batch_requests = requests[i:i + batch_size]
            if batch_requests:
                print(f"DEBUG: Executing batch {i//batch_size + 1} with {len(batch_requests)} requests")
                docs_service.documents().batchUpdate(
                    documentId=document_id,
                    body={'requests': batch_requests}
                ).execute()
        
        print("DEBUG: All placeholder replacements completed")
        
        # Table filling functionality removed - using simple placeholder replacement only
        
        # Always copy to LAST CREATED folder
        print("DEBUG: Copying to LAST CREATED folder...")
        copy_file_to_last_created(document_id)
        
        print(f"DEBUG: Template filling completed successfully. Document ID: {document_id}")
        return document_id
        
    except Exception as e:
        print(f"ERROR copying template and filling placeholders: {e}")
        import traceback
        traceback.print_exc()
        return None

def format_prd_data_for_template(prd_data, topic):
    """Convert nested PRD JSON data to template placeholders"""
    placeholders = {}
    
    print(f"DEBUG: PRD data keys: {list(prd_data.keys())}")
    
    # Title
    placeholders['{Title}'] = prd_data.get('title', f'PRD - {topic}')
    
    # Executive Summary - direct array access (matches actual JSON structure)
    exec_summary_array = prd_data.get('Executive_Summary', [])
    print(f"DEBUG: Executive_Summary array length: {len(exec_summary_array) if exec_summary_array else 0}")
    summary_text = format_array_as_text(exec_summary_array)
    print(f"DEBUG: summary_text length: {len(summary_text)}")
    placeholders['{{Executive_Summary}}'] = summary_text
    
    # Problem Statement - direct array access (matches actual JSON structure)
    prob_statement_array = prd_data.get('Problem_Statement', [])
    print(f"DEBUG: Problem_Statement array length: {len(prob_statement_array) if prob_statement_array else 0}")
    problem_text = format_array_as_text(prob_statement_array)
    print(f"DEBUG: problem_text length: {len(problem_text)}")
    placeholders['{{Problem_Statement}}'] = problem_text
    
    # Goals and Success Metrics - match template structure
    goals_metrics = prd_data.get('Goals_and_Success_Metrics', {})
    placeholders['{{Goals_and_Success_Metrics.Clear_Goals}}'] = format_array_as_bullets(goals_metrics.get('Clear_Goals', []))
    placeholders['{{Goals_and_Success_Metrics.Success_Metrics}}'] = format_array_as_bullets(goals_metrics.get('Success_Metrics', []))
    
    # Roles and Responsibilities - match template structure
    roles_resp = prd_data.get('Roles_and_Responsibilities', {})
    
    # Facilitators
    facilitators = roles_resp.get('Facilitator_Team', {}).get('Facilitators', [])
    if facilitators:
        facilitator_table = format_table_rows(facilitators, 'Role', 'Responsibilities')
        # Split into roles and responsibilities for table columns with bullet points
        roles = [f"• {f.get('Role', '')}" for f in facilitators]
        responsibilities = [f"• {f.get('Responsibilities', '')}" for f in facilitators]
        placeholders['{{Facilitators.Role}}'] = '\n\n'.join(roles)
        placeholders['{{Facilitators.Responsibilities}}'] = '\n\n'.join(responsibilities)
    else:
        placeholders['{{Facilitators.Role}}'] = ''
        placeholders['{{Facilitators.Responsibilities}}'] = ''
    
    # Clients  
    clients = roles_resp.get('Client_Team', {}).get('Clients', [])
    if clients:
        # Split into roles and responsibilities for table columns with bullet points
        roles = [f"• {c.get('Role', '')}" for c in clients]
        responsibilities = [f"• {c.get('Responsibilities', '')}" for c in clients]
        placeholders['{{Clients.Role}}'] = '\n\n'.join(roles)
        placeholders['{{Clients.Responsibilities}}'] = '\n\n'.join(responsibilities)
    else:
        placeholders['{{Clients.Role}}'] = ''
        placeholders['{{Clients.Responsibilities}}'] = ''
    
    # Learner Profiles
    learners = roles_resp.get('Learner_Profiles', [])
    if learners:
        placeholders['{{Learner_Profiles.Category}}'] = '\n\n'.join([f"• {l.get('Category', '')}" for l in learners])
        placeholders['{{Learner_Profiles.Background}}'] = '\n\n'.join([f"• {l.get('Background', '')}" for l in learners])
        placeholders['{{Learner_Profiles.User_Stories}}'] = '\n\n'.join([f"• {l.get('User_Stories', '')}" for l in learners])
        placeholders['{{Learner_Profiles.Strengths}}'] = '\n\n'.join([f"• {l.get('Strengths', '')}" for l in learners])
        placeholders['{{Learner_Profiles.Needs}}'] = '\n\n'.join([f"• {l.get('Needs', '')}" for l in learners])
    else:
        placeholders['{{Learner_Profiles.Category}}'] = ''
        placeholders['{{Learner_Profiles.Background}}'] = ''
        placeholders['{{Learner_Profiles.User_Stories}}'] = ''
        placeholders['{{Learner_Profiles.Strengths}}'] = ''
        placeholders['{{Learner_Profiles.Needs}}'] = ''
    
    # Constraints and Assumptions
    const_assump = prd_data.get('Constraints_and_Assumptions', {})
    constraints = const_assump.get('Constraints', [])
    assumptions = const_assump.get('Assumptions', [])
    
    placeholders['{{Constraints_and_Assumptions.Constraints}}'] = format_constraints_assumptions(constraints)
    placeholders['{{Constraints_and_Assumptions.Assumptions}}'] = format_constraints_assumptions(assumptions)
    
    # Evaluation Criteria
    eval_criteria = prd_data.get('Evaluation_Criteria', {})
    def_of_done = eval_criteria.get('Definition_of_Done', {})
    
    placeholders['{{Evaluation_Criteria.Deliverables}}'] = format_array_as_bullets([d.get('Deliverable', '') for d in def_of_done.get('Deliverables', [])])
    placeholders['{{Evaluation_Criteria.Engagement}}'] = format_array_as_bullets([e.get('Requirement', '') for e in def_of_done.get('Engagement', [])])
    placeholders['{{Evaluation_Criteria.Compliance}}'] = format_array_as_bullets([c.get('Requirement', '') for c in def_of_done.get('Compliance', [])])
    placeholders['{{Evaluation_Criteria.Functional_Requirements}}'] = format_array_as_bullets([r.get('Requirement', '') for r in eval_criteria.get('Functional_Requirements', [])])
    placeholders['{{Evaluation_Criteria.Non_Functional_Requirements}}'] = format_array_as_bullets([r.get('Requirement', '') for r in eval_criteria.get('Non_Functional_Requirements', [])])
    placeholders['{{Evaluation_Criteria.Deliverable_Rubric}}'] = format_rubric(eval_criteria.get('Deliverable_Rubric', []))
    placeholders['{{Evaluation_Criteria.Passing_Threshold}}'] = eval_criteria.get('Passing_Threshold', '')
    
    # Risks and Mitigations - match template structure
    risks_mit = prd_data.get('Risks_and_Mitigations', {})
    items = risks_mit.get('Items', [])
    
    # Format for table columns with bullet points
    if items:
        risks = [f"• {item.get('Risk', '')}" for item in items]
        mitigations = [f"• {item.get('Mitigation', '')}" for item in items]
        placeholders['{{List.Risks}}'] = '\n\n'.join(risks)
        placeholders['{{List.Mitigations}}'] = '\n\n'.join(mitigations)
    else:
        placeholders['{{List.Risks}}'] = ''
        placeholders['{{List.Mitigations}}'] = ''
    
    return placeholders


def format_array_as_text(arr):
    """Convert array to paragraph text"""
    if not arr:
        return ''
    return '\n\n'.join(str(item) for item in arr)

def format_array_as_bullets(arr):
    """Convert array to bullet points"""
    if not arr:
        return ''
    return '\n'.join(f'• {item}' for item in arr)

def format_constraints_assumptions(items):
    """Format constraints/assumptions with headlines"""
    if not items:
        return ''
    formatted = []
    for item in items:
        if isinstance(item, dict):
            headline = item.get('Constraint', item.get('Assumption', ''))
            description = item.get('Description', '')
            formatted.append(f'• {headline}: {description}')
        else:
            formatted.append(f'• {item}')
    return '\n'.join(formatted)

def format_table_rows(items, role_key, responsibility_key):
    """Format items as table rows for Google Docs"""
    if not items:
        return ''
    rows = []
    for item in items:
        role = item.get(role_key, '')
        resp = item.get(responsibility_key, '')
        rows.append(f'{role}\t{resp}')
    return '\n'.join(rows)

def format_risks_mitigations_table(items):
    """Format risks and mitigations as table rows"""
    if not items:
        return ''
    risks = []
    mitigations = []
    for item in items:
        risks.append(item.get('Risk', ''))
        mitigations.append(item.get('Mitigation', ''))
    return risks, mitigations

def format_rubric(rubric_items):
    """Format rubric items as bullet points"""
    if not rubric_items:
        return ''
    formatted = []
    for item in rubric_items:
        if isinstance(item, dict):
            criteria = item.get('Criteria', '')
            points = item.get('Points', '')
            description = item.get('Description', '')
            formatted.append(f'• {criteria} ({points}): {description}')
        else:
            formatted.append(f'• {item}')
    return '\n'.join(formatted)


def share_with_user(file_id, email, role='writer'):
    """Share a file or folder with a specific user"""
    drive_service = get_drive_service()
    if not drive_service:
        return False
    
    try:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        drive_service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        return True
    except Exception as e:
        print(f"Error sharing file: {e}")
        return False
