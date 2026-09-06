import json
import re

raw_input = """$http.body.choices"""

try:
    data = json.loads(raw_input)
    content = data[0]["message"]["content"]
except Exception:
    match = re.search(r'"content":\s*"(.*?)"', raw_input, re.DOTALL)
    if match:
        content = match.group(1)
    else:
        content = raw_input

# 1. Clean up unescaped quotes and newlines
content = content.replace('\\n', '\n').replace('\\"', '"')

# 2. Strip Markdown formatting (asterisks and backticks)
content = content.replace('**', '').replace('`', '')

# 3. Clean up extra newlines before section labels
content = re.sub(r'\n+\s*(Threat Category:)', r'\n\1', content)
content = re.sub(r'\n+\s*(Reasoning:)', r'\n\1', content)

# 4. Ensure each key header starts cleanly on a new line
content = re.sub(r'\s*(Threat Category:)', r'\nThreat Category:', content)
content = re.sub(r'\s*(Reasoning:)', r'\nReasoning:', content)

print(content.strip())