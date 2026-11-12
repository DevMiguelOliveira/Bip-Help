with open('models.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'interna' in line:
        lines[i] = '    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)\n'
with open('models.py', 'w') as f:
    f.writelines(lines)
print('Fixed')
