import json
from modules import registry
from modules.logger import log_info, log_error

MAX_ALLOWED_STEPS = 5  # Infinite loop / runaway plan circuit breaker

def validate_execution_plan(raw_plan_string):
    """
    Validates an AI-generated plan for structural integrity, 
    whitelisted service registry availability, and runtime safety boundaries.
    Returns (True, parsed_steps_list) if safe, or (False, error_message).
    """
    log_info("Guardrails", "Intercepting generated execution plan for safety review...")
    
    # 1. Structural Validation (Clean & Parse JSON)
    try:
        clean_str = raw_plan_string.replace("```json", "").replace("```", "").strip()
        plan_steps = json.loads(clean_str)
    except Exception as e:
        log_error("Guardrails", f"Plan validation failed: Malformed JSON syntax. {e}")
        return False, f"Safety violation: The generated plan is not valid JSON. Details: {e}"

    if not isinstance(plan_steps, list):
        log_error("Guardrails", "Plan validation failed: Blueprint is not a structured sequence list.")
        return False, "Safety violation: Plan payload must be a linear sequence array."

    # 2. Execution Runaway Bounds Check (Circuit Breaker)
    if len(plan_steps) > MAX_ALLOWED_STEPS:
        log_error("Guardrails", f"Plan validation failed: Step count ({len(plan_steps)}) exceeds ceiling safety margin.")
        return False, f"Safety violation: Execution plan contains too many steps ({len(plan_steps)}). Maximum allowed is {MAX_ALLOWED_STEPS}."

    # 3. Service Registry Whitelist Check
    for index, step in enumerate(plan_steps, start=1):
        if not isinstance(step, dict) or "service" not in step:
            log_error("Guardrails", f"Plan validation failed: Step index {index} lacks explicit service identifier keys.")
            return False, f"Safety violation: Step definition at position {index} is structurally deformed."

        requested_service = step["service"]
        
        # Verify the tool is actually loaded and live inside our v48 Service Registry catalog!
        try:
            registry.get_service(requested_service)
        except RuntimeError:
            log_error("Guardrails", f"Plan validation failed: Service [{requested_service}] requested by step {index} is UNREGISTERED.")
            return False, f"Safety violation: The plan attempts to call a non-existent or blocked service tool: '[{requested_service}]'."

    log_info("Guardrails", "Execution plan cleared all security checkpoints. Status: SAFE.")
    return True, plan_steps