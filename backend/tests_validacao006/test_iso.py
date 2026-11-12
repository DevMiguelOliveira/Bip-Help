import asyncio, json, sys, time
import requests
import websockets

BASE = "http://127.0.0.1:8001"
WSBASE = "ws://127.0.0.1:8001"
ORIGIN = "http://localhost:5173"
PW = "senha_teste123"
EMAIL = {"admin": "admin@biphelp.com", "suporte1": "suporte1@biphelp.com", "franA": "funcionario.a@biphelp.com", "franB": "funcionario.b@biphelp.com"}
RESULT = []
def check(n, ok, d=""):
    RESULT.append((n, bool(ok), str(d)))
    print(("[OK]  " if ok else "[FAIL] ") + n + ((" :: " + str(d)) if d else ""))
def login(k):
    r = requests.post(BASE + "/auth/login", data={"username": EMAIL[k], "password": PW}, timeout=20)
    r.raise_for_status(); d = r.json(); return d.get("access_token") or d.get("token")
TOK = {k: login(k) for k in EMAIL}
def H(k): return {"Authorization": "Bearer " + TOK[k]}
def ws_token(k, tid):
    r = requests.post(BASE + "/tickets/%d/ws-token" % tid, headers=H(k), timeout=20)
    return (r.json().get("token") if r.status_code == 200 else None), r.status_code
def enviar(k, tid, texto, interna=False):
    return requests.post(BASE + "/tickets/%d/mensagens/" % tid, headers=H(k),
                         data={"texto": texto, "interna": "true" if interna else "false"}, timeout=25)
async def connect(tid, tok):
    ws = await websockets.connect(WSBASE + "/ws/tickets/%d" % tid, additional_headers={"Origin": ORIGIN})
    await ws.send(json.dumps({"type": "authenticate", "token": tok}))
    return ws
async def drain(ws, timeout=3.0):
    out = []
    try:
        while True:
            m = await asyncio.wait_for(ws.recv(), timeout=timeout)
            out.append(json.loads(m))
    except asyncio.TimeoutError: pass
    except Exception: pass
    return out

async def main():
    t_sup1, _ = ws_token("suporte1", 1)
    t_sup2, _ = ws_token("suporte1", 2)
    ws_sup_t1 = await connect(1, t_sup1)
    ws_sup_t2 = await connect(2, t_sup2)
    tb, _ = ws_token("franB", 2)
    ws_b = await connect(2, tb)
    await drain(ws_sup_t1, 1.5); await drain(ws_sup_t2, 1.5); await drain(ws_b, 1.5)

    print("=== ISOLAMENTO POR TICKET (broadcast escopado) ===")
    uniq = "iso2-%s" % str(int(time.time()))[-5:]
    r = enviar("franB", 2, uniq + " de B")
    check("POST mensagem franquia B no ticket 2", r.status_code in (200, 201), r.status_code)
    ev1 = await drain(ws_sup_t1, 3)
    ev2 = await drain(ws_sup_t2, 3)
    evb = await drain(ws_b, 3)
    check("suporte no ticket 1 NAO recebe evento do ticket 2 (escopo correto)", not any(uniq in json.dumps(m) for m in ev1), ev1[:2])
    check("suporte no ticket 2 recebe evento do ticket 2", any(uniq in json.dumps(m) for m in ev2), ev2[:2])
    check("franquia B recebe sua propria mensagem", any(uniq in json.dumps(m) for m in evb), evb[:2])

    print("=== NOTA INTERNA NO TICKET 2 ===")
    uniq2 = "iso3-%s" % str(int(time.time()))[-5:]
    enviar("suporte1", 2, uniq2 + " interna B", interna=True)
    ev2b = await drain(ws_sup_t2, 3)
    evb2 = await drain(ws_b, 3)
    check("suporte no ticket 2 recebe nota interna", any(uniq2 in json.dumps(m) for m in ev2b), ev2b[:2])
    check("franquia B NAO recebe nota interna", not any(uniq2 in json.dumps(m) for m in evb2), evb2[:2])
    hist_b = requests.get(BASE + "/tickets/2/mensagens/", headers=H("franB"), timeout=20).json()
    check("franquia B historico sem internas", all(not m.get("interna") for m in hist_b), "total=%d" % len(hist_b))

    print("=== DESATIVACAO DE USUARIO ===")
    r = requests.patch(BASE + "/equipe/4", headers=H("admin"), json={"ativo": False}, timeout=20)
    check("admin desativa franquia A", r.status_code in (200, 204), r.status_code)
    t_a, _ = ws_token("franA", 1)
    try:
        ws = await connect(1, t_a)
        msg = await asyncio.wait_for(ws.recv(), timeout=4)
        check("WS negado apos desativacao", False, "conectou: %s" % str(msg)[:60])
        await ws.close()
    except websockets.ConnectionClosed as cc:
        check("WS negado apos desativacao", True, "fechado code=%s" % cc.rcvd.code)
    except Exception as ex:
        check("WS negado apos desativacao", True, "recusado %s" % type(ex).__name__)
    r2 = requests.get(BASE + "/tickets/1/mensagens/", headers=H("franA"), timeout=20)
    check("HTTP negado apos desativacao", r2.status_code in (401, 403), r2.status_code)
    r3 = requests.patch(BASE + "/equipe/4", headers=H("admin"), json={"ativo": True}, timeout=20)
    check("admin reativa franquia A", r3.status_code in (200, 204), r3.status_code)
    t_a2, _ = ws_token("franA", 1)
    ws_a = await connect(1, t_a2)
    ha = await drain(ws_a, 2)
    check("franquia A volta a conectar", any(m.get("type") == "authenticated" for m in ha), ha[:2])

    for w in (ws_sup_t1, ws_sup_t2, ws_b, ws_a):
        try: await w.close()
        except Exception: pass
    ok = sum(1 for _, o, _ in RESULT if o)
    print("ISO aprovados=%d reprovados=%d total=%d" % (ok, len(RESULT) - ok, len(RESULT)))
    json.dump([{"teste": n, "ok": o, "detalhe": d} for n, o, d in RESULT],
              open(r"D:\PROJETOS\BipHelp\backend\tests_validacao006\iso_results.json", "w"), indent=2, ensure_ascii=False)

asyncio.run(main())

