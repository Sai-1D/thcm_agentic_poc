# src/services/messaging.py

import os
import asyncio
from twilio.rest import Client
from langgraph.types import Command
from src.models.state import State
from src.graph import app as app_graph

def get_twilio_client():
    """Get Twilio client with current environment variables"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
    return Client(account_sid, auth_token)

def get_from_whatsapp_number():
    """Get from WhatsApp number from current environment variables"""
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    if not whatsapp_number:
        raise ValueError("TWILIO_WHATSAPP_NUMBER must be set")
    return "whatsapp:" + whatsapp_number

async def send_msg(msg: str, number: str):
    client = get_twilio_client()
    from_whatsapp_number = get_from_whatsapp_number()
    await asyncio.to_thread(
        client.messages.create,
        from_=from_whatsapp_number,
        body=msg,
        to=number,
    )

async def send_whatsapp_quotation(
    thread_id: str,
):
    pdf_url = (
        f"https://unrural-trippingly-erick.ngrok-free.dev"
        f"/thcm-agentic-poc/api/quotation/{thread_id}.pdf"
    )
    
    client = get_twilio_client()
    from_whatsapp_number = get_from_whatsapp_number()
    
    await asyncio.to_thread(
        client.messages.create,
        from_=from_whatsapp_number,
        to=f"whatsapp:+{thread_id}",
        body="Your quotation 📄 is ready and attached for your reference.",
        media_url=[pdf_url],
    )

async def run_graph(thread_id, data, cache):
    config = {"configurable": {"thread_id": thread_id}}
    if not cache.exist(thread_id):
        state = State(user_query=data)
        result = app_graph.invoke(state, config=config)
    else:
        cache.update(thread_id, data)
        if cache[thread_id].current_field_index > 0:
            state = State(user_query=data)
            result = app_graph.invoke(state, config=config)
        elif cache[thread_id].current_field_index == 0:
            result = app_graph.invoke(Command(resume=cache[thread_id].resume_data), config=config)
        else:
            field_value = cache.get_field(thread_id)
            msg = (field_value.get("options") or "") +'\n'+ (field_value.get("prompt") or "")
            await send_msg(msg, f"whatsapp:+{thread_id}")
            return

    if "__interrupt__" in result:
        interrupt_value = result["__interrupt__"][0].value
        cache.add(thread_id, interrupt_value)

        field_value = cache.get_field(thread_id)
        msg = (field_value.get("options") or "") +'\n'+ (field_value.get("prompt") or "")
        await send_msg(msg, f"whatsapp:+{thread_id}")
    elif result['buy_state'] == 'QUOTATION' or result['quotation_state'] == 'QUOTATION':
        await send_whatsapp_quotation(thread_id)
    elif result.get('messages'):
        # Handle messages from any agent - send last 2 messages if available, else last message
        messages = result['messages']
        if len(messages) >= 2:
            await send_msg('\n'.join(messages[-2:]), f"whatsapp:+{thread_id}")
        elif len(messages) == 1:
            await send_msg(messages[0], f"whatsapp:+{thread_id}")
        else:
            await send_msg('ENDED ):', f"whatsapp:+{thread_id}")
    else:
        await send_msg('ENDED ):', f"whatsapp:+{thread_id}")
