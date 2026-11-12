import asyncio
import websockets
import json
import requests

BASE_URL = 'http://127.0.0.1:8000'
SENHA = 'senha_teste123'

def login(email):
    r = requests.post(f'{BASE_URL}/auth/login', data={'username': email, 'password': SENHA})
    return r.json().get('access_token') if r.status_code == 200 else None

def get_ws_token(email, ticket_id):
    token = login(email)
    r = requests.post(f'{BASE_URL}/tickets/{ticket_id}/ws-token', headers={'Authorization': f'Bearer {token}'})
    return r.json() if r.status_code == 200 else None

async def test_websocket():
    print('=== TESTE WEBSOCKET: Isolamento de notas internas ===\n')
    
    suporte_token = login('suporte1@biphelp.com')
    func_a_token = login('funcionario.a@biphelp.com')
    func_b_token = login('funcionario.b@biphelp.com')
    
    print(f'Suporte token: OK' if suporte_token else 'Suporte token: FALHA')
    print(f'Func A token: OK' if func_a_token else 'Func A token: FALHA')
    print(f'Func B token: OK' if func_b_token else 'Func B token: FALHA\n')
    
    ws_suporte = get_ws_token('suporte1@biphelp.com', 1)
    ws_func_a = get_ws_token('funcionario.a@biphelp.com', 1)
    ws_func_b = get_ws_token('funcionario.b@biphelp.com', 1)
    
    print(f'WS Suporte pode_criar_nota_interna: {ws_suporte.get("pode_criar_nota_interna") if ws_suporte else "N/A"}')
    print(f'WS Func A pode_criar_nota_interna: {ws_func_a.get("pode_criar_nota_interna") if ws_func_a else "N/A"}')
    print(f'WS Func B pode_criar_nota_interna: {ws_func_b.get("pode_criar_nota_interna") if ws_func_b else "N/A"}\n')
    
    if not all([ws_suporte, ws_func_a, ws_func_b]):
        print('FALHA: Nao foi possivel obter todos os tokens WebSocket')
        return
    
    messages_received = {
        'suporte': [],
        'func_a': [],
        'func_b': [],
    }
    
    async def listen(name, ws_token):
        uri = 'ws://127.0.0.1:8000/ws/tickets/1'
        try:
            async with websockets.connect(uri) as ws:
                await ws.send(json.dumps({'type': 'authenticate', 'token': ws_token['token']}))
                response = await asyncio.wait_for(ws.recv(), timeout=3)
                data = json.loads(response)
                print(f'  {name}: autenticado - {data.get("type")}')
                
                try:
                    while True:
                        msg = await asyncio.wait_for(ws.recv(), timeout=3)
                        data = json.loads(msg)
                        messages_received[name].append(data)
                        print(f'  {name}: recebeu {data.get("type")} - interna={data.get("interna")}')
                except asyncio.TimeoutError:
                    pass
        except Exception as e:
            print(f'  {name}: erro - {e}')
    
    await asyncio.gather(
        listen('suporte', ws_suporte),
        listen('func_a', ws_func_a),
        listen('func_b', ws_func_b),
    )
    
    print(f'\n=== RESUMO WEBSOCKET ===')
    print(f'Suporte recebeu {len(messages_received["suporte"])} mensagem(ns)')
    print(f'Func A recebeu {len(messages_received["func_a"])} mensagem(ns)')
    print(f'Func B recebeu {len(messages_received["func_b"])} mensagem(ns)')

asyncio.run(test_websocket())
