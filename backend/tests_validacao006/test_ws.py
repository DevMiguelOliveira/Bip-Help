import asyncio, json, sys, time
import requests
import websockets

BASE = "http://127.0.0.1:8001"
WSBASE = "ws://127.0.0.1:8001"
ORIGIN = "http://localhost:5173"
PW = "senha_teste123"
EMAIL = {
    "admin": "admin@biphelp.com",
    "suporte1": "suporte1@biphelp.com",
    "suporte2": "suporte2@biphelp.com",
    "franA": "funcionario.a@biphelp.com",
    "franB": "funcionario.b@biphelp.com",
}
RESULT = []

def check(n, ok, d=""):
    RESULT.append((n, bool(ok), str(d)))
    print(("[OK]  " if ok else "[FAIL] ") + n + ((" :: " + str(d)) if d else ""))

def login(k):
    r = requests.post(BASE + "/auth/login", data={"username": EMAIL[k], "password": PW}, timeout=20)
    r.raise_for_status()
    d = r.json()
    return d.get("access_token") or d.get("token")

TOK = {k: login(k) for k in EMAIL}
def H(k):
    return {"Authorization": "Bearer " + TOK[k]}

def ws_token(k, tid):
    r = requests.post(BASE + "/tickets/%d/ws-token" % tid, headers=H(k), timeout=20)
    return (r.json().get("token") if r.status_code == 200 else None), r.status_code

def enviar(k, tid, texto, interna=False):
    return requests.post(BASE + "/tickets/%d/mensagens/" % tid, headers=H(k),
                         data={"texto": texto, "interna": "true" if interna else "false"}, timeout=25)

async def connect(tid, tok, origin=ORIGIN, send_auth=True):
    ws = await websockets.connect(WSBASE + "/ws/tickets/%d" % tid, additional_headers={"Origin": origin} if origin else {})
    if send_auth:
        await ws.send(json.dumps({"type": "authenticate", "token": tok}))
    return ws

async def drain(ws, timeout=3.0):
    out = []
    try:
        while True:
            m = await asyncio.wait_for(ws.recv(), timeout=timeout)
            out.append(json.loads(m))
    except asyncio.TimeoutError:
        pass
    except Exception:
        pass
    return out

async def main():
    print("=== HANDSHAKE E AUTENTICACAO ===")
    t1, _ = ws_token("suporte1", 1)
    t2, _ = ws_token("franA", 1)

    async def expect_reject(name, coro_factory):
        """Conecta, tenta autenticar e exige que o servidor feche a conexao."""
        try:
            ws = await coro_factory()
        except websockets.ConnectionClosed as cc:
            check(name, True, "handshake recusado status=%s" % cc.rcvd.code if cc.rcvd else cc)
            return
        except Exception as ex:
            check(name, True, "recusado %s: %s" % (type(ex).__name__, str(ex)[:60]))
            return
        try:
            await ws.send(json.dumps({"type": "authenticate", "token": TOK_PLACEHOLDER}))
        except Exception:
            pass
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=4)
            check(name, False, "NAO rejeitado, recebeu: %s" % str(msg)[:80])
        except websockets.ConnectionClosed as cc:
            check(name, True, "fechado code=%s reason=%s" % (cc.rcvd.code, (cc.rcvd.reason or "")[:40]))
        except asyncio.TimeoutError:
            check(name, False, "conexao permaneceu aberta (TIMEOUT)")
        finally:
            try:
                await ws.close()
            except Exception:
                pass

    TOK_PLACEHOLDER = t1

    # Sem Origin -> deve ser rejeitado
    await expect_reject("WS sem Origin rejeitado",
        lambda: websockets.connect(WSBASE + "/ws/tickets/1", additional_headers={}))

    # Origin invalida -> rejeitado
    await expect_reject("WS com Origin invalida rejeitado",
        lambda: websockets.connect(WSBASE + "/ws/tickets/1", additional_headers={"Origin": "http://evil.example"}))

    # Token invalido -> rejeitado
    await expect_reject("WS token invalido rejeitado",
        lambda: connect(1, "nao.e.um.token.valido"))

    # Token de outro ticket -> rejeitado
    tb2, _ = ws_token("franB", 2)
    await expect_reject("WS token de outro ticket rejeitado",
        lambda: connect(1, tb2))

    # Franquia B tentando ticket 1 sem permissao de token
    try:
        r = requests.post(BASE + "/tickets/1/ws-token", headers=H("franB"), timeout=20)
        check("ws-token franquia B no ticket A negado", r.status_code in (403, 404), r.status_code)
    except Exception as ex:
        check("ws-token franquia B no ticket A negado", False, ex)

    # Conexoes legitimas
    ws_sup = await connect(1, t1)
    ws_a = await connect(1, t2)
    hs = await drain(ws_sup, 2)
    ha = await drain(ws_a, 2)
    check("handshake suporte autenticado", any(m.get("type") == "authenticated" for m in hs), hs[:2])
    check("handshake franquia A autenticado", any(m.get("type") == "authenticated" for m in ha), ha[:2])

    print("=== TESTE REAL-TIME: MENSAGEM NORMAL ===")
    uniq = "rt-%s" % str(int(time.time()))[-6:]
    r = enviar("franA", 1, uniq + " normal")
    check("POST mensagem normal franquia A", r.status_code in (200, 201), r.status_code)
    ev_sup = await drain(ws_sup, 3)
    ev_a = await drain(ws_a, 3)
    check("suporte recebeu mensagem em tempo real", any(m.get("type") == "new_message" and uniq in (m.get("texto") or "") for m in ev_sup), ev_sup[:2])
    check("franquia A recebeu mensagem em tempo real", any(m.get("type") == "new_message" and uniq in (m.get("texto") or "") for m in ev_a), ev_a[:2])

    print("=== TESTE REAL-TIME: NOTA INTERNA ===")
    uniq2 = "rti-%s" % str(int(time.time()))[-6:]
    r = enviar("suporte1", 1, uniq2 + " interna", interna=True)
    check("POST nota interna suporte", r.status_code in (200, 201) and r.json().get("interna") is True, r.status_code)
    ev_sup = await drain(ws_sup, 3)
    ev_a = await drain(ws_a, 3)
    check("suporte RECEBEU nota interna no WS", any(m.get("type") == "new_message" and m.get("interna") is True and uniq2 in (m.get("texto") or "") for m in ev_sup), ev_sup[:3])
    check("franquia A NAO recebeu nota interna no WS", not any(uniq2 in json.dumps(m) for m in ev_a), ev_a[:3])

    print("=== ISOLAMENTO ENTRE FRANQUIAS (WS) ===")
    tb2b, _ = ws_token("franB", 2)
    ws_b = await connect(2, tb2b)
    hb = await drain(ws_b, 2)
    check("franquia B autenticada no seu ticket", any(m.get("type") == "authenticated" for m in hb), hb[:2])
    uniq3 = "iso-%s" % str(int(time.time()))[-5:]
    enviar("franB", 2, uniq3 + " de B")
    ev_sup = await drain(ws_sup, 3)
    ev_b = await drain(ws_b, 3)
    check("suporte recebeu mensagem do ticket B", any(uniq3 in json.dumps(m) for m in ev_sup), ev_sup[:2])
    check("franquia A nao recebe nada do ticket B", not any(uniq3 in json.dumps(m) for m in ev_a), ev_a[:2])
    r = requests.get(BASE + "/tickets/2/mensagens/", headers=H("franA"), timeout=20)
    check("franquia A nao le historico do ticket B", r.status_code in (403, 404), r.status_code)

    print("=== PING/PONG ===")
    await ws_sup.send("ping")
    pp = await drain(ws_sup, 2)
    check("ping responde pong", any(m.get("type") == "pong" for m in pp), pp[:2])

    print("=== RECONEXAO SEM VAZAMENTO ===")
    await ws_a.close()
    await asyncio.sleep(1.0)
    uniq4 = "rec-%s" % str(int(time.time()))[-5:]
    enviar("suporte1", 1, uniq4 + " pos-reconexao")
    ev_sup = await drain(ws_sup, 3)
    check("mensagem pos-desconexao entregue ao suporte", any(uniq4 in json.dumps(m) for m in ev_sup), ev_sup[:2])
    t2b, _ = ws_token("franA", 1)
    ws_a2 = await connect(1, t2b)
    ha2 = await drain(ws_a2, 2)
    check("franquia A reconectou", any(m.get("type") == "authenticated" for m in ha2), ha2[:2])
    hist_a = requests.get(BASE + "/tickets/1/mensagens/", headers=H("franA"), timeout=20).json()
    check("historico pos-reconexao sem internas para franquia A", all(not m.get("interna") for m in hist_a), "total=%d" % len(hist_a))
    ev_a2 = await drain(ws_a2, 3)
    check("franquia A nao recebeu notas internas antigas no WS apos reconexao", not any(m.get("interna") for m in ev_a2), ev_a2[:3])

    print("=== ANEXO ===")
    imagembytes = bytes.fromhex("89504e470d0a1a0a") + b"\x00" * 200
    r = requests.post(BASE + "/tickets/1/mensagens/", headers=H("franA"),
                      data={"texto": "anexo teste"}, files={"file": ("t.png", imagembytes, "image/png")}, timeout=25)
    check("envio com anexo (franquia A)", r.status_code in (200, 201) and r.json().get("url_anexo"), "%s %s" % (r.status_code, (r.json().get("url_anexo") if r.status_code in (200,201) else r.text[:120])))
    if r.status_code in (200, 201):
        url = r.json()["url_anexo"]
        ev_sup = await drain(ws_sup, 3)
        check("suporte recebeu anexo em tempo real", any(m.get("url_anexo") == url for m in ev_sup), ev_sup[:2])
        g = requests.get(BASE + url, headers=H("suporte1"), timeout=20)
        check("suporte baixa anexo", g.status_code == 200, g.status_code)
        g2 = requests.get(BASE + url, timeout=20)
        check("anexo exige autenticacao", g2.status_code in (401, 403), g2.status_code)

    for w in (ws_sup, ws_a2, ws_b):
        try:
            await w.close()
        except Exception:
            pass

    ok = sum(1 for _, o, _ in RESULT if o)
    print("WS aprovados=%d reprovados=%d" % (ok, len(RESULT) - ok))
    json.dump([{"teste": n, "ok": o, "detalhe": d} for n, o, d in RESULT],
              open(r"D:\PROJETOS\BipHelp\backend\tests_validacao006\ws_results.json", "w"), indent=2, ensure_ascii=False)

asyncio.run(main())



