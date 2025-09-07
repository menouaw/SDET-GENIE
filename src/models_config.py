# src/models_config.py

# --- Agno Model Classes ---
from agno.models.google import Gemini as AgnoGemini
from agno.models.openai import OpenAIChat as AgnoOpenAI
from agno.models.anthropic import Claude as AgnoClaude
from agno.models.groq import Groq as AgnoGroq

# --- Browser-Use Model Classes ---
from browser_use import ChatGoogle
from browser_use import ChatOpenAI
from browser_use import ChatAnthropic
from browser_use import ChatGroq

SUPPORTED_MODELS = {
    "Google": {
        "api_key_env": "GOOGLE_API_KEY",
        "models": {
            "gemini-2.5-flash": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
            "gemini-2.0-flash": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
            "gemini-2.5-pro": {"agno_class": AgnoGemini, "browser_use_class": ChatGoogle, "param_name": "id"},
        },
    },
    "OpenAI": {
        "api_key_env": "OPENAI_API_KEY",
        "models": {
            "gpt-4o": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
            "gpt-4o-mini": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
            "o3": {"agno_class": AgnoOpenAI, "browser_use_class": ChatOpenAI, "param_name": "id"},
        },
    },
    "Anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "models": {
            "claude-3-7-sonnet-latest": {"agno_class": AgnoClaude, "browser_use_class": ChatAnthropic, "param_name": "id"},
            "claude-sonnet-4-0": {"agno_class": AgnoClaude, "browser_use_class": ChatAnthropic, "param_name": "id"},
        },
    },
    "Groq": {
        "api_key_env": "GROQ_API_KEY",
        "models": {
            "meta-llama/llama-4-maverick-17b-128e-instruct": {"agno_class": AgnoGroq, "browser_use_class": ChatGroq, "param_name": "id"},
            "meta-llama/llama-3.1-8b-instant": {"agno_class": AgnoGroq, "browser_use_class": ChatGroq, "param_name": "id"},
        },
    },
}