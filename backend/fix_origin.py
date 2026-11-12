with open('main.py','r',encoding='utf-8') as f:
    c = f.read()
old = '''FRONTEND_ORIGINS = [
    "https://bip-manager.lovable.app",
    "http://127.0.0.1:5173",
]'''
new = '''FRONTEND_ORIGINS = [
    "https://bip-manager.lovable.app",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]'''
if old in c:
    c = c.replace(old, new, 1)
    with open('main.py','w',encoding='utf-8') as f:
        f.write(c)
    print('Origem localhost:5173 adicionada.')
else:
    print('Trecho nao encontrado.')
