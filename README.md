#setup venv and install requirements. 

#Folder Structure

thcm_agentic_poc/
│
├── .venv/                  # virtual environment
├── data/
│   └── product_catalog.xlsx # your THCM spreadsheet
├── src/
│   ├── __init__.py
│   ├── main.py              # entry point (terminal loop)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── catalog_search.py
│   │   ├── cart_manager.py
│   │   ├── payment_agent.py
│   │   └── order_processor.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py       # dataclass for product
│   │   └── state.py         # conversation state
│   └── utils/
│       ├── __init__.py
│       └── data_loader.py   # parse spreadsheet
│
├── requirements.txt         # pinned dependencies
└── README.md                # project notes



## Basic graph nodes and transitons

# Build graph
graph = StateGraph(State)
graph.add_node("orchestrator", orchestrator_node)
graph.add_node("search", lambda s: search_node(s, products))
graph.add_node("disambiguator", disambiguator_node)
graph.add_node("selector", selector_node)
graph.add_node("cart_manager", cart_manager_node)
graph.add_node("payment", payment_agent_node)
graph.add_node("issue_reporter", issue_reporting_node)

# Define transitions
graph.add_edge(START, "orchestrator")
graph.add_conditional_edges(
    "orchestrator",
    lambda s: "search" if s.intent == "buy" else "issue_reporter" if s.intent == "issue" else "orchestrator"
)


#Product flow
graph.add_edge("search", "disambiguator")
graph.add_edge("disambiguator", "selector")
graph.add_edge("selector", "cart_manager")
graph.add_edge("cart_manager", "payment")
graph.add_edge("payment", END)

#Issue flow
graph.add_edge("issue_reporter", END)
app = graph.compile()
