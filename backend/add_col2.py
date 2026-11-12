import re
content = open('models.py').read()
new_content = re.sub(r'(url_anexo = Column\(String, nullable=True\))', r'\\1\\n    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)', content)
open('models.py', 'w').write(new_content)
print('Done')
