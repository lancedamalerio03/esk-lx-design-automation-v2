# config.py
import streamlit as st

# OpenAI API Key
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Prompt Document IDs (Google Docs)
meta_prompt = st.secrets.get("METAPROMPT_ID")

# M1
topic_researcher = st.secrets.get("TOPIC_RESEARCHER_ID")

# M2
client_transcript = st.secrets.get("CLIENT_TRANSCRIPT_ID")
client_information = st.secrets.get("CLIENT_INFO_ID")

# M3
model_deliverable_researcher = st.secrets.get("MODEL_DELIVERABLE_RESEARCHER_ID")
model_deliverable_generation = st.secrets.get("MODEL_DELIVERABLE_GENERATION_ID")

# M4
prd_meta_prompt = st.secrets.get("PRD_META_PROMPT_ID")
prd_executive_summary = st.secrets.get("PRD_EXECUTIVE_SUMMARY_ID")
prd_problem_statement = st.secrets.get("PRD_PROBLEM_STATEMENT_ID")
prd_goals_and_success_metrics = st.secrets.get("PRD_GOALS_AND_SUCCESS_METRICS_ID")
prd_roles_and_responsibilities = st.secrets.get("PRD_ROLES_AND_RESPONSIBILITIES_ID")
prd_constraints_and_assumptions = st.secrets.get("PRD_CONSTRAINTS_AND_ASSUMPTIONS_ID")
prd_evaluation_criteria = st.secrets.get("PRD_EVALUATION_CRITERIA_ID")
prd_risk_and_mitigations = st.secrets.get("PRD_RISK_AND_MITIGATIONS_ID")    
prd_generator = st.secrets.get("PRD_GENERATOR_ID")  

# Mock Document IDs for testing (Google Docs)
mock_topic = st.secrets.get("MOCK_TOPIC_ID")
mock_topic_research = st.secrets.get("MOCK_TOPIC_RESEARCH_ID")
mock_client_transcript = st.secrets.get("MOCK_CLIENT_TRANSCRIPT_ID")
mock_client_information = st.secrets.get("MOCK_CLIENT_INFO_ID")
mock_model_deliverable_research = st.secrets.get("MOCK_MODEL_RESEARCH_ID")
mock_model_deliverable = st.secrets.get("MOCK_MODEL_DELIVERABLE_ID")
mock_prd = st.secrets.get("MOCK_PRD_ID")

# Output Folder
lx_design_folder = st.secrets.get("OUTPUTS_FOLDER_URL")
last_created_folder_name = st.secrets.get("LAST_CREATED_FOLDER_NAME", "LAST CREATED")

# Google Sheets Data Logger
lx_design_logger_sheet = st.secrets.get("LOGGING_SHEET_ID")

# Google Service Account
google_type = st.secrets["GOOGLE_TYPE"]
google_project_id = st.secrets["GOOGLE_PROJECT_ID"]
google_private_key_id = st.secrets["GOOGLE_PRIVATE_KEY_ID"]
google_private_key = st.secrets["GOOGLE_PRIVATE_KEY"]
google_client_email = st.secrets["GOOGLE_CLIENT_EMAIL"]
google_client_id = st.secrets["GOOGLE_CLIENT_ID"]
google_auth_uri = st.secrets["GOOGLE_AUTH_URI"]
google_token_uri = st.secrets["GOOGLE_TOKEN_URI"]
google_auth_provider_x509_cert_url = st.secrets["GOOGLE_AUTH_PROVIDER_X509_CERT_URL"]
google_client_x509_cert_url = st.secrets["GOOGLE_CLIENT_X509_CERT_URL"]
google_universe_domain = st.secrets["GOOGLE_UNIVERSE_DOMAIN"]   

# Google OAuth Configuration
google_auth_client_id = st.secrets["GOOGLE_AUTH_CLIENT_ID"]
google_auth_project_id = st.secrets["GOOGLE_AUTH_PROJECT_ID"]
google_auth_client_secret = st.secrets["GOOGLE_AUTH_CLIENT_SECRET"]
google_auth_redirect_uri = st.secrets["GOOGLE_AUTH_REDIRECT_URI"]
google_auth_js_origin = st.secrets["GOOGLE_AUTH_JS_ORIGIN"]

# Redirect URIs and JS Origins
redirect_uris = [
    "https://esk-lx-design-generator.streamlit.app",
    "http://localhost:8501",
    "http://localhost:8502"
]
js_origins = [
    "https://esk-lx-design-generator.streamlit.app",
    "http://localhost:8501",
    "http://localhost:8502"
]

