import json
from modules import registry
from modules.guardrails import validate_execution_plan
from modules.reasoner import assemble_knowledge_graph
from modules.reflector import evaluate_outcome
from modules.learner import recall_relevant_lessons, record_experience
from modules.console import update_telemetry
from modules.optimizer import compress_context_stream, distill_failure_trajectory
from modules.logger import log_info, log_error
from modules import profiler

def generate_and_run_plan(user_goal):
    """Compiles, runs, reflects, tracks pipeline latency, and writes telemetry logs."""
    log_info("OrchestrationEngine", f"Received autonomous goal request: '{user_goal}'")

    # Profile grounding assembly
    profiler.start_timer("GroundingAssembly")
    raw_knowledge = assemble_knowledge_graph()
    raw_lessons = recall_relevant_lessons(user_goal)
    profiler.stop_timer("GroundingAssembly")

    # Profile token stream optimization
    profiler.start_timer("ContextOptimization")
    knowledge_context = compress_context_stream(str(raw_knowledge), max_lines=10)
    historical_lessons = compress_context_stream(str(raw_lessons), max_lines=8)
    profiler.stop_timer("ContextOptimization")

    available_tools = {
        "currency_calc": "Converts currency parameters into KES baseline metrics. Expects text string.",
        "ai": "Generates natural language summaries, explanations, or reasoning. Expects text string input.",
        "voice": "Narrates text aloud using text-to-speech engines. Expects text string input."
    }

    current_attempt = 1
    max_retries = 3
    remedy_context = "This is the initial planning phase."

    initial_failure_plan = None
    first_failure_critique = None
    all_executed_steps = []

    while current_attempt <= max_retries:
        log_info("OrchestrationEngine", f"Execution Lifecycle Loop: Attempt {current_attempt}/{max_retries}")

        planner_prompt = f"""
You are Nova's Planning & Knowledge Reasoning Engine. Your job is to break down the user's goal into a valid sequence of steps using ONLY the available tools listed below.

USER PROFILE KNOWLEDGE BASE:
{knowledge_context}

HISTORICAL LESSONS FROM PAST FAILURES:
{historical_lessons}

AVAILABLE TOOLS:
{json.dumps(available_tools, indent=2)}

USER GOAL: "{user_goal}"

EXECUTION REFLECTION FEEDBACK FROM PREVIOUS ATTEMPT:
{remedy_context}

INSTRUCTIONS:
1. Review HISTORICAL LESSONS and PREVIOUS ATTEMPT FEEDBACK carefully to avoid generating invalid tools, wrong arguments, or broken workflow layouts.
2. You must respond with a raw, valid JSON array of objects representing the steps. Do not include any markdown, backticks, or prose.
"""
        try:
            # Profile Gemini Inference
            profiler.start_timer("GeminiAPIInference")
            ask_ai_func = registry.get_service("ai")
            raw_plan_response = ask_ai_func(planner_prompt)
            profiler.stop_timer("GeminiAPIInference")

            # Profile Guardrail parsing
            profiler.start_timer("GuardrailValidation")
            is_safe, validation_result = validate_execution_plan(raw_plan_response)
            profiler.stop_timer("GuardrailValidation")

            if not is_safe:
                remedy_context = f"Plan rejected by system guardrails: {validation_result}. Reformulate string structure."
                current_attempt += 1
                continue

            plan_steps = validation_result

            for step in plan_steps:
                all_executed_steps.append(step.get("service"))

            # Profile Workflow engine configuration and pipeline completion
            profiler.start_timer("WorkflowExecution")
            workflow_factory = registry.get_service("create_workflow")
            dynamic_pipeline = workflow_factory(f"Autonomous_Plan_Try_{current_attempt}")

            for step in plan_steps:
                dynamic_pipeline.add_step(
                    service_name=step["service"],
                    input_key=step.get("input_key"),
                    output_key=step.get("output_key")
                )

            final_result = dynamic_pipeline.execute(initial_input=user_goal)
            profiler.stop_timer("WorkflowExecution")

            # Profile Reflection evaluation
            profiler.start_timer("OutcomeReflection")
            is_satisfactory, critique = evaluate_outcome(user_goal, plan_steps, final_result)
            profiler.stop_timer("OutcomeReflection")

            if is_satisfactory:
                if current_attempt > 1 and initial_failure_plan:
                    clean_critique = distill_failure_trajectory(first_failure_critique)
                    record_experience(user_goal, initial_failure_plan, plan_steps, clean_critique)

                log_info("OrchestrationEngine", "Plan execution verified successfully by reflection engine.")
                update_telemetry(user_goal, current_attempt, "Success Verified", all_executed_steps)
                return final_result
            else:
                log_info("OrchestrationEngine", f"Attempt {current_attempt} outcome rejected. Self-correcting...")
                if current_attempt == 1:
                    initial_failure_plan = plan_steps
                    first_failure_critique = critique

                remedy_context = f"The previous execution outcome was REJECTED by evaluation check. Critique details: {critique}"
                current_attempt += 1

        except Exception as e:
            log_error("OrchestrationEngine", f"Error encountered during runtime cycle: {e}")
            remedy_context = f"Execution cycle crashed with exception error: {e}"
            current_attempt += 1

    log_error("OrchestrationEngine", "Max replanning retry loop budget completely exhausted.")
    update_telemetry(user_goal, current_attempt - 1, "Failed / Budget Exhausted", all_executed_steps)
    return f"Execution Error: Nova exhausted its self-correction budget. Last state: {remedy_context}"
