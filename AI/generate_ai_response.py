import os
from openai import OpenAI
import streamlit as st
from datetime import datetime

from keys.config import OPENAI_API_KEY


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Token tracking utilities
class TokenTracker:
    """Track token usage and costs throughout the workflow"""
    
    def __init__(self):
        self.usage_log = []
        self.session_totals = {
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0,
            'total_content_length': 0
        }
    
    def log_usage(self, step_name, input_tokens, output_tokens, content_length, model_name="gpt-5"):
        """Log token usage for a specific step"""
        total_tokens = input_tokens + output_tokens
        cost_usd = self.calculate_cost(input_tokens, output_tokens, model_name)
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'step_name': step_name,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens,
            'cost_usd': cost_usd,
            'content_length': content_length,
            'model_name': model_name
        }
        
        self.usage_log.append(entry)
        
        # Update session totals
        self.session_totals['input_tokens'] += input_tokens
        self.session_totals['output_tokens'] += output_tokens
        self.session_totals['total_tokens'] += total_tokens
        self.session_totals['total_cost_usd'] += cost_usd
        self.session_totals['total_content_length'] += content_length
    
    def calculate_cost(self, input_tokens, output_tokens, model_name="gpt-5"):
        """Calculate cost based on token usage and model pricing"""
        # OpenAI pricing per 1M tokens (updated 2025-09-08)
        pricing = {
            "gpt-5-pro":     {"input_per_1m": 15.00, "output_per_1m": 120.00},
            "gpt-5":         {"input_per_1m": 1.25, "output_per_1m": 10.00},
            "gpt-5-mini":    {"input_per_1m": 0.25, "output_per_1m": 2.00},
            "gpt-5-nano":    {"input_per_1m": 0.05, "output_per_1m": 0.40},
            "gpt-4.1":       {"input_per_1m": 2.00, "output_per_1m": 8.00},
            "gpt-4.1-mini":  {"input_per_1m": 0.40, "output_per_1m": 1.60},
            "gpt-4.1-nano":  {"input_per_1m": 0.10, "output_per_1m": 0.40},
            "gpt-4o":        {"input_per_1m": 2.50, "output_per_1m": 10.00},
            "gpt-4o-mini":   {"input_per_1m": 0.15, "output_per_1m": 0.60},
            "o3":            {"input_per_1m": 2.00, "output_per_1m": 8.00},
            "o3-mini":       {"input_per_1m": 0.40, "output_per_1m": 1.60}
        }
        
        model_pricing = pricing.get(model_name, pricing["gpt-5"])
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input_per_1m"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output_per_1m"]
        
        return input_cost + output_cost
    
    def get_session_summary(self):
        """Get summary of token usage for the current session"""
        return {
            **self.session_totals,
            'steps_completed': len(self.usage_log),
            'avg_tokens_per_step': self.session_totals['total_tokens'] / len(self.usage_log) if self.usage_log else 0,
            'avg_cost_per_step': self.session_totals['total_cost_usd'] / len(self.usage_log) if self.usage_log else 0
        }

def get_token_tracker():
    """Get or create token tracker in session state"""
    if 'token_tracker' not in st.session_state:
        st.session_state.token_tracker = TokenTracker()
    return st.session_state.token_tracker

def get_session_token_summary():
    """Get current session token usage summary"""
    tracker = get_token_tracker()
    return tracker.get_session_summary()

def reset_token_tracking():
    """Reset token tracking for new session"""
    if 'token_tracker' in st.session_state:
        st.session_state.token_tracker = TokenTracker()
    
def generate_ai_response(prompt, context, step_name="unknown") -> str:
    try:
        
        # Convert context dict to structured text
        context_str = ""
        if isinstance(context, dict):
            for key, value in context.items():
                context_str += f"{key.title().replace('_', ' ')}: {value}\n\n"
        else:
            context_str = str(context)
        
        # Get selected model from session state
        model = st.session_state.get('selected_ai_model', 'gpt-5')
        max_tokens = 15000
        
        # EXPERIMENTAL: Using responses API format
        # NOTE: This is experimental - if it doesn't work, will revert back to chat.completions
        api_params = {
            "model": model,
            "instructions": prompt,
            "input": context_str,
            "max_output_tokens": max_tokens
        }
        
        response = client.responses.create(**api_params)
        ai_response = response.output_text
        
        # Track token usage and log to Google Sheets
        if hasattr(response, 'usage') and response.usage:
            tracker = get_token_tracker()
            tracker.log_usage(
                step_name=step_name,
                input_tokens=response.usage.input_tokens,  # Changed from prompt_tokens
                output_tokens=response.usage.output_tokens,  # Changed from completion_tokens
                content_length=len(ai_response) if ai_response else 0,
                model_name=model
            )
            
            # Log detailed data to Google Sheets
            try:
                from utils.google_sheets_logger import log_detailed_data
                
                # Get session info
                session_id = st.session_state.get('session_id', 'unknown')
                doc_id = st.session_state.get('current_doc_id', '')
                
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
                    content=ai_response,
                    ai_model=model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    cost_usd=tracker.calculate_cost(response.usage.input_tokens, response.usage.output_tokens, model),
                    content_length=len(ai_response) if ai_response else 0
                )
                
                # Also update session logs with current step progress
                try:
                    from main import log_session_status_update
                    log_session_status_update()
                except Exception as e:
                    print(f"Error updating session status: {e}")
                    
            except Exception as e:
                print(f"Error logging detailed data: {e}")
        
        return ai_response
        
    except Exception as e:
        # Log the actual error for debugging
        print(f"Error generating AI response: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."