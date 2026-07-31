import sys
from io import StringIO
from modules.logger import log_info, log_error

def is_compound_command(user_input: str) -> bool:
    """Detects if an input string contains compound multi-tool sequencing keywords."""
    cleaned = user_input.lower()
    return " then " in cleaned or " and then " in cleaned or " && " in cleaned

def parse_and_execute_chain(user_input: str, main_router_callback) -> str:
    """
    Splits compound phrases into sequential tool tasks, captures intermediate outputs,
    and pipes data variables gracefully down the execution stream.
    """
    log_info("CompositionEngine", f"Decomposing multi-tool string: '{user_input}'")
    
    # Normalize command delimiters
    normalized = user_input.replace(" and then ", " then ").replace(" && ", " then ")
    steps = [step.strip() for step in normalized.split(" then ") if step.strip()]
    
    print(f"Nova Composition: Identified {len(steps)} sequential task steps.")
    
    last_output = ""
    execution_summary = []
    
    for idx, step in enumerate(steps):
        # Context Piping: Replace reference pronouns with the output of the previous tool execution
        if idx > 0 and any(pronoun in step.lower() for pronoun in ["the result", "it", "the output"]):
            for pronoun in ["the result", "it", "the output"]:
                if last_output:
                    step = step.replace(pronoun, last_output.strip())
        
        print(f"  -> Executing Step {idx + 1}: '{step}'")
        log_info("CompositionEngine", f"Routing composite step {idx + 1}: {step}")
        
        # Capture stdout to gather tool return messages if modules utilize direct print statements
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        try:
            # Re-route the individual step back into main's core logic router
            main_router_callback(step)
            sys.stdout = old_stdout
            step_response = redirected_output.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            log_error("CompositionEngine", f"Step {idx + 1} crashed: {e}")
            return f"Composition Halted at Step {idx + 1}. Error: {e}"
            
        # Clean up output string to isolate raw data markers for subsequent piping logic
        clean_response = step_response.replace("Nova:", "").strip()
        if "memory saved" in clean_response.lower() or "note saved" in clean_response.lower():
            pass # Retain confirmation message layout context if necessary
        else:
            last_output = clean_response
            
        execution_summary.append(f"Step {idx + 1} ({step}) -> Success")
        
    return f"Chain completed successfully:\n" + "\n".join(execution_summary)