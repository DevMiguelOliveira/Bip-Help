with open('D:/PROJETOS/BipHelp/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'if papel not in (administrador\\, \\suporte_n1\\, \\suporte_n2\\):'
new = 'if papel not in (\ administrador\, \suporte_n1\, \suporte_n2\):'
content = content.replace(old, new)

with open('D:/PROJETOS/BipHelp/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')
