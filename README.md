# THCM Agentic POC

```
thcm_agentic_poc/
│
├── .venv/ # Python virtual environment
├── data/
│ └── product_catalog.xlsx # Product catalog spreadsheet
├── src/
│ ├── __init__.py
│ ├── main.py # Console application entry point
│ ├── graph.py # Workflow graph setup
│ ├── agents/ # Node implementations
│ │ ├── __init__.py
│ │ ├── cart_manager.py
│ │ ├── controller.py
│ │ ├── disambiguator.py
│ │ ├── issue_agent.py
│ │ ├── orchestrator.py
│ │ └── payment_agent.py
│ ├── models/ # Core data models
│ │ ├── __init__.py
│ │ ├── product.py # Product dataclass
│ │ └── state.py # Conversation state
│ └── utils/
│ ├── __init__.py
│ ├── cache.py
│ ├── logger.py
│ └── data_loader.py # Load product catalog
│
├── env_example # Example environment variables
├── app.py # Twilio / FastAPI webhook
├── requirements.txt # Pinned dependencies
└── README.md # Project documentation
```

## Setup

```
python -m venv .venv
source .venv/bin/activate      # Linux / Mac
.venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

* Copy env_example → .env and update as needed.

## Running

### Console application

```
python -m src.main
```

### Twilio / FastAPI

```
python app.py
```