import re
from modules.logger import log_info, log_error
from modules.health import safe_execute_tool

# Global registry dictionary mapping tool keys to metadata
TOOL_REGISTRY = {}

def register_tool(name: str, keywords: list, usage: str, callback_function):
    """Registers a core tool capability into the intelligent routing matrix."""
    TOOL_REGISTRY[name] = {
        "keywords": [kw.lower() for kw in keywords],
        "usage": usage,
        "callback": callback_function
    }
    log_info("RouterEngine", f"Successfully registered intelligent tool: '{name}'")

def match_and_execute(user_input: str) -> bool:
    """
    Analyzes input semantic keywords, selects the single most accurate tool match,
    safely parses arguments, and executes the operation. Returns True if handled.
    """
    clean_input = user_input.strip()
    lower_input = clean_input.lower()
    
    if not clean_input:
        return False
        
    best_tool = None
    highest_score = 0
    
    # Calculate keyword match weight scoring
    for tool_name, metadata in TOOL_REGISTRY.items():
        score = 0
        for kw in metadata["keywords"]:
            if kw in lower_input:
                # Give higher weight to exact word or multi-word keyword phrases
                score += len(kw.split()) * 2
        
        if score > highest_score:
            highest_score = score
            best_tool = tool_name
            
    # Intent threshold rule: if no tools match significantly, fall back to dialogue
    if not best_tool or highest_score < 2:
        return False
        
    metadata = TOOL_REGISTRY[best_tool]
    log_info("RouterEngine", f"Selected tool '{best_tool}' with confidence score {highest_score}")
    
    # Delegate execution to the v69 safety layer
    safe_execute_tool(metadata["callback"], clean_input)
    return True

def get_tool_directory() -> str:
    """Compiles a clean layout summary of all dynamically active tools."""
    output = "\n"+"="*50+"\n"
    output += "            INTELLIGENT TOOL DIRECTORY\n"
    output += "="*50+"\n"
    for name, data in TOOL_REGISTRY.items():
        output += f" • [{name.upper()}]\n"
        output += f"   Usage: {data['usage']}\n"
        output += f"   Triggers: {', '.join(data['keywords'])}\n\n"
    output += "="*50+"\n"
    return output