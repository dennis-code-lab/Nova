import json
from datetime import datetime
from modules import projects
from modules import profile
from modules.logger import log_info

def compile_startup_suggestions() -> str:
    """
    Scans active data layers (projects, profile memory) to dynamically compile 
    a contextual dashboard of immediate recommendations on startup.
    """
    log_info("ProactiveEngine", "Analyzing local workspace data for startup grounding...")
    
    # 1. Fetch current time parameters to customize greet frameworks
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning, Dennis!"
    elif current_hour < 18:
        greeting = "Good afternoon, Dennis!"
    else:
        greeting = "Good evening, Dennis!"
        
    output = f"\nNova: {greeting} Welcome to your active workspace.\n"
    output += "="*45 + "\n"
    output += "          PROACTIVE WORKSPACE INSIGHTS         \n"
    output += "="*45 + "\n"
    
    # 2. Automatically look up active milestones
    ledger = projects._load_projects_ledger()
    active_project_found = False
    
    output += "RECOMMENDED ACTIONS:\n"
    
    for key, data in ledger.items():
        if data.get("completion_percentage", 0) < 100:
            next_milestone = projects.get_next_active_milestone(key)
            if next_milestone:
                active_project_found = True
                output += f"  * [Project: {data['project_name'].upper()}] -> Type 'auto {data['project_name']}'\n"
                output += f"    to execute immediate Phase {next_milestone['id']}: {next_milestone['title']}\n"
                
    if not active_project_found:
        output += "  * No active long-term project milestones pending. Type 'new project [name]=[goal]' to seed a new roadmap.\n"
        
    # 3. Inject system profiling discovery recommendations
    output += "\nQUICK CAPABILITY SUGGESTIONS:\n"
    output += "  * Type 'projects' to review your persistent roadmap dashboard matrices.\n"
    output += "  * Type 'discover' to trigger deep structural self-capability exploration scanning.\n"
    output += "  * Type 'run tests' to run your structural integrity unit test verification loops.\n"
    output += "="*45 + "\n"
    
    return output