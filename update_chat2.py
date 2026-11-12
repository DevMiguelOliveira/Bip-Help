content = open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'r', encoding='utf-8').read()

# Replace the message-visibility div with the redesigned-chat tabs
old_block = '{isSupport && <div className=\
message-visibility\>'
new_block = '''{isSupport && (
            <div className=\redesigned-chat\>
              <div className=\chat-tabs\>
                <button type=\button\ className={\chat-tab \\} onClick={() => setActiveView(\conversation\)}>
                  <MessageSquareText size={14} /> Conversa
                  <span className=\chat-tab-count\>
                    {messages.filter((m) => !m.interna).length}
                  </span>
                </button>
                <button type=\button\ className={\chat-tab \\} onClick={() => setActiveView(\notes\)}>
                  <StickyNote size={14} /> Notas
                  <span className=\chat-tab-count\>
                    {messages.filter((m) => m.interna).length}
                  </span>
                </button>
              </div>
              {(activeView === \notes\ && !canCreateInternalNote) && (
                <div className=\internal-access-banner\>
                  <LockKeyhole size={14} />
                  <div>
                    <strong>Acesso restrito</strong>
                    Somente administradores e equipe de suporte podem criar e visualizar notas internas.
                  </div>
                </div>
              )}
            </div>
          )}
          <div className=\composer-heading\>
            {activeView === \notes\
              ? <><StickyNote size={15} /><strong>Nova nota interna</strong></>
              : <><MessageSquareText size={15} /><strong>Responder ao chamado</strong></>}
          </div>
          {activeView === \notes\ && <span className=\notes-only-badge\>Somente suporte</span>}
          {isSupport && <div className=\message-visibility\>}'''

content = content.replace(old_block, new_block)

with open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Part 2 done!')
