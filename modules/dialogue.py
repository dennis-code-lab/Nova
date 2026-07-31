import json
from modules.ai import ask_ai
from modules import projects
from modules import profile
from modules.logger import log_info

# In-memory rolling history cache for casual conversational context tracking
_chat_context_history = []
MAX_HISTORY_TURNS = 5

def process_natural_dialogue(user_input: str) -> str:
    """
    Resolves multi-turn conversational context, matches profile/project keywords, 
    and returns a fluid, naturally aware follow-up response.
    """
    global _chat_context_history
    log_info("DialogueEngine", f"Processing natural chat stream: '{user_input}'")
    
    # 1. Look up data fragments from existing modules for contextual grounding
    active_projects_ledger = projects._load_projects_ledger()
    project_hints = [data["project_name"] for data in active_projects_ledger.values()]
    
    # Check if user is referencing an active project implicitly
    detected_project_context = ""
    for p_key, p_data in active_projects_ledger.items():
        if p_key in user_input.lower() or p_data["project_name"].lower() in user_input.lower():
            next_m = projects.get_next_active_milestone(p_key)
            m_str = next_m["title"] if next_m else "All Milestones Done"
            detected_project_context = f"User is currently discussing active Project '{p_data['project_name']}' (Next pending milestone: {m_str})."
            break

    # 2. Compile rolling short-term memory array
    history_block = ""
    if _chat_context_history:
        history_block = "RECENT CONVERSATION TURNS:\n" + "\n".join(_chat_context_history)

    # 3. Formulate the Contextual Dialogue Prompt
    dialogue_prompt = f"""
You are Nova, an authentic, adaptive AI collaborator. You are engaged in a natural, fluid conversation with the user.

SYSTEM STATIC PROFILE GROUNDING:
- User Name: Dennis
- Favorite Football Team: Arsenal
- Favorite Color: Green

DYNAMIC WORKSPACE CONTEXT:
{detected_project_context if detected_project_context else "No active project explicitly focused in this phrase."}
Tracked Active Roadmaps: {', '.join(project_hints) if project_hints else "None"}

{history_block}

CURRENT USER INPUT (Treat this as a natural follow-up if pronoun references or implicit contextual cues are present):
"{user_input}"

INSTRUCTIONS:
- Maintain a supportive, direct, and slightly witty persona.
- Answer the user's input directly. If they use pronouns like "they", "it", or "before", resolve them using the RECENT CONVERSATION TURNS provided above.
- Keep the response clean, concise, and conversational. Do not output markdown code blocks or JSON formatting tags.
"""

    # 4. Invoke the optimized Gemini interface box
    response = ask_ai(dialogue_prompt)
    
    # 5. Push current exchange turn into rolling memory history window
    _chat_context_history.append(f"User: {user_input}")
    _chat_context_history.append(f"Nova: {response}")
    if len(_chat_context_history) > (MAX_HISTORY_TURNS * 2):
        _chat_context_history = _chat_context_history[-2:]
        
    return response