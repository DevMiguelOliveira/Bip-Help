with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the return statement in emitir_token_websocket and add pode_criar_nota_interna
for i, line in enumerate(lines):
    if '\
expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS' in line and i+1 < len(lines) and '}' in lines[i+1]:
        # Insert before the closing brace
        lines[i] = '          \expires_in\: WEBSOCKET_TOKEN_EXPIRE_SECONDS,\n'
        lines.insert(i+1, '          \pode_criar_nota_interna\: pode_criar_nota_interna(current_user)\n')
        break

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')
