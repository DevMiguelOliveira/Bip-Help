content = open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'r', encoding='utf-8').read()

# Replace the notes tab condition
content = content.replace(
    '{isSupport && (\\n            <button',
    '{canCreateInternalNote && (\\n            <button'
)

# Replace the internal-access-banner condition  
content = content.replace(
    '{activeView === \
notes\ && isSupport && (',
    '{activeView === \notes\ && !canCreateInternalNote && ('
)

# Also fix the internal-access-banner content to match the new message
content = content.replace(
    '''<div className=\internal-access-banner\>
            <ShieldCheck size={16} />
            <div>
              <strong>Área exclusiva da equipe</strong>
              <span>Estas notas não são exibidas ao franqueado.</span>
            </div>
          </div>''',
    '''<div className=\internal-access-banner\>
            <LockKeyhole size={14} />
            <div>
              <strong>Acesso restrito</strong>
              Somente administradores e equipe de suporte podem criar e visualizar notas internas.
            </div>
          </div>'''
)

# Also update the notes tab label and icon
content = content.replace(
    '''<StickyNote size={16} />
              Notas internas
              <span className=\chat-tab-count\>{messages.filter((message) => message.interna).length}</span>
              <LockKeyhole size={12} />''',
    '''<StickyNote size={14} /> Notas
              <span className=\chat-tab-count\>{messages.filter((message) => message.interna).length}</span>'''
)

with open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed conditions!')
