import asyncio, json
import requests, websockets
BASE="http://127.0.0.1:8001"; WS="ws://127.0.0.1:8001"; ORIGIN="http://localhost:5173"
r=requests.post(BASE+"/auth/login", data={"username":"funcionario.a@biphelp.com","password":"senha_teste123"}, timeout=20)
print("LOGIN usuario inativo -> status", r.status_code, "(esperado 401/403)")
print("  resposta:", r.text[:100].replace("\n"," "))
ts=requests.post(BASE+"/auth/login", data={"username":"suporte1@biphelp.com","password":"senha_teste123"}, timeout=20).json()
tok=ts.get("access_token") or ts.get("token")
# token de suporte para ticket 1 continua valido (suporte ativo)
print("suporte ainda autentica:", bool(tok))
async def go():
    try:
        ws=await websockets.connect(WS+"/ws/tickets/1", additional_headers={"Origin":ORIGIN})
        await ws.send(json.dumps({"type":"authenticate","token":"assinatura.invalida.aqui"}))
        try:
            m=await asyncio.wait_for(ws.recv(), timeout=4); print("WS token invalido -> conectou (FALHA):", str(m)[:60])
        except websockets.ConnectionClosed as cc: print("WS token invalido -> fechado code", cc.rcvd.code, "(aprovado)")
    except Exception as ex: print("WS recusado:", type(ex).__name__, str(ex)[:70])
asyncio.run(go())
