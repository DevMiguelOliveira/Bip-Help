with open('models.py', 'r') as f:
    content = f.read()
content = content.replace('url_anexo = Column(String, nullable=True)\\\\n    interna = Column(Boolean, default=False, server_default=false\\\\, nullable=False)', 'url_anexo = Column(String, nullable=True)\\\\n    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)')
with open('models.py', 'w') as f:
    f.write(content)
print('Fixed')
