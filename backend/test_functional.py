import requests
import sys

BASE_URL = 'http://127.0.0.1:8000'
SENHA = 'senha_teste123'

def login(email, senha=SENHA):
    r = requests.post(f'{BASE_URL}/auth/login', data={'username': email, 'password': senha})
    print(f'Login {email}: status={r.status_code}', r.text[:200])
    if r.status_code == 200:
        return r.json().get('access_token')
    return None

def test_headers(token):
    return {'Authorization': f'Bearer {token}'}

admin_token = login('admin@biphelp.com')
suporte1_token = login('suporte1@biphelp.com')
suporte2_token = login('suporte2@biphelp.com')
func_a_token = login('funcionario.a@biphelp.com')
func_b_token = login('funcionario.b@biphelp.com')

passou = 0
falhou = 0

def ok(msg):
    global passou
    print(f'  OK: {msg}')
    passou += 1

def fail(msg):
    global falhou
    print(f'  FALHA: {msg}')
    falhou += 1

print()
print('=== TESTE 1: Listagem de tickets por franquia ===')
if func_a_token:
    r = requests.get(f'{BASE_URL}/tickets/', headers=test_headers(func_a_token))
    if r.status_code == 200:
        tickets = r.json()
        print(f'  Funcionario A ve {len(tickets)} ticket(s)')
        ok('Funcionario A lista tickets')
    else:
        print(f'  Erro: {r.status_code} {r.text[:200]}')
        fail('Funcionario A lista tickets')
if func_b_token:
    r = requests.get(f'{BASE_URL}/tickets/', headers=test_headers(func_b_token))
    if r.status_code == 200:
        tickets = r.json()
        print(f'  Funcionario B ve {len(tickets)} ticket(s)')
        ok('Funcionario B lista tickets')
    else:
        print(f'  Erro: {r.status_code} {r.text[:200]}')
        fail('Funcionario B lista tickets')
if admin_token:
    r = requests.get(f'{BASE_URL}/tickets/', headers=test_headers(admin_token))
    if r.status_code == 200:
        tickets = r.json()
        print(f'  Admin ve {len(tickets)} ticket(s)')
        ok('Admin lista tickets')
    else:
        print(f'  Erro: {r.status_code} {r.text[:200]}')
        fail('Admin lista tickets')

print()
print('=== TESTE 2: Isolamento entre franquias ===')
if func_a_token:
    r = requests.get(f'{BASE_URL}/tickets/2', headers=test_headers(func_a_token))
    if r.status_code == 403:
        ok('Func A nao acessa ticket da franquia B (403)')
    else:
        print(f'  Erro: esperado 403, obteve {r.status_code} {r.text[:200]}')
        fail('Func A nao acessa ticket da franquia B')
if func_b_token:
    r = requests.get(f'{BASE_URL}/tickets/1', headers=test_headers(func_b_token))
    if r.status_code == 403:
        ok('Func B nao acessa ticket da franquia A (403)')
    else:
        print(f'  Erro: esperado 403, obteve {r.status_code} {r.text[:200]}')
        fail('Func B nao acessa ticket da franquia A')

print()
print('=== TESTE 3: Mensagens de um ticket (filtrando internas) ===')
if func_a_token:
    r = requests.get(f'{BASE_URL}/tickets/1/mensagens/', headers=test_headers(func_a_token))
    if r.status_code == 200:
        msgs = r.json()
        internas = [m for m in msgs if m.get('interna')]
        normais = [m for m in msgs if not m.get('interna')]
        print(f'  Func A: {len(normais)} normal(ns), {len(internas)} interna(s)')
        if len(internas) == 0:
            ok('Func A nao recebe notas internas')
        else:
            fail('Func A deveria receber 0 notas internas')
    else:
        print(f'  Erro: {r.status_code} {r.text[:200]}')
        fail('Func A lista mensagens ticket 1')

print()
print('=== TESTE 4: Criacao de nota interna por suporte ===')
if suporte1_token:
    r = requests.post(f'{BASE_URL}/tickets/1/mensagens/', headers=test_headers(suporte1_token), data={'texto': 'Nota interna de teste', 'interna': 'true'})
    if r.status_code == 201:
        msg = r.json()
        if msg.get('interna') == True:
            ok('Suporte cria nota interna com interna=true')
        else:
            print(f'  Erro: interna={msg.get("interna")}')
            fail('Suporte cria nota interna com interna=true')
    else:
        print(f'  Erro: {r.status_code} {r.text[:300]}')
        fail('Suporte cria nota interna')

print()
print('=== TESTE 5: Criacao de nota interna por funcionario (deve falhar 403) ===')
if func_a_token:
    r = requests.post(f'{BASE_URL}/tickets/1/mensagens/', headers=test_headers(func_a_token), data={'texto': 'Tentativa interna', 'interna': 'true'})
    if r.status_code == 403:
        ok('Func A bloqueado ao criar nota interna (403)')
    else:
        print(f'  Erro: esperado 403, obteve {r.status_code} {r.text[:300]}')
        fail('Func A bloqueado ao criar nota interna')

print()
print('=== TESTE 6: Mensagens normais continuam funcionando ===')
if func_a_token:
    r = requests.post(f'{BASE_URL}/tickets/1/mensagens/', headers=test_headers(func_a_token), data={'texto': 'Mensagem normal de teste', 'interna': 'false'})
    if r.status_code == 201:
        msg = r.json()
        if msg.get('interna') == False:
            ok('Func A envia mensagem normal com interna=false')
        else:
            print(f'  Erro: interna={msg.get("interna")}')
            fail('Func A envia mensagem normal com interna=false')
    else:
        print(f'  Erro: {r.status_code} {r.text[:300]}')
        fail('Func A envia mensagem normal')

print()
print('=== TESTE 7: Suporte consegue ler nota interna ===')
if suporte1_token:
    r = requests.get(f'{BASE_URL}/tickets/1/mensagens/', headers=test_headers(suporte1_token))
    if r.status_code == 200:
        msgs = r.json()
        internas = [m for m in msgs if m.get('interna')]
        print(f'  Suporte: {len(internas)} nota(s) interna(s) visível(is)')
        if len(internas) >= 1:
            ok('Suporte visualiza notas internas')
        else:
            fail('Suporte deveria visualizar notas internas')
    else:
        print(f'  Erro: {r.status_code} {r.text[:200]}')
        fail('Suporte lista mensagens ticket 1')

print()
print(f'=== RESULTADO: {passou} passou, {falhou} falhou ===')
