import os
import json
from modules import registry
from modules.calculator import calculate
from modules.profile import remember_fact, get_fact
from modules.guardrails import validate_execution_plan
from modules.logger import log_info, log_error

def run_system_tests():
    """Executes a suite of programmatic structural assertions against Nova's core components."""
    log_info("AutomatedTester", "Warming engine test beds and initializing mock fixtures...")
    
    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    def assert_test(component_name, test_name, condition, message=""):
        if condition:
            results["passed"] += 1
            results["details"].append(f"  [PASS] {component_name} -> {test_name}")
        else:
            results["failed"] += 1
            results["details"].append(f"  [FAIL] {component_name} -> {test_name} | Reason: {message}")

    print("\n" + "~"*60)
    print("             NOVA AUTOMATED UNIT TESTING ENGINE            ")
    print("~"*60)

    # Test Case 1: Core Math Engine Utilities
    try:
        math_res = calculate("2 + 3 * 4")
        assert_test("Calculator", "Operator Precedence evaluation", "14" in str(math_res), f"Expected 14, got {math_res}")
    except Exception as e:
        assert_test("Calculator", "Crash Boundary Check", False, str(e))

    # Test Case 2: Service Registry Integrity Checks
    try:
        registry_dict = {}
        for attr_name in ["services", "SERVICES", "_services", "registry_map"]:
            if hasattr(registry, attr_name):
                target = getattr(registry, attr_name)
                if isinstance(target, dict):
                    registry_dict = target
                    break
        
        assert_test("Registry", "Critical AI anchor verification", "ai" in registry_dict, "Missing primary 'ai' injection key")
        assert_test("Registry", "Orchestrator hook presence", "run_autonomous_goal" in registry_dict, "Missing 'run_autonomous_goal'")
    except Exception as e:
        assert_test("Registry", "Reflection Inspection", False, str(e))

    # Test Case 3: Identity Profile Ledger Operations
    try:
        # Save a temporary testing fixture fact
        remember_fact("test_metric_key", "verified_unit_test")
        fetched_val = get_fact("test_metric_key")
        assert_test("ProfileMemory", "State Write/Read alignment", fetched_val == "verified_unit_test", f"Expected 'verified_unit_test', got '{fetched_val}'")
    except Exception as e:
        assert_test("ProfileMemory", "Storage Matrix Execution", False, str(e))

    # Test Case 4: Plan Validation Guardrail Limits
    try:
        # Test malformed input strings that should fail guardrail checks safely
        is_safe, _ = validate_execution_plan("INVALID NON JSON STRUCT CORRUPTION")
        assert_test("Guardrails", "Syntactical parser rejection safety", is_safe == False, "Allowed corrupt non-JSON strings to clear gates")
        
        # Test infinite loop ceiling enforcement
        overflow_json = json.dumps([{"service": "ai", "input_key": "x", "output_key": "y"}] * 10)
        is_safe, message = validate_execution_plan(overflow_json)
        assert_test("Guardrails", "Max loop circuit breaker ceilings", is_safe == False, "Allowed plan to exceed step constraint thresholds")
    except Exception as e:
        assert_test("Guardrails", "Boundary Execution Validation", False, str(e))

    # Print out detailed results map
    for detail in results["details"]:
        print(detail)
        
    print("~"*60)
    summary_str = f"Test suite finished. Passed: {results['passed']} | Failed: {results['failed']}"
    print(summary_str)
    print("~"*60 + "\n")
    
    return summary_str