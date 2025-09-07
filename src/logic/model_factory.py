# src/logic/model_factory.py
import os
import streamlit as st
from src.models_config import SUPPORTED_MODELS

def get_llm_instance(provider, model_name, for_agno=True):
    """
    Factory function to get an instance of an LLM provider.

    Args:
        provider (str): The LLM provider (e.g., 'Google', 'OpenAI').
        model_name (str): The specific model name (e.g., 'gemini-2.5-flash').
        for_agno (bool): True to get the agno-native class, False for the browser-use class.

    Returns:
        An instance of the LLM class.
    """
    if provider not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported provider: {provider}")
        
    model_info = SUPPORTED_MODELS[provider]["models"].get(model_name)
    if not model_info:
        raise ValueError(f"Unsupported model '{model_name}' for provider '{provider}'")

    api_key_env = SUPPORTED_MODELS[provider]["api_key_env"]
    api_key = os.environ.get(api_key_env)

    if not api_key:
        st.error(f"Please set the {api_key_env} environment variable.")
        return None

    model_class = model_info["agno_class"] if for_agno else model_info["browser_use_class"]
    param_name = model_info["param_name"]
    
    # The browser-use classes consistently use 'model' as the parameter name
    if not for_agno:
        param_name = 'model'

    try:
        # The 'api_key' parameter is needed for agno classes and some browser_use classes
        init_params = {param_name: model_name, "api_key": api_key}
        # For browser-use, we simplify to just the model name if api_key is not a direct param
        if not for_agno:
             init_params = {'model': model_name}

        # Some agno classes might not take api_key directly if it's read from env, handle gracefully
        # However, it's safer to pass it. Let's create the instance.
        return model_class(**init_params)

    except Exception as e:
        # A more robust exception handling might be needed depending on each class constructor
        try:
             # Fallback for browser-use classes that might read from env
             if not for_agno:
                 return model_class(model=model_name)
             return model_class(**{param_name: model_name, "api_key": api_key})
        except Exception as e_inner:
            st.error(f"Failed to initialize model '{model_name}': {e_inner}")
            return None