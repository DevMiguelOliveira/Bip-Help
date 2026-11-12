with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('administrador\\\\, \\\\suporte_n1\\\\, \\\\suporte_n2', '\
administrador\, \suporte_n1\, \suporte_n2\')

with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')
