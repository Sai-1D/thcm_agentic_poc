# src/main.py
from langgraph.graph import StateGraph, END, START
from src.models.state import State
from langgraph.types import Command
from src.utils.data_loader import load_catalog
from src.agents.orchestrator import orchestrator_node, search_node
from src.agents.disambiguator import disambiguator_node, selector_node
from src.agents.cart_manager import cart_manager_node
from src.agents.payment_agent import payment_agent_node
from src.agents.issue_agent import issue_reporting_node
from src.agents.controller import controller_node, route_from_controller, pause_node
from langgraph.checkpoint.memory import MemorySaver

products = load_catalog("data/product_catalog.xlsx")

# Build graph
graph = StateGraph(State)

# Core nodes
graph.add_node("orchestrator", orchestrator_node)
graph.add_node("search", lambda s: search_node(s, products))
graph.add_node("disambiguator", disambiguator_node)
graph.add_node("selector", selector_node)
graph.add_node("cart_manager", cart_manager_node)
graph.add_node("payment", payment_agent_node)
graph.add_node("issue_reporter", issue_reporting_node)
graph.add_node("pause", pause_node)

# Controller node
graph.add_node("controller", controller_node)
graph.add_conditional_edges(
    "controller",
    route_from_controller,
    {
        "issue_reporter": "issue_reporter",
        "search": "search",
        "disambiguator": "disambiguator",
        "pause": "pause",
        "selector": "selector",
        "cart_manager": "cart_manager",
        "payment": "payment",
    }
)

# Entry point
graph.set_entry_point("orchestrator")
graph.add_edge("orchestrator", "controller")

# Flow edges
graph.add_edge("disambiguator", "controller")
graph.add_edge("selector", "controller")
graph.add_edge("cart_manager", "controller")
graph.add_edge("payment", END)
graph.add_edge("issue_reporter", END)
graph.add_edge("pause", END)

checkpointer = MemorySaver()   # Use an in-memory checkpointer for testing
app = graph.compile(checkpointer=checkpointer)

state = State()
user_input = input("\n\nUser: ")
state.user_query = user_input.strip()

config = {"configurable": {"thread_id": "session-001"}}
result = app.invoke(state, config=config)
while "__interrupt__" in result:
    interrupt_value = result["__interrupt__"][0].value
    interrupt_type = interrupt_value["type"]

    if interrupt_type == "product_selection":
        print(interrupt_value["question"])
        print(interrupt_value["options"])
        user_choice = input("Enter article number: ").strip()
        result = app.invoke(Command(resume={"article_number": user_choice}), config=config)

    elif interrupt_type == "payment_info":
        print(interrupt_value["question"])
        card_number = input("Enter card number: ").strip()
        cvv = input("Enter CVV: ").strip()
        result = app.invoke(Command(resume={"card_number": card_number, "cvv": cvv}), config=config)
    else:
        print("Unknown Interrupt")
        break

print(State(**result))