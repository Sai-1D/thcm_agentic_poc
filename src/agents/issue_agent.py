# src/agents/issue_agent.py
import uuid
from src.models.state import State

def issue_reporting_node(state: State) -> State:
    if not state.user_query:
        state.messages.append("No issue description provided.")
        return state

    # Simulate ticket creation
    state.issue_description = state.user_query
    state.issue_ticket_id = str(uuid.uuid4())[:8].upper()
    state.messages.append(f"Issue reported: '{state.issue_description}'")
    state.messages.append(f"Ticket ID: {state.issue_ticket_id}")
    return state