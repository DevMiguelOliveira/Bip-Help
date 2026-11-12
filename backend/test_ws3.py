import asyncio
import websockets
import json
import requests
import threading
import time

BASE_URL = 'http://127.0.0.1:8000'
WS_URL = 'ws://127.0.0.1:8000'
SENHA = 'senha_teste123'

def login(email):
    r = requests.post(f'{BASE_URL}/auth/login', data={'username': email, 'password': SENHA})
    return r.json().get('access_token') if r.status_code == 200 else None

def get_ws_token(email, ticket_id):
    token = login(email)
    r = requests.post(f'{BASE_URL}/tickets/{ticket_id}/ws-token', headers={'Authorization': f'Bearer {token}'})
    return r.json() if r.status_code == 200 else None

def create_internal_note(token, ticket_id, texto):
    r = requests.post(f'{BASE_URL}/tickets/{ticket_id}/mensagens/', 
        headers={'Authorization': f'Bearer {token}'},
        data={'texto': texto, 'interna': 'true'})
    return r.status_code, r.json() if r.status_code == 201 else r.text

results = {'suporte': [], 'func_a': [], 'suporte_raw': []}
suporte_token = None

async def listen(name, ws_token, ticket_id):
    uri = f'{WS_URL}/ws/tickets/{ticket_id}'
    try:
        async with websockets.connect(uri) as ws:
            # Enviar mensagem de handshake com origem simulada
            await ws.send(json.dumps({'type': 'authenticate', 'token': ws_token['token']}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)
            if data.get('type') != 'authenticated':
                print(f'  {name}: autenticacao falhou - {data}')
                return
            print(f'  {name}: autenticado com sucesso')
            
            results[name] = []
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(msg)
                    results[name].append(data)
                    results[name + '_raw'].append(data)
                    print(f'  {name}: recebeu {data.get("type")} - interna={data.get("interna")} - texto={str(data.get("texto"))[:50]}')
            except asyncio.TimeoutError:
                pass
    except Exception as e:
        print(f'  {name}: erro - {e}')

def create_note_in_thread():
    time.sleep(2)
    print('\n--- CRIANDO NOTA INTERNA via API (suporte) ---')
    status, resp = create_internal_note(suporte_token, 1, 'Nota interna de teste - validacao WS')
    print(f'  Status: {status}')
    if status == 201:
        print(f'  Mensagem criada com id: {resp.get("id")}')

async def main():
    global suporte_token
    
    print('=== TESTE WEBSOCKET: SEGURANCA PONTA A PONTE ===\n')
    
    suporte_token = login('suporte1@biphelp.com')
    func_a_token = login('funcionario.a@biphelp.com')
    
    ws_suporte = get_ws_token('suporte1@biphelp.com', 1)
    ws_func_a = get_ws_token('funcionario.a@biphelp.com', 1)
    
    print(f'WS Suporte pode_criar_nota_interna: {ws_suporte.get("pode_criar_nota_interna") if ws_suporte else "N/A"}')
    print(f'WS Func A pode_criar_nota_interna: {ws_func_a.get("pode_criar_nota_interna") if ws_func_a else "N/A"}\n')
    
    if not ws_suporte or not ws_func_a:
        print('FALHA: Nao foi possivel obter tokens WebSocket')
        return
    
    # Iniciar thread para criar nota
    t = threading.Thread(target=create_note_in_thread, daemon=True)
    t.start()
    
    # Conectar WS simultaneamente
    await asyncio.gather(
        listen('suporte', ws_suporte, 1),
        listen('func_a', ws_func_a, 1),
    )
    
    print(f'\n=== RESULTADO WS ===')
    print(f'Suporte recebeu {len(results["suporte"])} mensagem(s)')
    print(f'Func A recebeu {len(results["func_a"])} mensagem(s)')
    
    suporte_internas = [m for m in results['suporte'] if m.get('interna') == True]
    func_a_internas = [m for m in results['func_a'] if m.get('interna') == True]
    
    print(f'\nSuporte recebeu {len(suporte_internas)} nota(s) interna(s)')
    print(f'Func A recebeu {len(func_a_internas)} nota(s) interna(s)')
    
    if len(suporte_internas) >= 1 and len(func_a_internas) == 0:
        print('\n[APROVADO] ISOLAMENTO WS: Nota interna somente para suporte')
    else:
        print('\n[FALHA] SEGURANCA: Funcionario recebeu nota interna!')

asyncio.run(main())
