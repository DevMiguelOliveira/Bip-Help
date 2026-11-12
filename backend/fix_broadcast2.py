with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the indentation of the interna field
new_lines = []
for line in lines:
    if '\"interna\": db_mensagem.interna,' in line:
        # Fix indentation to match the other fields
        new_lines.append('              \"interna\": db_mensagem.interna,\n')
    else:
        new_lines.append(line)

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed indentation')
