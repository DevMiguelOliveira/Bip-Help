with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'administrador\\, \\suporte_n1\\, \\suporte_n2\\)' in line:
        lines[i] = line.replace('administrador\\, \\suporte_n1\\, \\suporte_n2\\)', '\
administrador\, \suporte_n1\, \suporte_n2\')
    if 'detail=\\Apenas\\na\\nequipe\\nde\\nsuporte\\npode\\ncriar\\nnotas\\ninternas.' in line:
        lines[i] = line.replace('detail=\\Apenas\\na\\nequipe\\nde\\nsuporte\\npode\\ncriar\\nnotas\\ninternas.', 'detail=\Apenas
a
equipe
de
suporte
pode
criar
notas
internas.\')

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Fixed')
