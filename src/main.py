# src/main.py
from langgraph.graph import StateGraph, END, START
from src.models.state import State
from src.utils.data_loader import load_catalog
from src.agents.orchestrator import orchestrator_node, search_node
from src.agents.disambiguator import disambiguator_node, selector_node
from src.agents.cart_manager import cart_manager_node
from src.agents.payment_agent import payment_agent_node
from src.agents.issue_agent import issue_reporting_node
from src.agents.controller import controller_node, route_from_controller, pause_node, should_continue

products = load_catalog("data/product_catalog.xlsx")
print("Products loaded: ", len(products))

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
graph.add_conditional_edges("controller", route_from_controller)

# Entry point
graph.set_entry_point("orchestrator")
graph.add_edge("orchestrator", "controller")

# Flow edges
graph.add_edge("search", "controller")
graph.add_edge("disambiguator", "controller")
graph.add_edge("selector", "controller")
graph.add_edge("cart_manager", "controller")
graph.add_edge("pause", "controller")  
graph.add_edge("payment", END)
graph.add_edge("issue_reporter", END)
graph.add_edge("pause", END)

# Compile graph
app = graph.compile()




def run_loop():
    state = State()

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        if state.matched_products and not state.selected_products:
            state.selected_product_code = user_input.strip()
        else:
            state.user_query = user_input.strip()
            state.selected_product_code = None
            state.selected_products.clear()
            state.matched_products.clear()
            state.messages.clear()

        result_dict = app.invoke(state)
        state = State(**result_dict)

        for msg in state.messages:
            print("Bot:", msg)

        if state.payment_status == "authorized" or state.issue_ticket_id:
            print("Conversation complete.")
            break


if __name__ == "__main__":
    run_loop()