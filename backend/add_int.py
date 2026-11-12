with open('models.py', 'r') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'url_anexo = Column(String, nullable=True)' in line:
        lines.insert(i+1, '    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)\n')
        break
with open('models.py', 'w') as f:
    f.writelines(lines)
print('Done')
