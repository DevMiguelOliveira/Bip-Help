with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''      return {
          \
token\: token,
          \token_type\: \websocket\,
          \expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS
      }'''

new = '''      return {
          \token\: token,
          \token_type\: \websocket\,
          \expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS,
          \pode_criar_nota_interna\: pode_criar_nota_interna(current_user)
      }'''

content = content.replace(old, new)

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
