import re
import uuid

with open('tests/test_v1_4_50.py', 'r') as f:
    t = f.read()
# Fix worker test by giving it a unique capability
t = t.replace('"agy"', 'f"agy-{uuid.uuid4()}"')
with open('tests/test_v1_4_50.py', 'w') as f:
    f.write(t)

with open('tests/test_v1_5_50.py', 'r') as f:
    t2 = f.read()
# Replace hardcoded "A", "B", "C" with unique strings by appending UUID
t2 = re.sub(r'({"id": )"([A-C])"', r'\1"\2-" + workflow_id', t2)
t2 = re.sub(r'dependencies": \["([A-C])"\]', r'dependencies": ["\1-" + workflow_id]', t2)
t2 = re.sub(r'id"] == "([A-C])"', r'id"] == "\1-" + workflow_id', t2)
t2 = re.sub(r'update_node_state\("([A-C])"', r'update_node_state("\1-" + workflow_id', t2)
with open('tests/test_v1_5_50.py', 'w') as f:
    f.write(t2)
