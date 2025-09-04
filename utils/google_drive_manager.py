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
