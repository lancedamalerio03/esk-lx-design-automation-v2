from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime
import streamlit as st
from keys.config import (
    google_type, google_project_id, google_private_key_id, google_private_key,
    google_client_email, google_client_id, google_auth_uri, google_token_uri,
    google_auth_provider_x509_cert_url, google_client_x509_cert_url, google_universe_domain, lx_design_logger_sheet
)

def get_service_account_sheets_service():
    """Get Google Sheets service using service account credentials"""
    try:
        # Build service account info from config - properly handle private key
        service_account_info = {
            "type": google_type,
            "project_id": google_project_id,
            "private_key_id": google_private_key_id,
            "private_key": google_private_key.replace('\\n', '\n') if google_private_key else "",
            "client_email": google_client_email,
            "client_id": google_client_id,
            "auth_uri": google_auth_uri,
            "token_uri": google_token_uri,
            "auth_provider_x509_cert_url": google_auth_provider_x509_cert_url,
            "client_x509_cert_url": google_client_x509_cert_url,
            "universe_domain": google_universe_domain
        }
        
        print(f"Service account email: {google_client_email}")
        print(f"Private key starts with: {google_private_key[:50] if google_private_key else 'None'}...")
        
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        return build('sheets', 'v4', credentials=credentials)
        
    except Exception as e:
        print(f"Failed to initialize sheets service: {e}")
        return None

def get_user_email():
    """Get user identifier for logging"""
    return google_client_email

def ensure_sheets_exist(sheet_id):
    """Ensure Session_Logs and Detailed_Logs tabs exist"""
    sheets_service = get_service_account_sheets_service()
    if not sheets_service:
        return False
    
    try:
        # Get existing sheets
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        sheets_to_create = []
        if 'Session_Logs' not in existing_sheets:
            sheets_to_create.append({
                'addSheet': {
                    'properties': {
                        'title': 'Session_Logs'
                    }
                }
            })
        
        if 'Detailed_Logs' not in existing_sheets:
            sheets_to_create.append({
                'addSheet': {
                    'properties': {
                        'title': 'Detailed_Logs'
                    }
                }
            })
        
        # Create missing sheets
        if sheets_to_create:
            # print(f"Creating sheets: {[req['addSheet']['properties']['title'] for req in sheets_to_create]}")
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': sheets_to_create}
            ).execute()
        
        # Add headers if needed
        if 'Session_Logs' not in existing_sheets:
            session_headers = [['Session_ID', 'Timestamp', 'User_Path', 'Current_Step', 'Status', 'API_Calls', 'Total_Tokens', 'Created_At', 'Completed_At']]
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Session_Logs!A1:I1',
                valueInputOption='RAW',
                body={'values': session_headers}
            ).execute()
            # print("Added Session_Logs headers")
        
        if 'Detailed_Logs' not in existing_sheets:
            detailed_headers = [['Session_ID', 'Doc_ID', 'Module', 'Step', 'Content', 'AI_Model', 'Input_Tokens', 'Output_Tokens', 'Tokens_Used', 'Cost_USD', 'Content_Length', 'Timestamp']]
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Detailed_Logs!A1:L1',
                valueInputOption='RAW',
                body={'values': detailed_headers}
            ).execute()
            # print("Added Detailed_Logs headers")
        
        return True
        
    except Exception as e:
        # print(f"Error ensuring sheets exist: {e}")
        return False

def log_session_update(session_id, user_path, current_step, status, api_calls=0, total_tokens=0, completed_at=None):
    """Log session updates to Session_Logs tab"""
    sheets_service = get_service_account_sheets_service()
    if not sheets_service:
        print("No sheets service available for session update")
        return False
    
    # Use default sheet ID from config
    sheet_id = lx_design_logger_sheet
    
    print(f"Sheet ID from config: {sheet_id}")
    
    if not sheet_id:
        print("No LOGGING_SHEET_ID configured")
        return False
    
    # print(f"Logging session update: {session_id}, {current_step}, {status} to sheet {sheet_id}")
    
    # Ensure sheets exist
    if not ensure_sheets_exist(sheet_id):
        print("Failed to ensure sheets exist")
        return False
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        created_at = st.session_state.get('session_created_at', timestamp)
        
        # Session_Logs columns: Session_ID, Timestamp, User_Path, Current_Step, Status, API_Calls, Total_Tokens, Created_At, Completed_At
        row_data = [
            session_id,
            timestamp,
            user_path,
            current_step,
            status,
            api_calls,
            total_tokens,
            created_at,
            completed_at or ""
        ]
        
        # First check if session exists, if so update, otherwise create new row
        existing_row = find_session_row(sheet_id, session_id)
        
        if existing_row:
            # Update existing row
            range_name = f'Session_Logs!A{existing_row}:I{existing_row}'
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
        else:
            # Insert new row at top (row 2, after header)
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={
                    'requests': [{
                        'insertDimension': {
                            'range': {
                                'sheetId': get_sheet_id_by_name(sheets_service, sheet_id, 'Session_Logs'),
                                'dimension': 'ROWS',
                                'startIndex': 1,
                                'endIndex': 2
                            }
                        }
                    }]
                }
            ).execute()
            
            # Add data to the newly inserted row
            range_name = 'Session_Logs!A2:I2'
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
        
        # print(f"Session update logged successfully to row {existing_row if existing_row else 'new'}")
        return True
        
    except Exception as e:
        # print(f"Error logging session update: {e}")
        return False

def log_detailed_data(session_id, doc_id, module, step, content, ai_model, input_tokens, output_tokens, tokens_used, cost_usd, content_length):
    """Log detailed data to Detailed_Logs tab"""
    sheets_service = get_service_account_sheets_service()
    if not sheets_service:
        # print("No sheets service available for detailed logging")
        return False
    
    # Use default sheet ID from config
    sheet_id = lx_design_logger_sheet
    
    if not sheet_id:
        # print("No LOGGING_SHEET_ID configured for detailed logging")
        return False
    
    # print(f"Logging detailed data: {session_id}, {module}, {step}, tokens: {tokens_used}")
    
    # Ensure sheets exist
    if not ensure_sheets_exist(sheet_id):
        # print("Failed to ensure sheets exist for detailed logging")
        return False
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Detailed_Logs columns: Session_ID, Doc_ID, Module, Step, Content, AI_Model, Input_Tokens, Output_Tokens, Tokens_Used, Cost_USD, Content_Length, Timestamp
        row_data = [
            session_id,
            doc_id or "",
            module,
            step,
            content,  # Store full content (no truncation)
            ai_model,
            input_tokens,
            output_tokens,
            tokens_used,
            cost_usd,
            content_length,
            timestamp
        ]
        
        # Insert new row at top (row 2, after header)
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={
                'requests': [{
                    'insertDimension': {
                        'range': {
                            'sheetId': get_sheet_id_by_name(sheets_service, sheet_id, 'Detailed_Logs'),
                            'dimension': 'ROWS',
                            'startIndex': 1,
                            'endIndex': 2
                        }
                    }
                }]
            }
        ).execute()
        
        # Add data to the newly inserted row
        range_name = 'Detailed_Logs!A2:L2'
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': [row_data]}
        ).execute()
        
        # print(f"Detailed data logged successfully")
        return True
        
    except Exception as e:
        # print(f"Error logging detailed data: {e}")
        return False

def get_sheet_id_by_name(sheets_service, spreadsheet_id, sheet_name):
    """Get the sheet ID (gid) for a given sheet name"""
    try:
        spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        return 0  # Default to first sheet if not found
    except:
        return 0

def find_session_row(sheet_id, session_id):
    """Find the row number of an existing session in Session_Logs"""
    sheets_service = get_service_account_sheets_service()
    if not sheets_service:
        return None
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Session_Logs!A:A'
        ).execute()
        
        values = result.get('values', [])
        for i, row in enumerate(values):
            if row and len(row) > 0 and row[0] == session_id:
                return i + 1  # Return 1-based row number
        
        return None
        
    except Exception as e:
        # print(f"Error finding session row: {e}")
        return None

# Legacy function for compatibility - now wraps the new session logging
def log_session_data(session_id, step, data, sheet_id=None):
    """Legacy function - now logs to Detailed_Logs"""
    return log_detailed_data(
        session_id=session_id,
        doc_id="",
        module="legacy",
        step=step,
        content=str(data),
        ai_model="unknown",
        input_tokens=0,
        output_tokens=0,
        tokens_used=0,
        cost_usd=0.0,
        content_length=len(str(data))
    )

def create_session_log_sheet(session_id):
    """Initialize session in the logging system"""
    # Store session creation time
    if 'session_created_at' not in st.session_state:
        st.session_state.session_created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log initial session creation  
    user_path = get_user_email()
    
    result = log_session_update(
        session_id=session_id,
        user_path=user_path,
        current_step="1",
        status="started",
        api_calls=0,
        total_tokens=0
    )
    
    return True  # Return success since we're using the main logger sheet

def get_session_logs(session_id):
    """Retrieve logs for a specific session from both tabs"""
    sheets_service = get_service_account_sheets_service()
    if not sheets_service:
        return {'session_logs': [], 'detailed_logs': []}
    
    # Use default sheet ID from config
    sheet_id = lx_design_logger_sheet
    
    try:
        # Get session logs
        session_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Session_Logs!A:I'
        ).execute()
        
        session_values = session_result.get('values', [])
        session_logs = []
        
        for row in session_values[1:]:  # Skip header
            if row and len(row) > 0 and row[0] == session_id:
                session_logs.append({
                    'session_id': row[0] if len(row) > 0 else '',
                    'timestamp': row[1] if len(row) > 1 else '',
                    'user_path': row[2] if len(row) > 2 else '',
                    'current_step': row[3] if len(row) > 3 else '',
                    'status': row[4] if len(row) > 4 else '',
                    'api_calls': row[5] if len(row) > 5 else 0,
                    'total_tokens': row[6] if len(row) > 6 else 0,
                    'created_at': row[7] if len(row) > 7 else '',
                    'completed_at': row[8] if len(row) > 8 else ''
                })
        
        # Get detailed logs
        detailed_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Detailed_Logs!A:L'
        ).execute()
        
        detailed_values = detailed_result.get('values', [])
        detailed_logs = []
        
        for row in detailed_values[1:]:  # Skip header
            if row and len(row) > 0 and row[0] == session_id:
                detailed_logs.append({
                    'session_id': row[0] if len(row) > 0 else '',
                    'doc_id': row[1] if len(row) > 1 else '',
                    'module': row[2] if len(row) > 2 else '',
                    'step': row[3] if len(row) > 3 else '',
                    'content': row[4] if len(row) > 4 else '',
                    'ai_model': row[5] if len(row) > 5 else '',
                    'input_tokens': row[6] if len(row) > 6 else 0,
                    'output_tokens': row[7] if len(row) > 7 else 0,
                    'tokens_used': row[8] if len(row) > 8 else 0,
                    'cost_usd': row[9] if len(row) > 9 else 0.0,
                    'content_length': row[10] if len(row) > 10 else 0,
                    'timestamp': row[11] if len(row) > 11 else ''
                })
        
        return {
            'session_logs': session_logs,
            'detailed_logs': detailed_logs
        }
        
    except Exception as e:
        # print(f"Error retrieving logs: {e}")
        return {'session_logs': [], 'detailed_logs': []}