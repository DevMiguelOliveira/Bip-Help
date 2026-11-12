import asyncio, json
import requests, websockets
BASE="http://127.0.0.1:8001"; WS="ws://127.0.0.1:8001"; ORIGIN="http://localhost:5173"; PW="senha_teste123"
def login(e):
    r=requests.post(BASE+"/auth/login", data={"username":e,"password":PW}, timeout=20); r.raise_for_status(); d=r.json(); return d.get("access_token") or d.get("token")
ta=login("funcionario.a@biphelp.com")
r=requests.post(BASE+"/tickets/1/ws-token", headers={"Authorization":"Bearer "+ta}, timeout=20)
print("ws-token usuario inativo:", r.status_code, r.text[:120])
r2=requests.get(BASE+"/tickets/1/mensagens/", headers={"Authorization":"Bearer "+ta}, timeout=20)
print("GET mensagens usuario inativo:", r2.status_code)
rl=requests.post(BASE+"/auth/login", data={"username":"funcionario.a@biphelp.com","password":PW}, timeout=20)
print("login usuario inativo:", rl.status_code)
async def go():
    try:
        ws=await websockets.connect(WS+"/ws/tickets/1", additional_headers={"Origin":ORIGIN})
        await ws.send(json.dumps({"type":"authenticate","token":"token.invalido.qualquer"}))
        try:
            m=await asyncio.wait_for(ws.recv(), timeout=4); print("WS com token invalido: conectou", str(m)[:60])
        except websockets.ConnectionClosed as cc: print("WS token invalido rejeitado code=", cc.rcvd.code)
    except Exception as ex: print("WS recusado:", type(ex).__name__, str(ex)[:60])
asyncio.run(go())
