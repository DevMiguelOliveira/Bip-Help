import { Moon, Sun } from 'lucide-react'

export function ThemeToggle({ theme, onToggle }: { theme: 'light' | 'dark'; onToggle: () => void }) {
  return (
    <button className="icon-button" onClick={onToggle} aria-label={theme === 'light' ? 'Ativar tema escuro' : 'Ativar tema claro'} title="Alternar tema">
      {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
    </button>
  )
}
