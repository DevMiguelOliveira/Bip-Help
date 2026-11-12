\ = 'D:\PROJETOS\BIPHELP\frontend\src\pages\TicketChatDialog.tsx'
\ = Get-Content \ -Raw
\ = \ -split \"
\"

# Find and insert internalNote state after wsStatus state
\ = @()
\ = \False

for (\ = 0; \ -lt \.Count; \++) {
    \ = \[\]
    
    # Insert internalNote state after wsStatus declaration
    if (-not \ -and \ -match 'const \[wsStatus, setWsStatus\] = useState') {
        \ += \
        # Add internalNote state on next line
        \ += '  const [internalNote, setInternalNote] = useState(false)'
        \ = \True
        continue
    }
    
    # Insert note states after file state declaration
    if (-not \ -and \ -match 'const \[file, setFile\] = useState') {
        \ += \
        \ += '  const [noteText, setNoteText] = useState(\"\");'
        \ += '  const [noteFile, setNoteFile] = useState<File | undefined>();'
        \ = true
        continue
    }
    
    # Add visibility toggle UI before composer-attachment div
    if (-not \ -and \ -like '*className=\"composer-attachment*') {
        # Add the visibility toggle before this line
        \ += '      {isSupport && <div className=\"message-visibility\">'
        \ += '        <button type=\"button\" className={!internalNote ? \"visibility-option active\" : \"visibility-option\"}'
        \ += '          onClick={() => setInternalNote(!internalNote)}>'
        \ += '          Mensagem Normal'
        \ += '        </button>'
        \ += '        <button type=\"button\" className={internalNote ? \"visibility-option internal active\" : \"visibility-option intern\"}'
        \ += '          onClick={() => setInternalNote(!internalNote)}>'
        \ += '          Nota Interna'
        \ += '        </button>'
        \ += '      </div>'
        \ += \  # Add the original line after the toggle
        \ = true
        continue
    }
    
    # Modify message row class to include internal-note conditionally
    if (-not \ -and \ -match 'message-row.*own') {
        \ = \ -replace 'message-row', 'message-row {message.interna && \"internal-note\" || \"\"}'
        \ = true
    }
    
    \ += \
}

# Write back the modified content
Set-Content -Path  -Value (\ -join \"
\") -Encoding utf8
Write-Host 'TicketChatDialog.tsx integrated successfully'
