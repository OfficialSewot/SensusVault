# SensusVault v2.1: Autonomous Second Brain & Knowledge Engine

SensusVault is a local-first, private knowledge management system designed to function as a "Second Brain" for individuals and a high-context Knowledge Base for local Large Language Models (LLMs).

## 🚀 Key Features

- **100% Local & Private:** No data ever leaves your machine. All processing, storage, and LLM inference happen locally.
- **Agentic Autonomy:** AI agents (built with LangGraph) automatically organize, link, and curate your knowledge.
- **Graph-Aware RAG:** Goes beyond simple similarity search by performing "Graph-Walks" to retrieve related entities and contextual connections.
- **Human-in-the-Loop (HITL):** Critical system mutations (like file moves or deletions) are proposed by the agent and require user approval via an Action Queue.
- **ACID-like Consistency:** Uses a "Delete-then-Insert" strategy with UUIDs to ensure that metadata, vector indices, and graph relationships remain perfectly synchronized.

## 🏗️ Architecture

- **Persistence Layer:**
    - **Source of Truth:** Markdown files.
    - **Vector Store:** ChromaDB (Semantic Search).
    - **Graph Store:** SQLite-backed Adjacency List (Atomic Transactions).
- **Processing Layer:**
    - **Tri-State Workflow:** Inbox $\rightarrow$ Processing $\rightarrow$ Vault.
    - **Hybrid NER:** Uses lightweight models (GLiNER) for entity extraction, reserving the LLM for complex reasoning.
- **Agentic Layer:**
    - **LangGraph Agent:** Handles cyclic knowledge curation.
    - **Action Queue:** Manages proposed mutations with a review UI.
- **Interaction Layer:**
    - **Streamlit UI:** Dashboard for vault viewing and action review.
    - **FastAPI Gateway:** API for integration with tools like OpenWebUI.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **Orchestration:** LangChain / LangGraph
- **Vector Database:** ChromaDB
- **Relational Database:** SQLite
- **API Framework:** FastAPI
- **UI Framework:** Streamlit
- **LLM Inference:** `llama-swap` (llama.cpp)

## 🚦 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- `llama.cpp` (via `llama-swap`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SensusVault.git
   cd SensusVault
   ```
2. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your local paths and keys
   ```
3. Start the infrastructure:
   ```bash
   docker-compose up -d
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the API:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```
6. Launch the UI:
   ```bash
   streamlit run src/ui/app.py
   ```

## 🗺️ Roadmap
- [x] Foundation (Ingestion & Sync)
- [x] Brain (Graph-Aware RAG)
- [x] Secretary (Autonomy & HITL)
- [x] Face (UI & Integration)
- [ ] Deployment & User Testing

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
