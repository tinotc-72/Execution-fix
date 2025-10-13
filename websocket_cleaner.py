#!/usr/bin/env python3
import re

# Read the file
with open('/Users/tinotchinyoka/Desktop/Algo Trading/Axiom Sniper 13.03.25/Attempt/Hope/main.py', 'r') as f:
    content = f.read()

# Remove all lines that start with WebSocket method content from the broken area
lines = content.split('\n')
new_lines = []
in_websocket_method = False
method_indent = 0

for i, line in enumerate(lines):
    # Skip the broken WebSocket method content (lines 446 onwards until we hit a proper method)
    if i >= 445 and i < 1534:  # Skip the broken WebSocket section
        if line.strip().startswith('async def _execute_copy_buy'):
            new_lines.append(line)
            in_websocket_method = False
        else:
            continue
    else:
        new_lines.append(line)

# Write back
with open('/Users/tinotchinyoka/Desktop/Algo Trading/Axiom Sniper 13.03.25/Attempt/Hope/main.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("WebSocket methods removed successfully!")
