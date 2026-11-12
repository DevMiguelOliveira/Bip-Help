import requests
API="http://127.0.0.1:8001"; PW="senha_teste123"
r=requests.post(API+"/auth/login", data={"username":"suporte1@biphelp.com","password":PW}, timeout=20)
t=r.json().get("access_token") or r.json().get("token"); H={"Authorization":"Bearer "+t}
for path in ["/uploads/..%2F..%2F..%2Fetc%2Fpasswd","/uploads/%2e%2e/%2e%2e/main.py","/uploads/nonexist.png"]:
    try:
        g=requests.get(API+path, headers=H, timeout=15, allow_redirects=False)
        print(path, "->", g.status_code)
    except Exception as e:
        print(path, "-> ERRO", type(e).__name__)
