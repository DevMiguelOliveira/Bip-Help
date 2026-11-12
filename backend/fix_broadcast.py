with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the broadcast section and add 'interna' field
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    if '"type": "new_message",' in line:
        # Look ahead for the closing brace of the dict
        j = i + 1
        while j < len(lines) and '}' not in lines[j]:
            j += 1
        # Insert the interna field before the closing brace
        if j < len(lines):
            indent = len(lines[j]) - len(lines[j].lstrip())
            new_lines.append(' ' * indent + '            \"interna\": db_mensagem.interna,\n')
    i += 1

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Added interna field to broadcast')
