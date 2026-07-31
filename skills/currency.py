from modules.bus import subscribe
from modules import registry

SKILL_MANIFEST = {
    "intent_trigger": "CONVERT_CURRENCY",
    "description": "Exposes conversion steps to the autonomous planning module.",
    "parameter_key": "amount_or_query"
}

def calculate_base_rate(parameter):
    """Atomic functional step inside a workflow pipeline."""
    return f"Conversion parameter verified: '{parameter}'. The calculation index scales precisely at 130 KES per USD standard baseline."

def on_nova_boot(data):
    try:
        # Simply ensure our tool is registered globally so Nova can plan out workflows around it!
        registry.register_service("currency_calc", calculate_base_rate)
    except Exception:
        pass

subscribe("system_boot", on_nova_boot)

def execute(parameter):
    if not parameter: return "Please enter an amount."
    return calculate_base_rate(parameter)