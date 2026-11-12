with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Use raw string to avoid escaping issues
old = r'return {' + chr(10) + r'        "token": token,' + chr(10) + r'        "token_type": "websocket",' + chr(10) + r'        "expires_in": WEBSOCKET_TOKEN_EXPIRE_SECONDS' + chr(10) + r'    }'

new = r'return {' + chr(10) + r'        "token": token,' + chr(10) + r'        "token_type": "websocket",' + chr(10) + r'        "expires_in": WEBSOCKET_TOKEN_EXPIRE_SECONDS,' + chr(10) + r'        "pode_criar_nota_interna": pode_criar_nota_interna(current_user)' + chr(10) + r'    }'

print('Old:', repr(old))
print('In content:', old in content)

content = content.replace(old, new)

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
