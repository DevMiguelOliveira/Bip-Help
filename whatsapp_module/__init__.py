"""
WhatsApp Module for BipHelp
Módulo opcional para integração WhatsApp.

Este módulo pode ser importado condicionalmente e não afeta o core do sistema BipHelp.

Para habilitar:
1. Definir WA_ENABLED=true no config ou .env
2. Preencher WA_NUMBER_ID e WA_ACCESS_TOKEN
3. Incluir os routes no backend principal de forma condicional

Exemplo de uso:
    from whatsapp_module import create_whatsapp_service, is_whatsapp_enabled
    wa_service = create_whatsapp_service(config)
    if wa_service and wa_service.is_enabled():
        # Usar wa_service.send_text_message(...)
        pass
"""

from .config import DEFAULT_CONFIG, __all__ as config_all
from .services import WhatsAppService, create_whatsapp_service, is_enabled

__all__ = [
    "DEFAULT_CONFIG",
    "WhatsAppService",
    "create_whatsapp_service",
    "is_enabled",
    "whatsapp_module",
]