import sys
sys.path.insert(0, '.')

from database import SessionLocal
import models

db = SessionLocal()

try:
    franquia_a = models.Franquia(
        nome_responsavel='Joao Silva',
        unidade='Unidade Centro',
        telefone='+5511999990001',
        ativa=True,
    )
    franquia_b = models.Franquia(
        nome_responsavel='Maria Souza',
        unidade='Unidade Norte',
        telefone='+5511999990002',
        ativa=True,
    )
    db.add_all([franquia_a, franquia_b])
    db.flush()

    admin = models.Usuario(
        nome='Administrador Sistema',
        email='admin@biphelp.com',
        senha_hash='senha_placeholder',
        perfil_sistema='administrador',
        ativo=True,
    )
    suporte_n1 = models.Usuario(
        nome='Suporte N1',
        email='suporte1@biphelp.com',
        senha_hash='senha_placeholder',
        perfil_sistema='suporte_n1',
        ativo=True,
    )
    suporte_n2 = models.Usuario(
        nome='Suporte N2',
        email='suporte2@biphelp.com',
        senha_hash='senha_placeholder',
        perfil_sistema='suporte_n2',
        ativo=True,
    )
    func_a = models.Usuario(
        nome='Funcionario Franquia A',
        email='funcionario.a@biphelp.com',
        senha_hash='senha_placeholder',
        perfil_sistema=None,
        ativo=True,
    )
    func_b = models.Usuario(
        nome='Funcionario Franquia B',
        email='funcionario.b@biphelp.com',
        senha_hash='senha_placeholder',
        perfil_sistema=None,
        ativo=True,
    )
    db.add_all([admin, suporte_n1, suporte_n2, func_a, func_b])
    db.flush()

    db.add(models.UsuarioFranquia(usuario_id=func_a.id, franquia_id=franquia_a.id, papel='funcionario', ativo=True))
    db.add(models.UsuarioFranquia(usuario_id=func_b.id, franquia_id=franquia_b.id, papel='funcionario', ativo=True))
    db.flush()

    ticket_a = models.Ticket(franquia_id=franquia_a.id, descricao='Ticket da franquia A', status='Aberto')
    ticket_b = models.Ticket(franquia_id=franquia_b.id, descricao='Ticket da franquia B', status='Aberto')
    db.add_all([ticket_a, ticket_b])
    db.flush()

    m1 = models.Mensagem(ticket_id=ticket_a.id, remetente_id=func_a.id, remetente=func_a.nome, texto='Mensagem normal A', interna=False)
    m2 = models.Mensagem(ticket_id=ticket_a.id, remetente_id=suporte_n1.id, remetente=suporte_n1.nome, texto='Nota interna A', interna=True)
    m3 = models.Mensagem(ticket_id=ticket_b.id, remetente_id=func_b.id, remetente=func_b.nome, texto='Mensagem normal B', interna=False)
    db.add_all([m1, m2, m3])

    db.commit()
    print('Usuarios de teste criados com sucesso.')
    print('Franquia A id=' + str(franquia_a.id) + ', Franquia B id=' + str(franquia_b.id))
    print('Admin id=' + str(admin.id) + ', Suporte1 id=' + str(suporte_n1.id) + ', Suporte2 id=' + str(suporte_n2.id))
    print('Func A id=' + str(func_a.id) + ', Func B id=' + str(func_b.id))
    print('Ticket A id=' + str(ticket_a.id) + ', Ticket B id=' + str(ticket_b.id))
finally:
    db.close()
