# src/services/messaging.py

import os
import asyncio
from twilio.rest import Client
from langgraph.types import Command
from src.models.state import State
from src.graph import app as app_graph

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_whatsapp_number = "whatsapp:" + os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)

async def send_msg(msg: str, number: str):
    await asyncio.to_thread(
        client.messages.create,
        from_=from_whatsapp_number,
        body=msg,
        to=number,
    )

async def run_graph(thread_id, data, cache):
    config = {"configurable": {"thread_id": thread_id}}
    if not cache.exist(thread_id):
        state = State(user_query=data)
        result = app_graph.invoke(state, config=config)
    else:
        cache.update(thread_id, data)

        if cache[thread_id].current_field_index == 0:
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
    else:
        msg = result['messages'][-1] + '\n' + result['messages'][-2]
        await send_msg(msg, f"whatsapp:+{thread_id}")