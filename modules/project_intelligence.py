import json
from modules import projects
from modules import orchestrator
from modules.logger import log_info, log_error

def link_and_execute_project_goal(user_input: str) -> str:
    """
    Scans active project boards to determine if the user intent connects to a 
    long-term milestone. If found, it routes the goal into the automated pipeline.
    """
    ledger = projects._load_projects_ledger()
    target_project_key = None
    matched_milestone = None
    
    # Clean the input to check for exact project keyword hooks
    cleaned_input = user_input.lower().strip()
    
    # 1. Match intent against registered projects
    for project_key, project_data in ledger.items():
        if project_key in cleaned_input or project_data["project_name"].lower() in cleaned_input:
            target_project_key = project_key
            break
            
    if not target_project_key:
        log_info("ProjectIntelligence", "No active long-term project matched. Routing to standard autonomous planner.")
        return orchestrator.generate_and_run_plan(user_input)
        
    # 2. Extract the current active milestone from the project roadmap
    matched_milestone = projects.get_next_active_milestone(target_project_key)
    
    if not matched_milestone:
        return f"Project Intelligence: All milestones for project '{ledger[target_project_key]['project_name']}' are already completed!"
        
    project_name = ledger[target_project_key]["project_name"]
    milestone_id = matched_milestone["id"]
    milestone_title = matched_milestone["title"]
    
    log_info("ProjectIntelligence", f"Context Lock: Found active milestone for project '{project_name}' -> Phase {milestone_id}: {milestone_title}")
    print(f"Nova Intelligence: Context Locked on Project '{project_name}' (Phase {milestone_id}/{len(ledger[target_project_key]['milestones'])})")
    print(f"Nova Intelligence: Targeting Milestone -> '{milestone_title}'")
    
    # 3. Formulate an enriched goal prompt containing the milestone parameters
    enriched_goal = f"Execute Phase {milestone_id} for project '{project_name}'. Current Milestone Objective: {milestone_title}."
    
    # 4. Route the enriched goal into the standard Orchestration loop
    execution_result = orchestrator.generate_and_run_plan(enriched_goal)
    
    # 5. Check if execution succeeded by examining return content for error keywords
    if "Execution Error:" not in str(execution_result) and "Core Inference Error:" not in str(execution_result):
        log_info("ProjectIntelligence", f"Milestone success verified. Closing out phase {milestone_id} for project '{target_project_key}'.")
        
        # Parse step traces out of internal console if telemetry is active
        from modules.console import _telemetry_cache
        active_traces = _telemetry_cache.get("step_traces", [])
        
        # Permanently advance the project state on disk
        update_summary = projects.mark_milestone_complete(target_project_key, milestone_id, traces=active_traces)
        print(f"Nova Intelligence: {update_summary}")
        return f"Project Milestone Success! Result: {execution_result}"
    else:
        log_error("ProjectIntelligence", f"Orchestrator failed to fulfill milestone phase {milestone_id}. Project state held.")
        return f"Project Milestone Execution Halted. Reason: {execution_result}"