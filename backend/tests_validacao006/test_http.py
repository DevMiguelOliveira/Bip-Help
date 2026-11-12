import json, asyncio, uuid, sys, time
import requests
import websockets

BASE = "http://127.0.0.1:8001"
ORIGIN = "http://localhost:5173"
PW = "senha_teste123"
USERS = {
    "admin": "admin@biphelp.com",
    "suporte1": "suporte1@biphelp.com",
    "suporte2": "suporte2@biphelp.com",
    "franA": "funcionario.a@biphelp.com",
    "franB": "funcionario.b@biphelp.com",
}

RESULT = []

def check(name, ok, detail=""):
    RESULT.append((name, bool(ok), str(detail)))
    print(("[OK]  " if ok else "[FAIL] ") + name + ((" :: " + str(detail)) if detail else ""))

def login(email):
    r = requests.post(BASE + "/auth/login", data={"username": email, "password": PW}, timeout=20)
    if r.status_code != 200:
        raise RuntimeError("login falhou %s %s" % (r.status_code, r.text[:200]))
    d = r.json()
    return d.get("access_token") or d.get("token")

def auth(tok):
    return {"Authorization": "Bearer " + tok}

tokens = {}
print("=== LOGIN ===")
for k, e in USERS.items():
    try:
        tokens[k] = login(e)
        check("login " + k, True, e)
    except Exception as ex:
        check("login " + k, False, ex)

print("=== /auth/me ===")
me = {}
for k, t in tokens.items():
    r = requests.get(BASE + "/auth/me", headers=auth(t), timeout=20)
    if r.status_code == 200:
        me[k] = r.json()
        check("me " + k, True, "perfil=%s" % (me[k].get("perfil_sistema")))
    else:
        check("me " + k, False, r.status_code)

print("=== SEM AUTENTICACAO (seguranca HTTP) ===")
r = requests.get(BASE + "/tickets/", timeout=20)
check("GET /tickets sem token bloqueado", r.status_code in (401, 403), r.status_code)
r = requests.get(BASE + "/tickets/1/mensagens/", timeout=20)
check("GET mensagens sem token bloqueado", r.status_code in (401, 403), r.status_code)
r = requests.post(BASE + "/tickets/1/mensagens/", data={"texto": "x"}, timeout=20)
check("POST mensagem sem token bloqueado", r.status_code in (401, 403), r.status_code)
r = requests.get(BASE + "/tickets/", headers=auth("token.invalto.xxx"), timeout=20)
check("token invalido bloqueado", r.status_code in (401, 403), r.status_code)

print("=== LISTAGEM DE TICKETS (isolamento) ===")
def ticket_ids(k):
    r = requests.get(BASE + "/tickets/", headers=auth(tokens[k]), timeout=20)
    if r.status_code != 200:
        return None, r.status_code
    d = r.json()
    itens = d if isinstance(d, list) else d.get("items", d.get("data", []))
    return [int(t["id"]) for t in itis] if False else [int(t["id"]) for t in itens], 200

ta, ca = ticket_ids("franA")
check("franquia A lista tickets", ca == 200, ta)
check("franquia A ve apenas ticket 1", ta == [1], ta)
tb, cb = ticket_ids("franB")
check("franquia B lista tickets", cb == 200, tb)
check("franquia B ve apenas ticket 2", tb == [2], tb)
ts, cs = ticket_ids("suporte1")
check("suporte lista ambos tickets", cs == 200 and set([1, 2]).issubset(set(ts or [])), ts)

print("=== ACESSO CRUZADO DE TICKET (seguranca) ===")
r = requests.get(BASE + "/tickets/2", headers=auth(tokens["franA"]), timeout=20)
check("franquia A nao acessa ticket B", r.status_code in (403, 404), r.status_code)
r = requests.get(BASE + "/tickets/1", headers=auth(tokens["franB"]), timeout=20)
check("franquia B nao acessa ticket A", r.status_code in (403, 404), r.status_code)
r = requests.get(BASE + "/tickets/1/mensagens/", headers=auth(tokens["franB"]), timeout=20)
check("franquia B nao le historico do ticket A", r.status_code in (403, 404), r.status_code)
r = requests.get(BASE + "/tickets/9999/mensagens/", headers=auth(tokens["suporte1"]), timeout=20)
check("ticket inexistente tratado", r.status_code in (403, 404, 405), r.status_code)

print("=== NOTA INTERNA: AUTORIZACAO ===")
r = requests.post(BASE + "/tickets/1/mensagens/", headers=auth(tokens["franA"]),
                  data={"texto": "tentativa franquia", "interna": "true"}, timeout=20)
check("franquia nao cria nota interna", r.status_code == 403, "%s %s" % (r.status_code, r.text[:120]))
r = requests.post(BASE + "/tickets/1/mensagens/", headers=auth(tokens["suporte2"]),
                  data={"texto": "tentativa suporte2", "interna": "true"}, timeout=20)
check("suporte2 cria nota interna", r.status_code in (200, 201), r.status_code)

print("=== HISTORICO COM PERMISSAO ===")
hm = requests.get(BASE + "/tickets/1/mensagens/", headers=auth(tokens["suporte1"]), timeout=20).json()
check("suporte ve internas no historico", any(m.get("interna") for m in hm), "total=%d" % len(hm))
hm2 = requests.get(BASE + "/tickets/1/mensagens/", headers=auth(tokens["franA"]), timeout=20).json()
check("franquia A NAO ve internas no historico", all(not m.get("interna") for m in hm2), "total=%d" % len(hm2))

print("=== WS TOKEN ===")
def ws_token(k, tid):
    r = requests.post(BASE + "/tickets/%d/ws-token" % tid, headers=auth(tokens[k]), timeout=20)
    return (r.json() if r.status_code == 200 else None), r.status_code

(wt_sup, st_sup) = ws_token("suporte1", 1)
check("ws-token suporte ticket 1", st_sup == 200 and wt_sup and "token" in wt_sup, st_sup)
(wt_a, st_a) = ws_token("franA", 1)
check("ws-token franquia A ticket 1", st_a == 200 and wt_a and "token" in wt_a, st_a)
(r_sem, st_sem) = ws_token("franA", 2)
check("ws-token franquia A ticket B negado", st_sem in (403, 404), st_sem)

print("=== RESUMO HTTP ===")
ok = sum(1 for _, o, _ in RESULT if o)
print("HTTP aprovados=%d reprovados=%d" % (ok, len(RESULT) - ok))
json.dump([{"teste": n, "ok": o, "detalhe": d} for n, o, d in RESULT], open(r"D:\PROJETOS\BipHelp\backend\tests_validacao006\http_results.json", "w"), indent=2, ensure_ascii=False)
sys.exit(0 if ok == len(RESULT) else 1)
