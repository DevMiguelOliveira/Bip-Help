with open(r'D:\\PROJETOS\\BipHelp\\backend\\schemas.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'class WebSocketTokenResponse(BaseModel):\n    token: str\n    token_type: Literal["websocket"] = "websocket"\n    expires_in: int'

new = 'class WebSocketTokenResponse(BaseModel):\n    token: str\n    token_type: Literal["websocket"] = "websocket"\n    expires_in: int\n    pode_criar_nota_interna: bool = False'

content = content.replace(old, new)

with open(r'D:\\PROJETOS\\BipHelp\\backend\\schemas.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
