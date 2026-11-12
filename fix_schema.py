with open(r'D:\PROJETOS\BipHelp\backend\schemas.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('expires_in: int', 'expires_in: int\n    pode_criar_nota_interna: bool = False')
with open(r'D:\PROJETOS\BipHelp\backend\schemas.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
