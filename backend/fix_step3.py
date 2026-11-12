with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines 921-929
lines[920] = '            status_code=403,\n'
lines[921] = '            detail=\"Apenas a equipe de suporte pode criar notas internas.\",\n'
# Remove lines 922-929 (they are the broken message)
del lines[922:930]

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed the detail message')
