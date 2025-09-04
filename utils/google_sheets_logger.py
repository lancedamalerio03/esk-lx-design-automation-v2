from .google_auth import get_sheets_service
import datetime
import streamlit as st

def log_session_data(session_id, step, data, sheet_id=None):
    """Log session data to Google Sheets"""
    sheets_service = get_sheets_service()
    if not sheets_service:
        return False
    
    # Use default sheet ID from config if not provided
    if not sheet_id:
        from keys.config import lx_design_logger_sheet
        sheet_id = lx_design_logger_sheet
    
    try:
        # Prepare the row data
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_email = st.session_state.get('credentials', {}).get('id_token', {}).get('email', 'Unknown')
        
        row_data = [
            timestamp,
            session_id,
            user_email,
            step,
            str(data)  # Convert data to string for logging
        ]
        
        # Append to the sheet
        range_name = 'Sheet1!A:E'  # Adjust range as needed
        values = [row_data]
        body = {
            'values': values
        }
        
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"Error logging to sheets: {e}")
        return False

def create_session_log_sheet(session_id):
    """Create a new Google Sheet for session logging"""
    sheets_service = get_sheets_service()
    if not sheets_service:
        return None
    
    try:
        spreadsheet = {
            'properties': {
                'title': f'LX Design Session Log - {session_id}'
            }
        }
        
        result = sheets_service.spreadsheets().create(body=spreadsheet).execute()
        sheet_id = result['spreadsheetId']
        
        # Add headers
        headers = [
            ['Timestamp', 'Session ID', 'User Email', 'Step', 'Data']
        ]
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Sheet1!A1:E1',
            valueInputOption='RAW',
            body={'values': headers}
        ).execute()
        
        return sheet_id
        
    except Exception as e:
        print(f"Error creating log sheet: {e}")
        return None

def get_session_logs(session_id, sheet_id):
    """Retrieve logs for a specific session"""
    sheets_service = get_sheets_service()
    if not sheets_service:
        return []
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A:E'
        ).execute()
        
        values = result.get('values', [])
        
        # Filter for the specific session
        session_logs = []
        for row in values[1:]:  # Skip header row
            if len(row) >= 2 and row[1] == session_id:
                session_logs.append({
                    'timestamp': row[0] if len(row) > 0 else '',
                    'session_id': row[1] if len(row) > 1 else '',
                    'user_email': row[2] if len(row) > 2 else '',
                    'step': row[3] if len(row) > 3 else '',
                    'data': row[4] if len(row) > 4 else ''
                })
        
        return session_logs
        
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return []