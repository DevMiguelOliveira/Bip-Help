with open('models.py', 'r') as f:
    content = f.read()
idx = content.find('url_anexo = Column(String, nullable=True)')
if idx != -1:
    end_idx = content.find('\n', idx)
    rep = '    interna = Column(Boolean, default=False, server_default=\
false\, nullable=False)\n'
    new_content = content[:end_idx+1] + rep + content[end_idx+1:]
    with open('models.py', 'w') as f:
        f.write(new_content)
    print('Done')
else:
    print('Not found')
