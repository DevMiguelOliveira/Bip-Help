with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix the duplicated status_code and add closing parenthesis
# Lines 919-922 should be:
#         raise HTTPException(
#             status_code=403,
#             detail="Apenas a equipe de suporte pode criar notas internas.",
#         )
new_lines = []
i = 0
while i < len(lines):
    if i == 918:  # '        raise HTTPException(\n'
        new_lines.append(lines[i])  # raise HTTPException(
        new_lines.append(lines[i+1])  # status_code=403,
        new_lines.append(lines[i+2])  # detail="..."
        new_lines.append('        )\n')  # closing
        i += 4  # skip the duplicate status_code line and move to next
    else:
        new_lines.append(lines[i])
        i += 1

with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed the HTTPException closing')
