# Teste de seguranca do WS - simulando broadcast
import sys
sys.path.insert(0, '.')

from main import manager, models
from database import SessionLocal

db = SessionLocal()

# Simular conexões
class MockWS:
    def __init__(self, name):
        self.name = name
        self.sent = []
    async def send_json(self, data):
        self.sent.append(data)
        print(f'  {self.name} recebeu: {data.get("type")} - interna={data.get("interna")}')
    def close(self):
        pass

# Criar mensagens de teste
mensagem_normal = {
    "type": "new_message",
    "interna": False,
    "id": 1,
    "ticket_id": 1,
    "texto": "Mensagem normal",
    "remetente": "Funcionario A",
}

mensagem_interna = {
    "type": "new_message",
    "interna": True,
    "id": 2,
    "ticket_id": 1,
    "texto": "Nota interna de teste",
    "remetente": "Suporte",
}

# Simular conexões
print('=== SIMULACAO WS: Testando broadcast com filtro interna ===\n')

# Reset manager
manager.active_connections = {}

# Conectar suporte (is_support=True)
ws_suporte = MockWS('Suporte')
manager.connect(ticket_id=1, websocket=ws_suporte, is_support=True)
print('  Suporte conectado (is_support=True)')

# Conectar funcionario A (is_support=False)
ws_func_a = MockWS('Funcionario A')
manager.connect(ticket_id=1, websocket=ws_func_a, is_support=False)
print('  Funcionario A conectado (is_support=False)')

# Broadcast mensagem normal
print('\n--- Broadcast: Mensagem normal ---')
import asyncio
asyncio.run(manager.broadcast(1, mensagem_normal))

# Broadcast nota interna
print('\n--- Broadcast: Nota interna ---')
asyncio.run(manager.broadcast(1, mensagem_interna))

# Verificar resultados
print(f'\n=== RESULTADO ===')
print(f'Suporte recebeu {len(ws_suporte.sent)} mensagem(s):')
for m in ws_suporte.sent:
    print(f'  - {m.get("type")}')

print(f'\nFuncionarie A recebeu {len(ws_func_a.sent)} mensagem(s):')
for m in ws_func_a.sent:
    print(f'  - {m.get("type")}')

# Validacao
suporte_internas = [m for m in ws_suporte.sent if m.get('interna') == True]
func_a_internas = [m for m in ws_func_a.sent if m.get('interna') == True]

if len(suporte_internas) >= 1 and len(func_a_internas) == 0:
    print('\n[APROVADO] FILTRAGEM WS: Nota interna somente para suporte')
    sys.exit(0)
else:
    print('\n[FALHA] SEGURANCA WS: Isolamento nao funcionou corretamente')
    sys.exit(1)
