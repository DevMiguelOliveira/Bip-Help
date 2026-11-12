with open('D:\\PROJETOS\\BipHelp\\backend\\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_listar = '''@app.get(
    \
/tickets/
ticket_id
/mensagens/\,
    response_model=list[schemas.MensagemResponse]
)
def listar_mensagens(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

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

new_listar = '''@app.get(
    \/tickets/
ticket_id
/mensagens/\,
    response_model=list[schemas.MensagemResponse]
)
def listar_mensagens(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

    papel = verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    consulta = db.query(models.Mensagem).filter(
        models.Mensagem.ticket_id == ticket_id
    )

    if papel not in (\administrador\, \suporte_n1\, \suporte_n2\):
        consulta = consulta.filter(models.Mensagem.interna.is_(False))

    return (
        consulta
        .order_by(models.Mensagem.id.asc())
        .all()
    )'''

content = content.replace(old_listar, new_listar)

with open('D:\\PROJETOS\\BipHelp\\backend\\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Backend patch applied')
