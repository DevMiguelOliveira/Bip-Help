import re

with open('D:/PROJETOS/BipHelp/backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix corrupted strings
content = content.replace(
    'equipe_suporte = papel in (administrador\\, \\suporte_n1\\, \\suporte_n2\\)',
    'equipe_suporte = papel in (\
administrador\, \suporte_n1\, \suporte_n2\)'
)
content = content.replace(
    'detail=\\Apenas\\na\\nequipe\\nde\\nsuporte\\npode\\ncriar\\nnotas\\ninternas\\.        \\)',
    'detail=\Apenas
a
equipe
de
suporte
pode
criar
notas
internas.\        )'
)

# Add 'interna=interna' to Mensagem creation
content = content.replace(
    'url_anexo=anexo_url\n        )',
    'url_anexo=anexo_url,\n            interna=interna\n        )'
)

# Add 'interna' to broadcast
content = content.replace(
    '\criada_em\: db_mensagem.criada_em.isoformat()\n        }',
    '\interna\: db_mensagem.interna,\n            \criada_em\: db_mensagem.criada_em.isoformat()\n        }'
)

with open('D:/PROJETOS/BipHelp/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Step 1 done')
