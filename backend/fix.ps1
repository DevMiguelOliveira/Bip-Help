$content = [IO.File]::ReadAllText("main.py", [Text.Encoding]::UTF8)
$content = $content -replace "administrador\\, \\suporte_n1\\, \\suporte_n2\\)", "\"administrador\", \"suporte_n1\", \"suporte_n2\""
$content = $content -replace "detail=\Apenas\na\nequipe\nde\nsuporte\npode\ncriar\nnotas\ninternas\.", "detail=\"Apenas a equipe de suporte pode criar notas internas.\""
[IO.File]::WriteAllText("main.py", $content, [Text.Encoding]::UTF8)
Write-Host "Fixed"
