# 16 — Lacunas e Comportamentos Não Implementados

Documento investigativo da Fase 4. Lista de itens identificados como ausentes, incompletos ou divergentes.

## Funcionalidades não encontradas no código

| Item | Onde foi esperado | Status |
|------|-------------------|--------|
| Objeto R / R.url.getAPIURL / R.services | Busca em todos os arquivos fonte, bundle, .map, starter | Não encontrado |
| Axios como cliente HTTP | package.json e src/lib/ | Não encontrado (usa fetch nativo) |
| Socket.IO | src e backend | Não encontrado (usa WebSocket nativo) |
| Serviço chatAgents | src e backend | Não encontrado |
| Serviço chatIntegrator | src e backend | Não encontrado |
| Serviço ai | src e backend | Não encontrado |
| Serviço creditManagement | src e backend | Não encontrado |
| Serviço whatsapp | src e backend | Não encontrado |
| Endpoint GET /tickets/{id} | backend/main.py | Não encontrado |
| Endpoint PATCH /franquias/{id} (ativar/desativar) | backend/main.py | Não encontrado |
| Endpoint PATCH /usuarios/{id} (desativar) | backend/main.py | Não encontrado |
| Endpoint PATCH /mensagens/{id} | backend/main.py | Não encontrado |
| Endpoint DELETE /mensagens/{id} | backend/main.py | Não encontrado |
| Lógica de distribuição automática de tickets | backend/main.py | Não encontrada |
| Lógica de atribuição de ticket a atendente | backend/main.py | Não encontrada |
| Timeout explícito de requisição HTTP | src/lib/api.ts | Não definido |

## Comportamentos parcialmente implementados

| Item | Descrição | Impacto |
|------|-----------|---------|
| Filtro de status na listagem de tickets | Frontend recebe parâmetro status mas ignora (void status). Backend não expõe o parâmetro. | Usuário não pode filtrar tickets por status via API. |
| Controle de status no chat | Frontend expõe select de status apenas para administrador e suporte_n1. Backend permite suporte_n2 também. | Suporte_n2 não pode alterar status via interface do chat. |
| Capacidade de atendente | capacidade_maxima e disponivel são armazenados mas não usados para limitar ou distribuir tickets. | Configuração sem efeito operacional. |
| Ativação/desativação de franquia | Campo ativa existe no modelo mas não há endpoint para alterá-lo. | Não é possível ativar/desativar franquias via API. |
| Expiração de token WS | Token expira em 60s sem renovação automática. | Conexão WebSocket pode cair silenciosamente após 1 minuto. |
| Perda de acesso ao ticket durante WS | Validação de acesso ocorre apenas no handshake. Não há desconexão se o usuário perder acesso durante a conexão. | Usuário pode continuar recebendo eventos após perder acesso. |

## Pontos não identificados

| Item | Motivo |
|------|--------|
| Timeout de requisição HTTP de 15s | Não existe no código frontend; pode estar em proxy/Nginx/infraestrutura. |
| Banco de dados real (dados) | URL em /etc/bipmanager/database_url, não acessível neste ambiente. |
| Segredo JWT | Arquivo em /etc/bipmanager/jwt_secret, não acessível neste ambiente. |
| Logs de produção completos | Logs parciais no repositório, truncados. |
| Branches/tags alternativas | Não verificadas; podem conter R, Axios ou serviços ausentes. |

## Riscos técnicos e funcionais

1. **Sem distribuição automática:** Tickets não são atribuídos automaticamente a atendentes. A configuração de capacidade e disponibilidade não tem efeito operacional.
2. **Sem edição/exclusão de mensagens:** Mensagens são imutáveis após criação. Não há como corrigir erros.
3. **Sem validação de transição de status:** Qualquer status pode ser definido para qualquer ticket (ex: de Encerrado para Aberto).
4. **Sem identificação de criador de ticket:** Não há registro de quem abriu cada ticket.
5. **Token WS de curta duração (60s):** Pode causar desconexões frequentes se o frontend não renovar proativamente.
6. **Sem desconexão WS por perda de acesso:** Segurança potencialmente fraca se o acesso ao ticket for revogado durante uma sessão WS ativa.

## Dúvidas que dependem do responsável pelo produto

- Os serviços ausentes (chatAgents, chatIntegrator, ai, creditManagement, whatsapp) estão planejados para outra fase ou outro repositório?
- O objeto R / getAPIURL / R.services existe em alguma versão anterior ou branch diferente?
- O timeout de 15s mencionado está implementado em alguma camada de infraestrutura (Nginx, balanceador)?
- A capacidade de atendente deve afetar a distribuição de tickets ou é apenas exibição?
- É necessário adicionar endpoints de edição/exclusão de mensagem e consulta individual de ticket?
