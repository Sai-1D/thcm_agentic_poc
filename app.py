# app.py
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.models.state import State
from langgraph.types import Command
from src.graph import app as app_graph

fastapi_app = FastAPI()

# Request model
class RunGraphRequest(BaseModel):
    thread_id: str
    user_query: str = None          # required only for new sessions
    resume_data: dict = None        # optional for resuming

@fastapi_app.post("/run_graph")
def run_graph(request: RunGraphRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    if request.resume_data:
        # Resume graph with provided data
        result = app_graph.invoke(Command(resume=request.resume_data), config=config)
    else:
        # Start new graph session
        if not request.user_query:
            return {"error": "user_query is required for new sessions"}
        state = State(user_query=request.user_query)
        result = app_graph.invoke(state, config=config)

    # Check if graph paused for input
    if "__interrupt__" in result:
        interrupt_value = result["__interrupt__"][0].value
        return {
            "thread_id": request.thread_id,
            "interrupt": interrupt_value
        }

    return {
        "thread_id": request.thread_id,
        "result": result
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:fastapi_app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )