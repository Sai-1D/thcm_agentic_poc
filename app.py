import os
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from twilio.rest import Client
from langgraph.types import Command
from src.models.state import State
from src.graph import app as app_graph
from src.utils.cache import Cache

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_whatsapp_number = "whatsapp:" + os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)
fastapi_app = FastAPI()
cache = Cache()

async def send_msg(msg: str, number: str):
    await asyncio.to_thread(
        client.messages.create,
        from_=from_whatsapp_number,
        body=msg,
        to=f"whatsapp:+{number}",
    )

async def run_graph(thread_id, data):
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
            await send_msg(msg, thread_id)
            return

    if "__interrupt__" in result:
        interrupt_value = result["__interrupt__"][0].value
        cache.add(thread_id, interrupt_value)

        field_value = cache.get_field(thread_id)
        msg = (field_value.get("options") or "") +'\n'+ (field_value.get("prompt") or "")
        await send_msg(msg, thread_id)
    else:
        msg = result['messages'][-1] + '\n' + result['messages'][-2]
        await send_msg(msg, thread_id)

@fastapi_app.post("/whatsapp_webhook")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    data = dict(form)

    sender = data.get("From")
    message = data.get("Body")
    thread_id = sender.replace("whatsapp:", "").replace("+", "")

    termination_keywords = ["clear", "end", "close", "exit", "stop"]
    if message and any(word in message.lower() for word in termination_keywords):
        cache.remove(thread_id)
        await send_msg("Chat Ended:)", thread_id)
    else:
        await run_graph(thread_id, message)


if __name__ == "__main__":
    uvicorn.run(
        "app:fastapi_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
