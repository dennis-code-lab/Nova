from modules.logger import log_info

def show_help() -> str:
    """Returns the core Nova options index string."""
    return """
=== NOVA HELP SYSTEM ===

[Task Manager]
* add task <text>          - Add a new task to your list
* show tasks               - Display all current tasks
* complete task <number>   - Remove a task by its list number

[Alarms Engine]
* set alarm for <HH:MM>    - Set a 24-hour persistent alarm
* show alarms              - List all active alarms
* delete alarm <HH:MM>     - Delete a specific set alarm

[Reminders]
* remind me to <text>      - Create a generic reminder
* remind me to <x> at <t>  - Set a reminder for a specific time
* show reminders           - Display all active reminders

[Timers & Stopwatch]
* set timer <n> seconds    - Start a countdown timer (seconds)
* set timer <n> minutes    - Start a countdown timer (minutes)
* set timer <n> hours      - Start a countdown timer (hours)
* start stopwatch          - Begin a stopwatch tracker
* stopwatch time           - Check elapsed stopwatch time
* stop stopwatch           - Stop and clear the stopwatch

[Smart Notes]
* save note <title>=<text> - Create or rewrite a note file
* read note <title>        - Read full contents of a note
* list notes               - List all text notes in folder
* find note <keyword>      - Scan titles and text for a match

[Web Discovery]
* search <query>           - Run a browser search
* search for <query>       - Alternative search routing
* latest <query>           - Find recent updates
* news about <query>       - Search news aggregates

[File System]
* find file <filename>     - Scan directories for a match

[Weather Diagnostics]
* weather <city>           - Retrieve live regional weather updates

[System Information]
* battery status           - Check power and battery life levels
* disk space               - View hard drive storage limits
* computer name            - Output local host computer identity
* current user             - Display active profile session name
* ip address               - Display local network connection IP

[Daily Planner]
* plan my day              - Display aggregated tasks, alarms, and reminders

[System Control]
* lock computer            - Instantly lock the OS interface
* sleep computer           - Put the computer into low-power sleep mode
* restart computer         - Reboot the operating system
* shutdown computer        - Power off the local machine completely

[Utilities]
* flip a coin              - Randomly returns Heads or Tails
* roll a dice              - Generates a dynamic dice roll (1-6)
* random number            - Generates a random integer (1-100)

[Help Dashboard]
* help                     - Display this core options index
"""

def get_specific_help(query: str) -> str:
    """
    Scans the existing show_help string dynamically for lines or section categories 
    matching your command query parameter.
    """
    log_info("HelpSystem", f"Searching explicit system help definitions for: '{query}'")
    clean_query = query.strip().lower()
    help_text = show_help()
    
    matched_lines = []
    current_section = "General"
    
    for line in help_text.splitlines():
        if line.startswith("[") and line.endswith("]"):
            current_section = line
            continue
        if clean_query in line.lower() and "*" in line:
            matched_lines.append(f"{current_section} -> {line.strip()}")
            
    if matched_lines:
        output = f"\n--------------------------------------------------\n"
        output += f" MATCHED COMMAND SYNTAX FOR: {query.upper()}\n"
        output += f"--------------------------------------------------\n"
        for match in matched_lines:
            output += f" {match}\n"
        output += f"--------------------------------------------------\n"
        return output
        
    return f"Nova: I couldn't isolate an explicit rule syntax for '{query}' inside my index layout. Type 'help' to review all paths."