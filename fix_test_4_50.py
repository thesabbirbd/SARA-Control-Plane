import re

with open('tests/test_v1_4_50.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'await WorkerRegistry.register_worker' in line:
        new_lines.append('    cap = f"agy-{uuid.uuid4()}"\n')
        line = line.replace('f"agy-{uuid.uuid4()}"', 'cap')
    if 'await WorkerDispatcher.get_least_loaded_worker' in line:
        line = line.replace('f"agy-{uuid.uuid4()}"', 'cap')
    new_lines.append(line)

with open('tests/test_v1_4_50.py', 'w') as f:
    f.writelines(new_lines)
