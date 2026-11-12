import re
content = open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'r', encoding='utf-8').read()

# Update WsToken interface
content = content.replace(
    'interface WsToken { token: string; expires_in: number }',
    'interface WsToken { token: string; expires_in: number; pode_criar_nota_interna?: boolean }'
)

# Add canCreateInternalNote state after liveMessages
content = content.replace(
    'const [liveMessages, setLiveMessages] = useState<Message[]>([])\n  const bottomRef',
    'const [liveMessages, setLiveMessages] = useState<Message[]>([])\n  const [canCreateInternalNote, setCanCreateInternalNote] = useState(false)\n  const bottomRef'
)

# Update the connect function to use canCreateInternalNote
old = '''const result = await apiRequest<WsToken>(/tickets//ws-token, { method: \
POST\ }, token)
        if (!active) return
        const configured'''
new = '''const result = await apiRequest<WsToken>(/tickets//ws-token, { method: \POST\ }, token)
        if (!active) return
        setCanCreateInternalNote(result.pode_criar_nota_interna ?? false)
        const configured'''
content = content.replace(old, new)

with open('D:/PROJETOS/BipHelp/frontend/src/pages/TicketChatDialog.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print('Part 1 done!')
