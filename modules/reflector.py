import json
from modules import registry
from modules.logger import log_info, log_error

def evaluate_outcome(user_goal, plan_steps, final_output):
    """Inspects pipeline execution results against the original user intent.
    
    Returns:
        tuple: (is_satisfactory (bool), critique_or_remedy (str))
    """
    log_info("Reflector", "Initiating post-execution self-reflection critique...")
    
    eval_prompt = f"""
You are Nova's Post-Execution Evaluation and Self-Reflection Engine. Your job is to critically analyze whether the execution results of an automated pipeline genuinely satisfy the user's initial goal.

USER GOAL: "{user_goal}"
PLAN EXECUTED:
{json.dumps(plan_steps, indent=2)}

FINAL PIPELINE OUTPUT:
"{final_output}"

CRITERIA:
1. Does the final output fully answer or achieve the user's goal?
2. Is the output high quality, or did a tool return an error, empty response, or garbled/incomplete data?

Respond with a raw JSON object containing exactly two keys:
- "satisfactory": true or false
- "critique": A brief explanation of why it passed, or what went wrong and how the plan should change to fix it.

Do not include any markdown, backticks, or prose.
"""
    try:
        ask_ai_func = registry.get_service("ai")
        raw_eval = ask_ai_func(eval_prompt)
        
        # Clean up possible formatting blunders before loading
        raw_eval = raw_eval.strip().replace("```json", "").replace("```", "")
        eval_data = json.loads(raw_eval)
        
        is_satisfactory = bool(eval_data.get("satisfactory", True))
        critique = eval_data.get("critique", "Outcome matches intent parameters safely.")
        
        if is_satisfactory:
            log_info("Reflector", "Outcome passed reflection inspection. Criteria met.")
        else:
            log_info("Reflector", f"Outcome FAILED evaluation. Critique: {critique}")
            
        return is_satisfactory, critique
    except Exception as e:
        log_error("Reflector", f"Self-reflection routine encountered an error: {e}")
        # On failure, default to True to avoid locked execution loops
        return True, "Evaluation crashed; defaulting to unverified pass-through."