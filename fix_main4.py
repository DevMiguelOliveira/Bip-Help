with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'return {\n        \
token\: token,\n        \token_type\: \websocket\,\n        \expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS\n    }'

new = 'return {\n        \token\: token,\n        \token_type\: \websocket\,\n        \expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS,\n        \pode_criar_nota_interna\: pode_criar_nota_interna(current_user)\n    }'

content = content.replace(old, new)

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
