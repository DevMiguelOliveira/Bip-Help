import sys
with open('models.py', 'r') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    new_lines.append(line)
    if 'url_anexo = Column(String, nullable=True)' in line:
        new_lines.append('    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)\\n')
with open('models.py', 'w') as f:
    f.writelines(new_lines)
print('Done')
