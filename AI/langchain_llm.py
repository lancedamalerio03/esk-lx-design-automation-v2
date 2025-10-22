"""
LangChain LLM Wrapper
Provides unified interface for multiple LLM providers with LangSmith tracking
Uses init_chat_model() for standardized model initialization
"""

import os
from typing import Optional, Dict, Any
import streamlit as st
from langchain.chat_models import init_chat_model

from keys.config import (
    OPENAI_API_KEY, 
    LANGSMITH_API_KEY, 
    GOOGLE_AI_API_KEY,
    ANTHROPIC_API_KEY,
    PERPLEXITY_API_KEY
)


# Model mapping: UI name -> (provider, actual_model_name)
MODEL_MAPPING = {
    # OpenAI Models
    "gpt-5": ("openai", "gpt-5"),
    "gpt-5-mini": ("openai", "gpt-5-mini"),
    "gpt-5-nano": ("openai", "gpt-5-nano"),
    "gpt-4.1": ("openai", "gpt-4.1"),
    "gpt-4.1-mini": ("openai", "gpt-4.1-mini"),
    "gpt-4.1-nano": ("openai", "gpt-4.1-nano"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "o3": ("openai", "o3"),
    "o3-mini": ("openai", "o3-mini"),
    
    # Gemini Models (free tier for testing)
    "gemini-2.5-flash": ("google_genai", "gemini-2.5-flash"),
    "gemini-2.0-flash-exp": ("google_genai", "gemini-2.0-flash-exp"),
    "gemini-1.5-flash": ("google_genai", "gemini-1.5-flash"),
    "gemini-1.5-pro": ("google_genai", "gemini-1.5-pro"),
    
    # Claude Models (Anthropic) - Claude 4.5 generation
    "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5"),
    "claude-haiku-4.5": ("anthropic", "claude-haiku-4-5"),
    
    # Perplexity Reasoning Models (different from search tool)
    "perplexity-sonar-reasoning-pro": ("perplexity", "sonar-pro"),
    "perplexity-sonar-reasoning": ("perplexity", "sonar"),
}


def setup_langsmith():
    """Set up LangSmith environment variables for tracing"""
    if LANGSMITH_API_KEY:
        os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "esk-lx-design-automation"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        return True
    return False


def get_chat_model(model_name: str, temperature: float = 0.7, max_tokens: int = 15000):
    """
    Get a LangChain chat model instance based on model name
    Uses init_chat_model() for standardized initialization
    
    Args:
        model_name: Model name from UI (e.g., 'gpt-5', 'gemini-2.5-flash')
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        
    Returns:
        LangChain ChatModel instance
    """
    # Set up LangSmith tracing
    langsmith_enabled = setup_langsmith()
    
    # Get provider and actual model name
    if model_name not in MODEL_MAPPING:
        # Default to gpt-5 if model not found
        st.warning(f"Model '{model_name}' not found in mapping. Defaulting to gpt-5")
        provider, actual_model = MODEL_MAPPING["gpt-5"]
    else:
        provider, actual_model = MODEL_MAPPING[model_name]
    
    # Validate API keys based on provider
    if provider == "google_genai" and not GOOGLE_AI_API_KEY:
        raise ValueError("Google AI API key not configured. Please add GOOGLE_AI_API_KEY to secrets.")
    if provider == "openai" and not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured. Please add OPENAI_API_KEY to secrets.")
    if provider == "anthropic" and not ANTHROPIC_API_KEY:
        raise ValueError("Anthropic API key not configured. Please add ANTHROPIC_API_KEY to secrets.")
    if provider == "perplexity" and not PERPLEXITY_API_KEY:
        raise ValueError("Perplexity API key not configured. Please add PERPLEXITY_API_KEY to secrets.")
    
    # Use init_chat_model() - the standardized LangChain approach
    # See: https://python.langchain.com/docs/how_to/chat_models_universal_init/
    try:
        # Build config with API keys
        config_params = {
            "model": actual_model,
            "model_provider": provider,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add provider-specific API keys
        if provider == "openai":
            config_params["api_key"] = OPENAI_API_KEY
        elif provider == "google_genai":
            config_params["api_key"] = GOOGLE_AI_API_KEY
        elif provider == "anthropic":
            config_params["api_key"] = ANTHROPIC_API_KEY
        elif provider == "perplexity":
            config_params["api_key"] = PERPLEXITY_API_KEY
        
        model = init_chat_model(**config_params)
    except Exception as e:
        raise ValueError(f"Error initializing {provider}/{actual_model}: {str(e)}")
    
    # Add metadata for LangSmith
    if langsmith_enabled:
        # Get session info from streamlit session state
        session_id = st.session_state.get('session_id', 'unknown')
        current_step = st.session_state.get('current_step', 0)
        
        # LangSmith will automatically track with these tags
        model.metadata = {
            "session_id": session_id,
            "current_step": current_step,
            "model_name": model_name,
            "provider": provider,
        }
    
    return model


def get_model_info(model_name: str) -> Dict[str, Any]:
    """
    Get information about a model
    
    Args:
        model_name: Model name from UI
        
    Returns:
        Dictionary with model info (provider, actual_name, etc.)
    """
    if model_name not in MODEL_MAPPING:
        return {
            "provider": "unknown",
            "actual_model": model_name,
            "supported": False
        }
    
    provider, actual_model = MODEL_MAPPING[model_name]
    
    return {
        "provider": provider,
        "actual_model": actual_model,
        "supported": True,
        "is_free": provider == "google_genai" and "flash" in actual_model.lower()
    }


def get_available_models() -> list:
    """Get list of all available model names for UI dropdown"""
    return list(MODEL_MAPPING.keys())


def get_models_by_provider() -> Dict[str, list]:
    """Get models grouped by provider for UI organization"""
    models_by_provider = {}
    
    for model_name, (provider, _) in MODEL_MAPPING.items():
        # Convert internal provider name to display name for UI
        display_provider = "OpenAI" if provider == "openai" else \
                           "Gemini (Google)" if provider == "google_genai" else \
                           "Claude (Anthropic)" if provider == "anthropic" else \
                           "Perplexity" if provider == "perplexity" else \
                           provider
        
        if display_provider not in models_by_provider:
            models_by_provider[display_provider] = []
        models_by_provider[display_provider].append(model_name)
    
    return models_by_provider

