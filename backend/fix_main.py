with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    return (
        db.query(models.Mensagem)
        .filter(models.Mensagem.ticket_id == ticket_id)
        .order_by(models.Mensagem.id.asc())
        .all()
    )'''

new = '''    equipe_suporte = current_user.perfil_sistema in (
        "administrador",
        "suporte_n1",
        "suporte_n2",
    )

    query = db.query(models.Mensagem).filter(
        models.Mensagem.ticket_id == ticket_id
    )

    if not equipe_suporte:
        query = query.filter(models.Mensagem.interna == False)

    return query.order_by(models.Mensagem.id.asc()).all()'''

if old in content:
    content = content.replace(old, new, 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Arquivo atualizado com sucesso.')
else:
    print('Trecho não encontrado.')
