"""
WhatsApp Module Configuration
Módulo opcional para integração WhatsApp no BipHelp.
Este módulo pode ser importado condicionalmente e não afeta o core do sistema.
"""

# Configurações padrão - substituir por variáveis de ambiente em produção
DEFAULT_CONFIG = {
    "WA_ENABLED": False,  # Desabilitado por padrão; habilitar via .env ou configuração
    "WA_PROVIDER": "official",  # "official" (Twilio/MetriQ) ou "sandbox"
    "WA_NUMBER_ID": None,  # Number ID da conta WhatsApp Business
    "WA_ACCESS_TOKEN": None,  # Token de acesso da API WhatsApp
    "WA_WEBHOOK_VERIFY_TOKEN": None,  # Token para validação de webhook
    "WA_WEBHOOK_URL": None,  # URL do webhook (ngrok/produção)

    # Configurações de segurança
    "MAX_MESSATURES_PER_DAY": 1000,
    "MAX_MESSAGE_SIZE_BYTES": 5 * 1024 * 1024,  # 5MB
    "SUPPORTED_MEDIA_TYPES": ["image/jpeg", "image/png", "image/webp", "text/plain"],

    # Flags de recurso
    "USE_NATIVE_API": True,  # Usar API oficial vs. workaround
    "LOG_WHATSAPP_ACTIVITY": True,  # Log de atividades para auditoria
}

# Para habilitar: exportar variáveis de ambiente ou sobrescrever este módulo
# Exemplo .env:
# WA_ENABLED=true
# WA_PROVIDER=official
# WA_NUMBER_ID=1234567890
# WA_ACCESS_TOKEN=seu_token_aqui