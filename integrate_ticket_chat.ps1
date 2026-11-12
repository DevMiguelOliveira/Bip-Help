\ = 'D:\PROJETOS\BIPHELP\frontend\src\pages\TicketChatDialog.tsx'
\ = Get-Content \ -Raw
\ = \ -split \"
\"

# Insert internalNote state after wsStatus state
\ = @()
\ = \False

for (\ = 0; \ -lt \.Count; \++) {
    \ = \[\]
    
    # Insert internalNote state after wsStatus state
    if (-not \ -and \ -like 'const [wsStatus, setWsStatus] = useState*') {
        \.Add(\)
        \.Add('  const [internalNote, setInternalNote] = useState(false)')
        \ = \True
        continue
    }
    
    # Add noteText and noteFile states after file state
    if (-not \ -and \ -like 'const [file, setFile] = useState<File | undefined>(') {
        \.Add(\)
        \.Add('  const [noteText, setNoteText] = useState(\"\");')
        \.Add('  const [noteFile, setNoteFile] = useState<File | undefined>();')
        continue
    }
    
    # Add visibility toggle UI before composer-attachment div
    if (-not \ -and \ -like '*className=\"composer-attachment\"*') {
        \.Add('      {isSupport && <div className=\"message-visibility\">')
        .Add('          <button type=\"button\" className={!internalNote ? \"visibility-option active\" : \"visibility-option\"}')
        .Add('            onClick={() => setInternalNote(!internalNote)}>')
        .Add('            Mensagem Normal')
        .Add('        </button>')
        .Add('        <button type=\"button\" className={internalNote ? \"visibility-option internal active\" : \"visibility-option intern\"}')
        .Add('            onClick={() => setInternalNote(!internalNote)}>')
        .Add('            Nota Interna')
        .Add('        </button>')
        .Add('      </div>')
        .Add(')')  # Close the div
        .Add()  # Add the original line
        continue
    }
    
    # Add internal-note class to message rows
    if (-not \ -and \ -like '*message-row*own*') {
        # Replace message-row with conditional internal-note class
        \ = \ -replace 'message-row', 'message-row {message.interna && \"internal-note\" || \"\"} {own}'
        \ = True
    }
    
    \.Add(\)
}

# Write back the modified content
Set-Content -Path \ -Value (\ -join \"
\") -Encoding utf8
Write-Host \"File modified successfully\"
