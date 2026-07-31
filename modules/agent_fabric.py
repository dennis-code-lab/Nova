import re
from modules.logger import log_info, log_error
from modules import router

class AgentBlackboard:
    """A shared context memory layer that agents use to pass data to one another."""
    def __init__(self):
        self.storage = {}
        self.last_output = None

    def set(self, key: str, value):
        self.storage[key] = value
        
    def get(self, key: str, default=None):
        return self.storage.get(key, default)

# Global blackboard instance for active agent sessions
session_blackboard = AgentBlackboard()

def orchestrate_multi_agent_intent(user_input: str) -> bool:
    """
    Analyzes input for complex multi-agent instructions, splits them into 
    sequential agent handoffs, and passes results along the shared blackboard.
    """
    clean_input = user_input.strip()
    
    # Identify agent linkage markers (like "then", "and then", "following that")
    delimiters = [r"\band\b\s+then\b", r"\bthen\b", r"\bnext,\b"]
    combined_pattern = "|".join(delimiters)
    
    steps = [s.strip() for s in re.split(combined_pattern, clean_input, flags=re.IGNORECASE) if s.strip()]
    
    if len(steps) <= 1:
        # Not a compound collaborative agent request; hand back to standard router
        return False

    log_info("AgentFabric", f"Detected multi-step intent. Splitting into {len(steps)} sub-agent tasks.")
    
    # Clear previous transient session states
    session_blackboard.last_output = None
    
    for i, step_text in enumerate(steps):
        # Context Injection: If an agent needs the output of a prior step, inject it
        if "it" in step_text.lower() or "that file" in step_text.lower() or "the result" in step_text.lower():
            if session_blackboard.last_output:
                # Replace pronouns with the real string representation of the last output
                step_text = re.sub(r"\b(it|that file|the result)\b", str(session_blackboard.last_output), step_text, flags=re.IGNORECASE)
        
        log_info("AgentFabric", f"Executing Sub-Agent Step {i+1}: '{step_text}'")
        
        # Pass execution directly to the intelligent single-tool router layer
        success = router.match_and_execute(step_text)
        
        if not success:
            log_error("AgentFabric", f"Sub-Agent failed to resolve task component: '{step_text}'. Aborting chain.")
            print(f"Nova [Agent Error]: Collaborative sequence broken at step: '{step_text}'")
            return True
            
    return True