# BIPManager Frontend

Frontend independente do backend BIPManager: React + TypeScript + Vite, Tailwind CSS 4, React Router e TanStack Query.

## Requisitos

- Node.js 22.12+ (Vite 8 exige 20.19+ ou 22.12+; Node 24 LTS também é uma opção)
- npm 10+
- Backend FastAPI disponível em `127.0.0.1:8001` durante desenvolvimento na VM

Vite 8 exige Node.js 20.19+ ou 22.12+. Consulte https://vite.dev/releases/.

## Instalação na VM Azure

A partir de `/home/BipManager/bipmanager`:

```bash
unzip bipmanager-frontend.zip -d .
cd frontend
cp .env.example .env
npm install
npm run typecheck
npm run build
```

O projeto foi entregue para ser extraído como `bipmanager/frontend` e não altera `backend/`, `docker-compose.yml` ou o banco.

## Desenvolvimento

Na própria Azure VM, com o FastAPI ativo em `127.0.0.1:8001`:

```bash
npm run dev -- --host 0.0.0.0
```

O Vite fica na porta 5173 e usa proxy local para `/auth`, `/franquias`, `/tickets`, `/usuarios`, `/uploads` e `/ws`. Não exponha a porta 5173 publicamente. Para acesso remoto de desenvolvimento, use o túnel do VS Code Remote-SSH ou um túnel SSH.

Abra `http://localhost:5173` pelo encaminhamento de porta do VS Code.

Se o FastAPI não estiver em `127.0.0.1:8001`, defina `BIPMANAGER_API_TARGET` antes de iniciar Vite:

```bash
BIPMANAGER_API_TARGET=http://127.0.0.1:8001 npm run dev
```

## Build de produção

```bash
npm run typecheck
npm run build
```

O build estático será gerado em `dist/`. O plano de implantação é servir `dist/` pelo Nginx no domínio do BIPManager e encaminhar os endpoints REST e WebSocket ao Uvicorn em `127.0.0.1:8001`.

**Não publique `dist/` até revisar o arquivo `deploy/nginx-frontend.example.conf` e preservar os blocos TLS existentes do Nginx.** A configuração de produção não é aplicada automaticamente por este projeto.

## Backend esperado

- `POST /auth/login` (form-urlencoded: username, password)
- `GET /auth/me`
- `GET /franquias/`
- `GET /tickets/` e `POST /tickets/`
- `GET /tickets/{id}/mensagens/`
- `POST /tickets/{id}/mensagens/` (multipart: texto e file; sem remetente)
- `POST /tickets/{id}/ws-token`
- `GET /uploads/{filename}` (Bearer token obrigatório)
- Rotas administrativas `/usuarios/` e `/usuarios/{id}/franquias`

## Sessão e segurança nesta primeira entrega

- O JWT é mantido somente em memória React. Atualizar/recarregar a página encerra a sessão e exige novo login. Não há refresh-token no backend atual.
- A API é a autoridade final para permissões. O frontend oculta navegação administrativa de outros perfis, mas isso não substitui as verificações do backend.
- Anexos são carregados por `fetch` autenticado e mostrados via URL Blob temporária, revogada ao desmontar o componente.
- O WebSocket obtém token efêmero pelo endpoint REST e o envia no primeiro frame, conforme contrato do backend.
- Para produção, considere uma estratégia de renovação de sessão com cookie HttpOnly/Secure/SameSite antes de buscar sessões persistentes.
- Atenção à origem do WebSocket: o backend atual valida `Origin` comparando com `https://bip-manager.lovable.app`. Antes de publicar este frontend em `https://bipmanager.duckdns.org`, altere essa allowlist no `main.py` para incluir o domínio de produção. Para desenvolvimento via Vite (`http://localhost:5173`), inclua essa origem apenas em ambiente de desenvolvimento. Não enfraqueça a validação para `*`.

## Funcionalidades iniciais

- Login conectado à API real.
- Dashboard com dados reais e filtros por unidade.
- Resumo de tickets por status.
- Central de chamados, pesquisa e filtros por unidade/status.
- Abertura de chamado.
- Chat com histórico, envio de texto/imagem e atualizações WebSocket.
- Leitura autenticada de anexos.
- Listagem e cadastro administrativo de usuários e vínculo inicial a uma franquia.
- Alternância de tema claro/escuro.

Algumas funções administrativas ainda são incrementais: edição avançada de vínculos, criação de franquias e configurações de conta não estão implementadas nesta primeira entrega.

## Compatibilidade / validação da entrega

Os arquivos TS/TSX foram submetidos a análise sintática. A instalação npm e o build completo precisam ser executados no ambiente com acesso ao registry npm (`npm install`, `npm run typecheck`, `npm run build`). O ambiente de empacotamento desta entrega não conseguiu resolver `registry.npmjs.org`, portanto não foi possível gerar `package-lock.json` nem afirmar que o build foi executado aqui. As versões de dependências estão fixadas em `package.json` para reprodutibilidade; gere e versione o `package-lock.json` no primeiro `npm install` bem-sucedido.

## Publicação Nginx (quando o build for aprovado)

1. Gere `dist/` com `npm run build`.
2. Copie os arquivos estáticos para `/var/www/bipmanager` e garanta leitura para o usuário `www-data`.
3. Faça backup de `/etc/nginx/sites-available/bipmanager`.
4. Mescle `deploy/nginx-frontend.locations.conf` dentro do `server` HTTPS já existente, preservando os caminhos `ssl_certificate` e o redirect HTTP do Certbot.
5. Execute `sudo nginx -t` antes de `sudo systemctl reload nginx`.
6. Antes de testar WSS no novo domínio, atualize no backend a allowlist do WebSocket para aceitar `https://bipmanager.duckdns.org`. Mantenha apenas origens conhecidas; não use `*`.

Não aplique o snippet como arquivo independente: ele contém diretivas de localização para mesclar no `server` HTTPS existente.
