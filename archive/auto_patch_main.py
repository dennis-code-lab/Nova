# auto_patch_main.py
import re
from pathlib import Path

main_path = Path("main.py")

if not main_path.exists():
    print("❌ Error: main.py not found in the current directory.")
    exit(1)

# 1. Backup main.py first just in case
backup_path = Path("main.py.bak")
backup_path.write_text(main_path.read_text(encoding="utf-8"), encoding="utf-8")
print("🛡️ Created backup: main.py.bak")

content = main_path.read_text(encoding="utf-8")

# 2. Add import if missing
import_line = "from modules.engineering_controller import EngineeringController"
if import_line not in content:
    content = import_line + "\n" + content
    print("✅ Added EngineeringController import to main.py")

# 3. v82 Handler block to inject
v82_handlers = '''    # =========================================================
    # v82 Autonomous Engineering Commands
    # =========================================================
    if clean_input.startswith("improve "):
        target_file = user_input.strip()[8:].strip()
        controller = EngineeringController()
        controller.improve_target(target_file)
        return True

    if clean_input in ["engineering session", "session"]:
        controller = EngineeringController()
        controller.run_engineering_session()
        return True
'''

# 4. Inject v82 handlers into route_system_intent
if 'clean_input.startswith("improve ")' not in content:
    # Find the start of route_system_intent definition and insert inside
    target_pattern = r"(def route_system_intent\([^)]*\):(?:\s*\"\"\"[^\"]*\"\"\")?\s*clean_input\s*=\s*user_input\.strip\(\)\.lower\(\))"
    
    if re.search(target_pattern, content):
        content = re.sub(
            target_pattern,
            r"\1\n\n" + v82_handlers,
            content,
            count=1
        )
        print("✅ Injected v82 command routing into route_system_intent()")
    else:
        # Fallback placement right under function definition
        fallback_pattern = r"(def route_system_intent\([^)]*\):)"
        content = re.sub(
            fallback_pattern,
            r"\1\n    clean_input = user_input.strip().lower()\n" + v82_handlers,
            content,
            count=1
        )
        print("✅ Injected v82 command routing into route_system_intent() (fallback mode)")

# Save updated main.py
main_path.write_text(content, encoding="utf-8")
print("🎉 Successfully patched main.py!")