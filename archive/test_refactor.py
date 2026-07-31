# test_refactor.py
import os
from modules.code_intel import code_intel
from modules.refactor import RefactorEngine

def verify_system_file(target_file_path: str):
    if not os.path.exists(target_file_path):
        print(f"Error: Could not find '{target_file_path}' to analyze.")
        return

    print(f"Parsing '{target_file_path}' via CodeIntelEngine...")
    # 1. Reuse existing CodeIntel parser setup
    raw_intel = code_intel.parse_file_structure(target_file_path, return_raw=True)
    
    if "error" in raw_intel:
        print(f"Parser Error: {raw_intel['error']}")
        return
        
    ast_tree = raw_intel["tree"]
    raw_source = raw_intel["source"]
    
    # 2. Run our Refactor analysis
    print("Analyzing AST for structural smells...")
    engine = RefactorEngine()
    findings = engine.analyze_ast(ast_tree, raw_source)
    
    # 3. Print the clean structured output
    print("\n" + "="*50)
    print(f"🔍 REFRACTOR FINDINGS FOR: {target_file_path}")
    print("="*50)
    
    if not findings:
        print("✨ Clean bill of health! No issues detected.")
    else:
        for idx, finding in enumerate(findings, 1):
            print(f"{idx}. [{finding['type']}] Line {finding['line']}: {finding['message']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Let's test it on your newly saved modules/code_intel.py!
    verify_system_file("modules/code_intel.py")