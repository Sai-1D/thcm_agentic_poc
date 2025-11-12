# src/graph.py
from src.utils.data_loader import load_catalog
from langgraph.graph import StateGraph, END, START
from src.models.state import State
from src.utils.data_loader import load_catalog
from src.agents.orchestrator import orchestrator_node, search_node
from src.agents.disambiguator import disambiguator_node, selector_node
from src.agents.cart_manager import cart_manager_node, order_review_node
from src.agents.payment_agent import payment_agent_node
from src.agents.issue_agent import issue_reporting_node
from src.agents.controller import controller_node, route_from_controller
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
graph.add_node("order_review", order_review_node)
graph.add_node("payment", payment_agent_node)
graph.add_node("issue_reporter", issue_reporting_node)

# Controller node
graph.add_node("controller", controller_node)
graph.add_conditional_edges(
    "controller",
    route_from_controller,
    {
        "issue_reporter": "issue_reporter",
        "search": "search",
        "disambiguator": "disambiguator",
        "selector": "selector",
        "cart_manager": "cart_manager",
        "order_review": "order_review",
        "payment": "payment",
        "end": END
    }
)

# Entry point
graph.set_entry_point("orchestrator")
graph.add_edge("orchestrator", "controller")

# Flow edges
graph.add_edge("disambiguator", "controller")
graph.add_edge("selector", "controller")
graph.add_edge("cart_manager", "controller")
graph.add_edge("order_review", "controller")
graph.add_edge("payment", END)
graph.add_edge("issue_reporter", END)

checkpointer = MemorySaver()   # Use an in-memory checkpointer for testing
app = graph.compile(checkpointer=checkpointer)