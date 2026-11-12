import asyncio
import websockets
import json
import requests
import threading
import time

BASE_URL = 'http://127.0.0.1:8000'
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
    return r.status_code, r.text

results = {'suporte': [], 'func_a': []}

async def listen(name, ws_token):
    uri = 'ws://127.0.0.1:8000/ws/tickets/1'
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({'type': 'authenticate', 'token': ws_token['token']}))
            response = await asyncio.wait_for(ws.recv(), timeout=3)
            data = json.loads(response)
            print(f'  {name}: autenticado')
            
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(msg)
                    results[name].append(data)
                    print(f'  {name}: recebeu {data.get("type")} - interna={data.get("interna")} - texto={data.get("texto")}')
            except asyncio.TimeoutError:
                pass
    except Exception as e:
        print(f'  {name}: erro - {e}')

def create_note_after_delay():
    time.sleep(3)
    print('\n--- Criando nota interna via API (suporte) ---')
    status, texto = create_internal_note(suporte_token, 1, 'Nota interna de teste WS')
    print(f'  Status: {status} - {texto[:200]}')

async def main():
    global suporte_token
    suporte_token = login('suporte1@biphelp.com')
    func_a_token = login('funcionario.a@biphelp.com')
    
    ws_suporte = get_ws_token('suporte1@biphelp.com', 1)
    ws_func_a = get_ws_token('funcionario.a@biphelp.com', 1)
    
    print(f'WS Suporte pode_criar_nota_interna: {ws_suporte.get("pode_criar_nota_interna") if ws_suporte else "N/A"}')
    print(f'WS Func A pode_criar_nota_interna: {ws_func_a.get("pode_criar_nota_interna") if ws_func_a else "N/A"}\n')
    
    # Iniciar criação da nota em thread separada depois de conectar
    t = threading.Thread(target=create_note_after_delay, daemon=True)
    t.start()
    
    await asyncio.gather(
        listen('suporte', ws_suporte),
        listen('func_a', ws_func_a),
    )
    
    print(f'\n=== RESULTADO WEBSOCKET ===')
    print(f'Suporte recebeu {len(results["suporte"])} mensagem(ns)')
    print(f'Func A recebeu {len(results["func_a"])} mensagem(ns)')
    
    # Verificar isolamento
    suporte_internal = [m for m in results['suporte'] if m.get('interna') == True]
    func_a_internal = [m for m in results['func_a'] if m.get('interna') == True]
    
    print(f'\nSuporte recebeu {len(suporte_internal)} nota(s) interna(s)')
    print(f'Func A recebeu {len(func_a_internal)} nota(s) interna(s)')
    
    if len(suporte_internal) >= 1 and len(func_a_internal) == 0:
        print('✅ ISOLAMENTO WEBSOCKET OK: Nota interna so para suporte')
    else:
        print('❌ FALHA DE SEGURANCA: Funcionario recebeu nota interna!')

asyncio.run(main())
