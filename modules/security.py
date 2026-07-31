import sys
from modules.logger import log_info, log_error

# Explicitly mapping system domains to security risk tiers
TOOL_TRUST_POLICIES = {
    # Low Risk - Auto-executes without interruption
    "calc": "LOW", "time": "LOW", "date": "LOW", "year": "LOW", "help": "LOW", 
    "list notes": "LOW", "profile list": "LOW", "discover": "LOW", "projects": "LOW",
    
    # High Risk - Requires Human-in-the-Loop Validation [Y/N]
    "save note": "HIGH", "open": "HIGH", "find file": "HIGH", "auto": "HIGH", 
    "remember": "HIGH", "profile remember": "HIGH", "run tests": "HIGH",
    
    # Critical Risk - Destructive / Hardware State disruption
    "lock computer": "CRITICAL", "sleep computer": "CRITICAL", 
    "restart computer": "CRITICAL", "shutdown computer": "CRITICAL"
}

def verify_tool_permission(command_string: str) -> bool:
    """
    Inspects the incoming command payload, determines its trust level tier,
    and forces terminal authentication or confirmation if permissions dictate.
    """
    lower = command_string.strip().lower()
    
    # Determine which tool rule matches the input vector
    matched_tool = "LOW"
    policy_tier = "LOW"
    
    for tool, tier in TOOL_TRUST_POLICIES.items():
        if lower.startswith(tool) or tool in lower:
            # Upgrade policy if a higher risk tool token is detected in the string
            if tier == "HIGH" and policy_tier != "CRITICAL":
                policy_tier = "HIGH"
                matched_tool = tool
            elif tier == "CRITICAL":
                policy_tier = "CRITICAL"
                matched_tool = tool

    # --- Policy Gate Enforcement Layout ---
    if policy_tier == "LOW":
        return True # Safe execution clearing
        
    elif policy_tier == "HIGH":
        log_info("SecurityGate", f"Intercepted HIGH-trust command operation: '{matched_tool}'")
        print(f"\n[SECURITY ALERT] Nova is attempting an elevated action: '{command_string}'")
        confirm = input("Are you sure you want to authorize this execution? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            log_info("SecurityGate", "User authorized HIGH-trust operation explicitly.")
            return True
        else:
            print("Nova: Action aborted by user policy denial.")
            return False
            
    elif policy_tier == "CRITICAL":
        log_error("SecurityGate", f"CRITICAL SYSTEM BLOCKADE TRIGGERED FOR: '{matched_tool}'")
        print(f"\n[CRITICAL SECURITY BLOCK] Destructive command threat vector detected: '{matched_tool.upper()}'")
        print("This operation requires explicit administrator confirmation.")
        confirm = input("Type 'CONFIRM' to release root execution safety rails: ").strip()
        if confirm == "CONFIRM":
            log_info("SecurityGate", "Root authorization override confirmed.")
            return True
        else:
            print("Nova: Critical action rejected. Access denied.")
            return False

    return True