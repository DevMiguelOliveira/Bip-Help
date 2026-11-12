with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    ticket = obter_ticket(db, ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    return (
        db.query(models.Mensagem)
        .filter(models.Mensagem.ticket_id == ticket_id)
        .order_by(models.Mensagem.id.asc())
        .all()
    )'''

new = '''    ticket = obter_ticket(db, ticket_id)

    papel = verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    consulta = db.query(models.Mensagem).filter(
        models.Mensagem.ticket_id == ticket_id
    )

    if papel not in (\
administrador\, \suporte_n1\, \suporte_n2\):
        consulta = consulta.filter(models.Mensagem.interna.is_(False))

    return (
        consulta
        .order_by(models.Mensagem.id.asc())
        .all()
    )'''

content = content.replace(old, new)

with open('D:\\\\PROJETOS\\\\BipHelp\\\\backend\\\\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Backend patch applied')
