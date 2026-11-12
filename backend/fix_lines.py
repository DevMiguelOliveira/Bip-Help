import
os
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'administrador' in line and 'suporte_n1' in line and 'suporte_n2' in line:
        lines[i] = '    equipe_suporte = papel in (\
administrador\, \suporte_n1\, \suporte_n2\)\n'
    if 'Apenas' in line and 'equipe' in line and 'suporte' in line:
        lines[i] = '            detail=\
Apenas
a
equipe
de
suporte
pode
criar
notas
internas.\\n'

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed')
