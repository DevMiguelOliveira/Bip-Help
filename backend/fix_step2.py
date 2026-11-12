import re

# Read the current main.py
with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Print the problematic line to debug
for i, line in enumerate(content.split('\n')):
    if 'equipe_suporte' in line:
        print(f'Line {i}: {repr(line)}')

# 1. Fix the corrupted tuple syntax in enviar_mensagem
content = content.replace(
    r'equipe_suporte = papel in (\ administrador\, \suporte_n1\, \suporte_n2\)',
    'equipe_suporte = papel in (\"administrador\", \"suporte_n1\", \"suporte_n2\")'
)

# 2. Fix the corrupted error message
content = content.replace(
    r'detail=\Apenas\na\nequipe\nde\nsuporte\npode\ncriar\nnotas\sinternas\.',
    'detail=\"Apenas a equipe de suporte pode criar notas internas.\"'
)

# Write the fixed content
with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Step 2: Syntax fixes applied successfully!')
