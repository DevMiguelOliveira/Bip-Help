import re
content = open('models.py').read()
old = 'url_anexo = Column(String, nullable=True)'
new = 'url_anexo = Column(String, nullable=True)\\n    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)'
content = content.replace(old, new)
open('models.py', 'w').write(content)
print('Done')
