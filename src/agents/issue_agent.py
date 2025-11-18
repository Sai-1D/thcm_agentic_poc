# src/agents/issue_agent.py

import uuid
from src.models.state import State
from src.utils.logger import logger

def issue_reporting_node(state: State) -> State:
    logger.debug("[ISSUE_AGENT] Start: %s", state)

    if not state.user_query:
        state.messages.append("No issue description provided.")
        logger.warning("[ISSUE_AGENT] No issue description provided by user.")
        logger.info("[ISSUE_AGENT] End: %s", state)
        return state

    # Simulate ticket creation
    state.issue_description = state.user_query
    state.issue_ticket_id = str(uuid.uuid4())[:8].upper()
    state.messages.append(f"Issue reported: '{state.issue_description}'")
    state.messages.append(f"Ticket ID: {state.issue_ticket_id}")

    logger.info("[ISSUE_AGENT] Issue reported: %s", state.issue_description)
    logger.info("[ISSUE_AGENT] Ticket ID: %s", state.issue_ticket_id)
    logger.debug("[ISSUE_AGENT] End: %s", state)
    return state
