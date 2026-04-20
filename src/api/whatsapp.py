# src/api/whatsapp.py

from fastapi import APIRouter, Request
from src.utils.cache import Cache
from src.services.messaging import send_msg, run_graph
import asyncio

cache = Cache()
router = APIRouter(prefix="/thcm-agentic-poc/api", tags=["WhatsApp"])

def run_in_background(coro, context: dict = None):
    async def wrapper():
        try:
            await coro
        except Exception as e:
            print(f"❌ Background error: {e} | context: {context}")

    asyncio.create_task(wrapper())


async def handle_whatsapp_message(data: dict):
    sender = data.get("From")
    message = data.get("Body")

    if not sender:
        print(f"❌ Invalid webhook payload: {data}")
        return

    thread_id = sender.replace("whatsapp:", "").replace("+", "")

    termination_keywords = ["clear", "end", "close", "exit", "stop"]

    if message and any(word in message.lower() for word in termination_keywords):
        cache.remove(thread_id)
        await send_msg("Chat Ended:", f"whatsapp:+{thread_id}")
    else:
        await run_graph(thread_id, message, cache)


@router.post("/whatsapp_webhook")
async def whatsapp_webhook(request: Request):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)

    run_in_background(
        handle_whatsapp_message(data),
        context={"From": data.get("From"), "Body": data.get("Body")}
    )

    return {"status": "received"}