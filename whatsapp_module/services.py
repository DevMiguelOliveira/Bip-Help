"""
WhatsApp Module Services
Serviços opcionais para integração com API WhatsApp.
Este módulo é importado apenas se WA_ENABLED=True na configuração.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Serviço base para integração WhatsApp."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get("WA_ENABLED", False)
        self.provider = self.config.get("WA_PROVIDER", "official")
        self.number_id = self.config.get("WA_NUMBER_ID")
        self.access_token = self.config.get("WA_ACCESS_TOKEN")

        if not self.enabled:
            logger.info("WhatsApp module disabled - service not initialized")
            return

        if not self.number_id or not self.access_token:
            logger.error("WhatsApp module enabled but missing number_id or access_token")
            self.enabled = False
            return

        logger.info(f"WhatsApp service initialized - provider: {self.provider}, number_id: {self.number_id}")

    async def send_text_message(self, to_number: str, text: str) -> Optional[Dict[str, Any]]:
        """Enviar mensagem de texto via WhatsApp."""
        if not self.enabled:
            return None

        # Implementação placeholder - em produção integraria com Twilio/MetriQ
        logger.info(f"Would send WhatsApp text to {to_number}: {text[:50]}...")
        return {
            "status": "placeholder",
            "message": "Funcionalidade placeholder - integrar com provedor WhatsApp"
        }

    async def send_media_message(
        self,
        to_number: str,
        media_type: str,
        media_url: str,
        caption: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Enviar mensagem com mídia (imagem, documento, etc.)."""
        if not self.enabled:
            return None

        logger.info(
            f"Would send WhatsApp {media_type} to {to_number} with caption: {caption[:50]}..."
        )
        return {
            "status": "placeholder",
            "message": "Funcionalidade placeholder - integrar com provedor WhatsApp"
        }

    async def get_template_status(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Verificar status de um template de mensagem aprovado."""
        if not self.enabled:
            return None

        logger.info(f"Would check template status: {template_name}")
        return {"status": "placeholder", "template": template_name}

    def is_enabled(self) -> bool:
        """Verificar se o serviço WhatsApp está ativo."""
        return self.enabled


# Função auxiliar para criar instância condicional
def create_whatsapp_service(config: Dict[str, Any] = None) -> Optional[WhatsAppService]:
    """Criar serviço WhatsApp apenas se estiver habilitado."""
    service = WhatsAppService(config)
    if service.is_enabled():
        return service
    return None