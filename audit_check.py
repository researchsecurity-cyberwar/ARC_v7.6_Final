import os, sys, py_compile

# Check for file vs directory name conflicts
conflicts = []
for root, dirs, files in os.walk('.'):
    for d in dirs:
        dirpath = os.path.join(root, d)
        for f in os.listdir(dirpath):
            filepath = os.path.join(dirpath, f)
            if os.path.isfile(filepath):
                name = os.path.splitext(f)[0]
                if name == d:
                    conflicts.append(filepath)

print('=== NAME CONFLICTS (file == dir) ===')
for c in sorted(conflicts):
    print(c)
print()

# Check for missing __init__.py
missing_init = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for d in dirs:
        dirpath = os.path.join(root, d)
        if not os.path.exists(os.path.join(dirpath, '__init__.py')):
            missing_init.append(dirpath)

print('=== DIRECTORIES MISSING __init__.py ===')
for m in sorted(missing_init):
    print(m)
print()

# Syntax check all
errors = []
for root, dirs, files in os.walk('.'):
    if '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            filepath = os.path.join(root, f)
            try:
                py_compile.compile(filepath, doraise=True)
            except py_compile.PyCompileError as e:
                errors.append(str(e))

print('=== SYNTAX ERRORS ===')
if errors:
    for e in errors:
        print(e)
else:
    print('All .py files passed syntax check!')
