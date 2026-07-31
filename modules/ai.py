import os
from google import genai
from google.genai import types

# Global client reference for Nova's conversational brain
_client = None
_DEFAULT_MODEL = "gemini-2.5-flash"  # Standard high-performance baseline model

def _discover_api_key():
    """Tries multiple locations to find your existing Gemini API key based on your workspace setup."""
    # 1. Check standard modern environment variable
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ.get("GEMINI_API_KEY")
        
    # 2. Check legacy environment variable
    if os.environ.get("GOOGLE_API_KEY"):
        return os.environ.get("GOOGLE_API_KEY")
        
    # 3. Check Nova's dedicated data/config.json configuration path
    config_path = os.path.join("data", "config.json")
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                # Try all common variable name styles used in configs
                for key_variant in ["gemini_api_key", "api_key", "gemini_key", "GEMINI_API_KEY"]:
                    if key_variant in config_data and config_data[key_variant]:
                        return config_data[key_variant]
        except Exception:
            pass
            
    # 4. Global fallback to main directory memory if present
    if os.path.exists("memory.json"):
        try:
            import json
            with open("memory.json", "r", encoding="utf-8") as f:
                mem = json.load(f)
                if "api_key" in mem: return mem["api_key"]
        except Exception:
            pass
        
    return None

def initialize_nova():
    """Initializes the modern Google GenAI Client interface safely."""
    global _client
    api_key = _discover_api_key()
    
    try:
        if api_key:
            # Explicitly feed the key directly to the client constructor
            _client = genai.Client(api_key=api_key)
            os.environ["GEMINI_API_KEY"] = api_key
        else:
            # Attempt default system credential setup
            _client = genai.Client()
    except Exception as e:
        raise RuntimeWarning(f"GenAI Client failed to initialize. Check your API environment keys: {e}")

def ask_ai(prompt: str) -> str:
    """Generates a text completion using the unified Client models interface."""
    global _client
    if _client is None:
        initialize_nova()
        
    try:
        response = _client.models.generate_content(
            model=_DEFAULT_MODEL,
            contents=prompt
        )
        if response and response.text:
            return response.text.strip()
        return "Nova Engine Error: Model returned an empty generation response block."
    except Exception as e:
        return f"Core Inference Error: Failure communicating with GenAI pipeline. Details: {e}"

def ask_ai_with_config(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Advanced generation option supporting dynamic hyperparameter configurations."""
    global _client
    if _client is None:
        initialize_nova()
        
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        response = _client.models.generate_content(
            model=_DEFAULT_MODEL,
            contents=prompt,
            config=config
        )
        return response.text.strip() if response.text else ""
    except Exception as e:
        return f"Config Inference Error: {e}"