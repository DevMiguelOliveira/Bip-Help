import sys
with open('models.py', 'r') as f:
    content = f.read()
old = 'url_anexo = Column(String, nullable=True)'
new = 'url_anexo = Column(String, nullable=True)\\n    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)'
if old in content:
    content = content.replace(old, new)
    with open('models.py', 'w') as f:
        f.write(content)
    print('Done')
else:
    print('Not found')
