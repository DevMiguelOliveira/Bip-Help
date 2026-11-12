with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    if not (texto and texto.strip()) and file is None:'''

new = '''    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    papel = verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    equipe_suporte = papel in (\
administrador\, \suporte_n1\, \suporte_n2\)

    if interna and not equipe_suporte:
        raise HTTPException(
            status_code=403,
            detail=\Apenas
a
equipe
de
suporte
pode
criar
notas
internas.\
        )

    if not (texto and texto.strip()) and file is None:'''

content = content.replace(old, new)
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
