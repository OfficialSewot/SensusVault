# Deployment & User Testing Guide

This guide provides instructions for deploying SensusVault and performing initial user testing.

## 🚀 Deployment

### 1. Infrastructure Setup
Ensure your Docker environment is ready. Run the following command to start the core services:
```bash
docker-compose up -d
```
This will start:
- **ChromaDB**: Vector database for semantic search.
- **SQLite**: Relational database for graph and metadata.
- **Llama-Swap**: Local LLM inference engine.

### 2. Environment Configuration
Verify your `.env` file has the correct local paths and keys.
```bash
cp .env.example .env
```

### 3. Dependencies
Install the Python requirements:
```bash
pip install -r requirements.txt
```

### 4. Run the API
Start the FastAPI backend:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 5. Launch the Web UI
Start the Streamlit dashboard:
```bash
streamlit run src/ui/app.py
```

## 🧪 User Testing Plan

Perform the following tests to ensure the system meets the objectives:

### Test 1: Ingestion & Sync
1. Add a new PDF or Markdown file to the `Inbox` folder.
2. Verify that the `Ingestor` processes the file and creates a new entry in the `Vault`.
3. Check the `SQLite` graph to ensure entities were extracted and linked correctly.

### Test 2: Graph-Aware Retrieval
1. Query the system with a question that requires multi-hop reasoning (e.g., "Who are the stakeholders for Project X?").
2. Verify that the results include relevant entities linked via the graph, not just textually similar notes.

### Test 3: Agentic Autonomy & HITL
1. Trigger a knowledge curation task (e.g., "Organize my notes on Project Y").
2. Observe the `Action Review` queue in the Streamlit UI.
3. Approve a proposed link or tag and verify that the change persists in the `Vault`.

### Test 4: OpenWebUI Integration
1. Connect the SensusVault tool to OpenWebUI.
2. Ask a natural language question in the OpenWebUI chat.
3. Verify that the tool correctly fetches data from the `Vault` and presents it.
