import re
with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 1041 (0-indexed: 1040)
lines[1040] = re.sub(r'administrador\\\\\\\\, \\\\\\\\suporte_n1\\\\\\\\, \\\\\\\\suporte_n2', '\
administrador\, \suporte_n1\, \suporte_n2\', lines[1040])

with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed')
