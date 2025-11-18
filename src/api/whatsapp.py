# src/api/whatsapp.py

from fastapi import APIRouter, Request
from src.utils.cache import Cache
from src.services.messaging import send_msg, run_graph

cache = Cache()
router = APIRouter(prefix="/api", tags=["WhatsApp"])

@router.post("/whatsapp_webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    data = dict(form)

    sender = data.get("From")
    message = data.get("Body")
    thread_id = sender.replace("whatsapp:", "").replace("+", "")

    termination_keywords = ["clear", "end", "close", "exit", "stop"]
    if message and any(word in message.lower() for word in termination_keywords):
        cache.remove(thread_id)
        await send_msg("Chat Ended:", f"whatsapp:+{thread_id}")
    else:
        await run_graph(thread_id, message, cache)