import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from keys.config import (
    google_auth_client_id,
    google_auth_client_secret,
    google_auth_redirect_uri
)

# OAuth Configuration
GOOGLE_CLIENT_ID = google_auth_client_id
GOOGLE_CLIENT_SECRET = google_auth_client_secret
REDIRECT_URI = google_auth_redirect_uri

SCOPES = [
    'openid',  # Required when using userinfo scopes
    'https://www.googleapis.com/auth/userinfo.email',  # For getting user email
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

def create_oauth_flow():
    """Create OAuth flow for Google authentication."""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow

def authenticate_user():
    """Handle Google OAuth authentication."""
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None
    
    if st.session_state.credentials is None:
        # Check if we have an authorization code in the URL
        query_params = st.query_params
        
        if 'code' in query_params:
            # Exchange authorization code for credentials
            try:
                flow = create_oauth_flow()
                flow.fetch_token(code=query_params['code'])
                st.session_state.credentials = flow.credentials
                st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {str(e)}")
                return False
        else:
            # Show login button
            st.title("🎯 LX Design Automation v2")
            st.write("Please authenticate with Google to continue.")
            
            if st.button("Login with Google", type="primary"):
                flow = create_oauth_flow()
                auth_url, _ = flow.authorization_url(prompt='consent')
                st.write(f"Please visit this URL to authorize the application: {auth_url}")
                st.write("After authorization, you'll be redirected back to this app.")
            return False
    
    # Check if credentials are valid
    if st.session_state.credentials.expired:
        try:
            st.session_state.credentials.refresh(Request())
        except Exception as e:
            st.error(f"Failed to refresh credentials: {str(e)}")
            st.session_state.credentials = None
            st.rerun()
            return False
    
    return True

def get_user_credentials():
    """Get the user's credentials from session state."""
    return st.session_state.get('credentials', None)

def get_drive_service():
    """Get authenticated Google Drive service."""
    credentials = get_user_credentials()
    if credentials:
        return build('drive', 'v3', credentials=credentials)
    return None

def get_docs_service():
    """Get authenticated Google Docs service."""
    credentials = get_user_credentials()
    if credentials:
        return build('docs', 'v1', credentials=credentials)
    return None

def get_user_email():
    """Get the authenticated user's email address from OAuth2 userinfo endpoint.

    This uses the userinfo endpoint instead of People API, so no additional API needs to be enabled.
    """
    if 'user_email' not in st.session_state:
        try:
            credentials = get_user_credentials()
            if credentials:
                # Use OAuth2 userinfo endpoint (no People API needed)
                import requests
                headers = {'Authorization': f'Bearer {credentials.token}'}
                response = requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    user_info = response.json()
                    st.session_state.user_email = user_info.get('email', 'unknown')
                    print(f"Successfully retrieved user email: {st.session_state.user_email}")
                else:
                    print(f"Failed to get user info: {response.status_code}")
                    st.session_state.user_email = 'unknown'
            else:
                st.session_state.user_email = 'unknown'
        except Exception as e:
            print(f"Error getting user email: {e}")
            st.session_state.user_email = 'unknown'

    return st.session_state.user_email

def get_sheets_service():
    """Get authenticated Google Sheets service."""
    credentials = get_user_credentials()
    if credentials:
        return build('sheets', 'v4', credentials=credentials)
    return None