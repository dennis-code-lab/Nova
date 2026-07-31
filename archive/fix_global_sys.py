# fix_global_sys.py
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# Force 'import sys' to be at the absolute top of the file if it isn't
if "import sys" not in content[:200]:
    content = "import sys\n" + content
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ Added global sys import to the top of main.py")
else:
    print("Global sys import already present.")