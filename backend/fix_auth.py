import sys
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i in range(len(lines)):
    if 'verificar_acesso_ticket(' in lines[i] and 'db,' in lines[i+1] and 'current_user,' in lines[i+2] and 'ticket' in lines[i+3]:
        j = i + 4
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        if 'if not (texto and texto.strip()) and file is None:' in lines[j]:
            start_idx = i
            end_idx = j
            break

if start_idx != -1:
    new_lines = lines[:start_idx+5] + [
        '\n',
        '    papel = verificar_acesso_ticket(\n',
        '        db,\n',
        '        current_user,\n',
        '        ticket\n',
        '    )\n',
        '\n',
        '    equipe_suporte = papel in (\
administrador\, \suporte_n1\, \suporte_n2\)\n',
        '\n',
        '    if interna and not equipe_suporte:\n',
        '        raise HTTPException(\n',
        '            status_code=403,\n',
        '            detail=\Apenas
a
equipe
de
suporte
pode
criar
notas
internas.\\n',
        '        )\n',
        '\n',
    ] + lines[end_idx:]
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Authorization check added at line', start_idx)
else:
    print('Pattern not found')
