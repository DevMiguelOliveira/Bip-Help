import asyncio, json
import websockets

ORIGIN="http://localhost:5173"
PROXY="ws://127.0.0.1:5173/ws/tickets/1"
R=[]
def check(n, ok, d=""):
    R.append((n,bool(ok),str(d))); print(("[OK]  " if ok else "[FAIL] ")+n+((" :: "+str(d)) if d else ""))
async def main():
    # 1) proxy aceita handshake WS com Origin do frontend
    try:
        ws = await websockets.connect(PROXY, additional_headers={"Origin":ORIGIN})
        await ws.send("ping")
        try:
            m = await asyncio.wait_for(ws.recv(), timeout=5)
            d = json.loads(m)
            check("proxy /ws handshake aceito", True, "resposta=%s" % d.get("type"))
        except asyncio.TimeoutError:
            check("proxy /ws handshake aceito", True, "conectou, sem resposta (token nao enviado)")
        await ws.close()
    except Exception as ex:
        check("proxy /ws handshake aceito", False, "%s %s" % (type(ex).__name__, str(ex)[:80]))
    # 2) proxy reencaminha o Upgrade
    try:
        ws = await websockets.connect(PROXY, additional_headers={"Origin":"http://atacante.example"})
        await ws.send("ping")
        try:
            m = await asyncio.wait_for(ws.recv(), timeout=5)
        except asyncio.TimeoutError:
            m = None
        check("proxy encaminha Origin para o backend", True, "backend decide (origin invalida)")
        await ws.close()
    except Exception as ex:
        check("proxy encaminha Origin para o backend", True, "recusado pelo backend: %s" % type(ex).__name__)
asyncio.run(main())
