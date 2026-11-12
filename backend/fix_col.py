content = open('models.py').read()
content = content.replace('url_anexo = Column(String, nullable=True)\\\\n    interna = Column(Boolean, default=False, server_default=false\\\\, nullable=False)', 'url_anexo = Column(String, nullable=True)\\n    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)')
open('models.py', 'w').write(content)
print('Fixed')
