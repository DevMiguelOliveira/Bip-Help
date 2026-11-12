import asyncio, json, time
import requests, websockets

BASE="http://127.0.0.1:8001"; WS="ws://127.0.0.1:8001"
ORIGIN="http://localhost:5173"; PW="senha_teste123"
EMAIL={"admin":"admin@biphelp.com","suporte1":"suporte1@biphelp.com","suporte2":"suporte2@biphelp.com",
       "franA":"funcionario.a@biphelp.com","franB":"funcionario.b@biphelp.com"}
R=[]
def check(n, ok, d=""):
    R.append((n,bool(ok),str(d)))
    print(("[OK]  " if ok else "[FAIL] ")+n+((" :: "+str(d)) if d else ""))
def login(k):
    r=requests.post(BASE+"/auth/login", data={"username":EMAIL[k],"password":PW}, timeout=20)
    r.raise_for_status(); d=r.json(); return d.get("access_token") or d.get("token")
TOK={k:login(k) for k in EMAIL}
def H(k): return {"Authorization":"Bearer "+TOK[k]}
def wt(k,t):
    r=requests.post(BASE+"/tickets/%d/ws-token"%t, headers=H(k), timeout=20)
    return (r.json().get("token") if r.status_code==200 else None), r.status_code
def send(k,t,txt,intr=False):
    return requests.post(BASE+"/tickets/%d/mensagens/"%t, headers=H(k),
        data={"texto":txt,"interna":"true" if intr else "false"}, timeout=25)
async def conn(t,tok):
    ws=await websockets.connect(WS+"/ws/tickets/%d"%t, additional_headers={"Origin":ORIGIN})
    await ws.send(json.dumps({"type":"authenticate","token":tok})); return ws
async def drain(ws,to=2.5):
    out=[]
    try:
        while True:
            out.append(json.loads(await asyncio.wait_for(ws.recv(),timeout=to)))
    except asyncio.TimeoutError: pass
    except Exception: pass
    return out


async def main():
    t1,_=wt("suporte1",1)
    print("=== ITEM 1: ORIGIN DO HANDSHAKE ===")
    for nm,hdr in [("sem Origin",{}),("Origin invalida",{"Origin":"http://atacante.example"})]:
        try:
            ws=await websockets.connect(WS+"/ws/tickets/1", additional_headers=hdr)
            await ws.send(json.dumps({"type":"authenticate","token":t1}))
            m=await asyncio.wait_for(ws.recv(),timeout=4)
            check("WS "+nm+" rejeitado", False, "conectou")
            await ws.close()
        except websockets.ConnectionClosed as cc:
            check("WS "+nm+" rejeitado", True, "code=%s"%cc.rcvd.code)
        except Exception as ex:
            check("WS "+nm+" rejeitado", True, type(ex).__name__)

    print("=== ITEM 2: TOKEN DE OUTRO TICKET ===")
    tb,_=wt("franB",2)
    try:
        ws=await conn(1,tb); m=await asyncio.wait_for(ws.recv(),timeout=4)
        check("token ticket B no ticket A rejeitado", False, "conectou"); await ws.close()
    except Exception as ex: check("token ticket B no ticket A rejeitado", True, type(ex).__name__)

    print("=== ITEM 3: FRANQUIA NAO CRIA NOTA INTERNA ===")
    r=send("franA",1,"nao pode")
    check("franquia A mensagem normal permitida", r.status_code==201, r.status_code)
    r=send("franA",1,"nao pode",True)
    check("franquia A nota interna 403", r.status_code==403, r.status_code)

    print("=== ITEM 4: NAO RECEBE EVENTOS DO TICKET B ===")
    ta,_=wt("franA",1); ws_a=await conn(1,ta); ws_s=await conn(1,t1)
    await drain(ws_a,1.2); await drain(ws_s,1.2)
    u="e2e-%s"%str(int(time.time()))[-5:]
    send("franB",2,u+" de B")
    ev_a=await drain(ws_a,2.5); ev_s=await drain(ws_s,2.5)
    check("franquia A nao recebe ticket B (WS)", not any(u in json.dumps(m) for m in ev_a), ev_a[:2])
    check("suporte no ticket 1 nao recebe ticket B (escopo)", not any(u in json.dumps(m) for m in ev_s), ev_s[:2])
    r=requests.get(BASE+"/tickets/2/mensagens/", headers=H("franA"), timeout=20)
    check("franquia A nao le ticket B (HTTP)", r.status_code in (403,404), r.status_code)

    print("=== ITEM 5: NOTA INTERNA SO PARA SUPORTE ===")
    u2="e2i-%s"%str(int(time.time()))[-4:]
    r=send("suporte1",1,u2+" interna",True)
    check("suporte cria nota interna", r.status_code in (200,201) and r.json().get("interna"), r.status_code)
    ev_s=await drain(ws_s,2.5); ev_a=await drain(ws_a,2.5)
    check("suporte recebe nota (WS)", any(u2 in json.dumps(m) for m in ev_s), ev_s[:2])
    check("franquia A nao recebe nota (WS)", not any(u2 in json.dumps(m) for m in ev_a), ev_a[:2])
    hist=requests.get(BASE+"/tickets/1/mensagens/", headers=H("franA"), timeout=20).json()
    check("franquia A historico sem internas", all(not m.get("interna") for m in hist), "total=%d"%len(hist))
    hist_s=requests.get(BASE+"/tickets/1/mensagens/", headers=H("suporte2"), timeout=20).json()
    check("suporte2 historico com internas", any(m.get("interna") for m in hist_s), "total=%d"%len(hist_s))

    print("=== ITEM 6: MENSAGEM NORMAL TEMPO REAL ===")
    u3="e2n-%s"%str(int(time.time()))[-4:]
    r=send("franA",1,u3+" normal")
    check("POST mensagem normal", r.status_code==201, r.status_code)
    ev_s=await drain(ws_s,2.5); ev_a=await drain(ws_a,2.5)
    check("suporte recebe normal (WS)", any(u3 in json.dumps(m) for m in ev_s), ev_s[:2])
    check("franquia A recebe normal (WS)", any(u3 in json.dumps(m) for m in ev_a), ev_a[:2])
    ev_s2=await drain(ws_s,2.5); ev_a2=await drain(ws_a,2.5)
    dup_s=[m for m in ev_s if u3 in json.dumps(m)]; dup_a=[m for m in ev_a if u3 in json.dumps(m)]
    check("sem duplicacao (suporte)", len(dup_s)==1, len(dup_s))
    check("sem duplicacao (franquia)", len(dup_a)==1, len(dup_a))

    print("=== ITEM 7: ANEXO ===")
    img=bytes.fromhex("89504e470d0a1a0a")+b"\x00"*300
    r=requests.post(BASE+"/tickets/1/mensagens/", headers=H("franA"), data={"texto":"anexo e2e"},
                    files={"file":("a.png",img,"image/png")}, timeout=25)
    check("envio com anexo", r.status_code==201 and r.json().get("url_anexo"), "%s %s"%(r.status_code,(r.json().get("url_anexo") or "")[:40]))
    if r.status_code==201:
        url=r.json()["url_anexo"]
        ev=await drain(ws_s,2.5)
        check("anexo transmitido (WS)", any(m.get("url_anexo")==url for m in ev), ev[:1])
        g=requests.get(BASE+url, headers=H("franA"), timeout=20)
        check("franquia baixa anexo autenticada", g.status_code==200, g.status_code)
        g2=requests.get(BASE+url, timeout=20)
        check("anexo exige auth", g2.status_code in (401,403), g2.status_code)

    print("=== ITEM 8: RECONEXAO ===")
    await ws_a.close(); await asyncio.sleep(0.8)
    u4="rec2-%s"%str(int(time.time()))[-4:]
    send("suporte1",1,u4+" pos-desc")
    ev_s=await drain(ws_s,2.5)
    check("mensagem entregue apos desconexao", any(u4 in json.dumps(m) for m in ev_s), ev_s[:1])
    ta2,_=wt("franA",1); ws_a2=await conn(1,ta2); ha=await drain(ws_a2,2)
    check("franquia reconecta", any(m.get("type")=="authenticated" for m in ha), ha[:1])
    ev_a2=await drain(ws_a2,3)
    check("reconexao sem vazamento de internas", not any(m.get("interna") for m in ev_a2), ev_a2[:2])

    print("=== ITEM 9: PING ===")
    await ws_s.send("ping"); pp=await drain(ws_s,2)
    check("ping/pong", any(m.get("type")=="pong" for m in pp), pp[:1])

    print("=== ITEM 10: SEM TOKEN NO HANDSHAKE ===")
    try:
        ws=await websockets.connect(WS+"/ws/tickets/1", additional_headers={"Origin":ORIGIN})
        await ws.send(json.dumps({"type":"authenticate"}))
        m=await asyncio.wait_for(ws.recv(),timeout=4)
        check("handshake sem token rejeitado", False, "conectou"); await ws.close()
    except websockets.ConnectionClosed as cc: check("handshake sem token rejeitado", True, "code=%s"%cc.rcvd.code)
    except Exception as ex: check("handshake sem token rejeitado", True, type(ex).__name__)

    for w in (ws_s, ws_a2):
        try: await w.close()
        except Exception: pass
    ok=sum(1 for _,o,_ in R if o)
    print("\nE2E aprovados=%d reprovados=%d total=%d"%(ok,len(R)-ok,len(R)))
    json.dump([{"teste":n,"ok":o,"detalhe":d} for n,o,d in R], open(r"D:\PROJETOS\BipHelp\backend\tests_validacao006\e2e_results.json","w"), indent=2, ensure_ascii=False)

asyncio.run(main())
