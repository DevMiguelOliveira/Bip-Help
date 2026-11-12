import asyncio, json, time
import requests, websockets

API="http://127.0.0.1:5173"      # proxy Vite (como o navegador)
WSP="ws://127.0.0.1:5173/ws/tickets/"
ORIGIN="http://localhost:5173"
PW="senha_teste123"
R=[]
def check(n, ok, d=""):
    R.append((n,bool(ok),str(d))); print(("[OK]  " if ok else "[FAIL] ")+n+((" :: "+str(d)) if d else ""))
def login(e):
    r=requests.post(API+"/auth/login", data={"username":e,"password":PW}, timeout=20)
    r.raise_for_status(); d=r.json(); return d.get("access_token") or d.get("token")
def H(t): return {"Authorization":"Bearer "+t}
def wt(t,tid):
    r=requests.post(API+"/tickets/%d/ws-token"%tid, headers=H(t), timeout=20)
    return (r.json().get("token") if r.status_code==200 else None), r.status_code
def send(t,tid,txt,intr=False):
    return requests.post(API+"/tickets/%d/mensagens/"%tid, headers=H(t),
        data={"texto":txt,"interna":"true" if intr else "false"}, timeout=25)
async def conn(tid, tok):
    ws=await websockets.connect(WSP+str(tid), additional_headers={"Origin":ORIGIN})
    await ws.send(json.dumps({"type":"authenticate","token":tok})); return ws
async def drain(ws,to=2.5):
    out=[]
    try:
        while True: out.append(json.loads(await asyncio.wait_for(ws.recv(),timeout=to)))
    except asyncio.TimeoutError: pass
    except Exception: pass
    return out

async def main():
    ts=login("suporte1@biphelp.com"); ta=login("funcionario.a@biphelp.com")
    tks,_=wt(ts,1); tka,_=wt(ta,1)
    print("=== FLUXO COMPLETO VIA PROXY VITE (igual ao navegador) ===")
    check("login via proxy", bool(ts and ta))
    ws_s=await conn(1,tks); ws_a=await conn(1,tka)
    hev=await drain(ws_s,2.5); aev=await drain(ws_a,2.5)
    check("WS suporte via proxy", any(m.get("type")=="authenticated" for m in hev), hev[:1])
    check("WS franquia via proxy", any(m.get("type")=="authenticated" for m in aev), aev[:1])
    u="px-%s"%str(int(time.time()))[-5:]
    r=send(ta,1,u+" normal")
    check("POST via proxy", r.status_code==201, r.status_code)
    sev=await drain(ws_s,2.5); aev=await drain(ws_a,2.5)
    check("suporte recebe via proxy WS", any(u in json.dumps(m) for m in sev), sev[:1])
    check("franquia recebe via proxy WS", any(u in json.dumps(m) for m in aev), aev[:1])
    u2="pxi-%s"%str(int(time.time()))[-4:]
    r=send(ts,1,u2+" interna", True)
    check("nota interna via proxy", r.status_code==201 and r.json().get("interna"), r.status_code)
    sev=await drain(ws_s,2.5); aev=await drain(ws_a,2.5)
    check("suporte recebe nota via proxy", any(u2 in json.dumps(m) for m in sev), sev[:1])
    check("franquia NAO recebe nota via proxy", not any(u2 in json.dumps(m) for m in aev), aev[:1])
    # anexo via proxy
    img=bytes.fromhex("89504e470d0a1a0a")+b"\x00"*200
    r=requests.post(API+"/tickets/1/mensagens/", headers=H(ta), data={"texto":"anexo proxy"},
                    files={"file":("p.png",img,"image/png")}, timeout=25)
    check("anexo via proxy", r.status_code==201 and r.json().get("url_anexo"), r.status_code)
    if r.status_code==201:
        url=r.json()["url_anexo"]
        g=requests.get(API+url, headers=H(ta), timeout=20)
        check("download anexo via proxy", g.status_code==200, g.status_code)
    hist=requests.get(API+"/tickets/1/mensagens/", headers=H(ta), timeout=20).json()
    check("historico via proxy sem internas p/ franquia", all(not m.get("interna") for m in hist), "total=%d"%len(hist))
    for w in (ws_s, ws_a):
        try: await w.close()
        except Exception: pass
    ok=sum(1 for _,o,_ in R if o)
    print("PROXY aprovados=%d reprovados=%d total=%d"%(ok,len(R)-ok,len(R)))
asyncio.run(main())
