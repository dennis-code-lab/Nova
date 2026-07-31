from modules.profile import list_facts
from modules.logger import log_info, log_error

def assemble_knowledge_graph():
    """Gathers facts from user profile memory and compiles them into a reasoning block."""
    log_info("Reasoner", "Harvesting structural profile memory context...")
    try:
        facts_str = list_facts()
        # Handle empty memory or uninitialized files gracefully
        if not facts_str or "No facts found" in facts_str:
            return "No user profile facts currently cached."
        return facts_str
    except Exception as e:
        log_error("Reasoner", f"Failed to gather knowledge context: {e}")
        return "Error loading profile knowledge base."