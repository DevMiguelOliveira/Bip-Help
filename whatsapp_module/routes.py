"""
WhatsApp Module Routes
Endpoints e webhooks para integração WhatsApp.
Estes endpoints devem ser adicionados ao backend principal condicionalmente.
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = "",
    hub_challenge: str = "",
    hub_verify_token: str = "",
    config: dict = None
):
    """
    Verificar webhook do WhatsApp.
    O Meta (WhatsApp) envia estes parâmetros GET para validar a URL.
    """
    # Verificar token de segurança
    expected_token = config.get("WA_WEBHOOK_VERIFY_TOKEN") if config else None

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return int(hub_challenge) if hub_challenge else {"status": "verified"}

    raise HTTPException(status_code=403, detail="Token de verificação inválido")


@router.post("/webhook")
async def whatsapp_webhook_receive(
    request: Request,
    config: dict = None
):
    """
    Receber webhook do WhatsApp.
    O Meta envia POSTs com eventos de mensagem, status, etc.
    """
    if not config or not config.get("WA_ENABLED", False):
        raise HTTPException(status_code=404, detail="WhatsApp module disabled")

    try:
        body = await request.json()
        logger.info(f"WhatsApp webhook received: {body.get('entry', [])}")

        # Processar eventos de mensagem
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])

                # Processar mensagens recebidas
                for message in messages:
                    await process_incoming_message(message, value)

        return {"status": "received"}

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


async def process_incoming_message(message: Dict[str, Any], value: Dict[str, Any]):
    """Processar mensagem recebida do WhatsApp."""
    message_type = message.get("type", "")

    if message_type == "text":
        text_content = message.get("text", {}).get("body", "")
        from_number = message.get("from", "")
        message_id = message.get("id", "")

        logger.info(
            f"Received WhatsApp text from {from_number}: {text_content[:50]}..."
        )

        # Aqui seria acionar lógica do BipHelp
        # Ex: criar ticket, responder automaticamente, etc.

    elif message_type == "image":
        image_caption = message.get("image", {}).get("caption", "")
        image_id = message.get("image", {}).get("id", "")
        from_number = message.get("from", "")

        logger.info(
            f"Received WhatsApp image from {from_number}, image_id: {image_id}"
        )

    elif message_type == "status":
        status = message.get("status", {})
        logging.info(f"WhatsApp status update: {status}")


@router.post("/send-text")
async def whatsapp_send_text(
    to_number: str,
    text: str,
    background_tasks: BackgroundTasks,
    whatsapp_service: Optional[Any] = None
):
    """Endpoint HTTP para enviar mensagem de texto WhatsApp."""
    if not whatsapp_service:
        return {"status": "disabled", "message": "WhatsApp module not enabled"}

    # Executar em background
    background_tasks.add_task(
        whatsapp_service.send_text_message, to_number, text
    )

    return {
        "status": "queued",
        "message": f"Mensagem para {to_number} enfileirada para envio",
    }