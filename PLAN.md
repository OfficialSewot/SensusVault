# Project SensusVault v2.1: Autonomous Second Brain & Knowledge Engine

## 1. Vision & Objectives
- **Core Purpose:** A local-first, private knowledge management system that functions as a "Second Brain" for the user and a high-context Knowledge Base for local LLMs.
- **Key Goals:**
    - **Privacy:** 100% local execution (No cloud data leaks).
    - **Autonomy:** AI agents that can organize, link, and curate knowledge automatically.
    - **Portfolio-Ready:** A modular, high-quality GitHub repository demonstrating senior-level system design (Graph-Aware RAG, Agentic Workflows, ACID-like consistency).
    - **Interoperability:** Accessible via a custom UI and as a Tool/API for OpenWebUI.
    - **Knowledge Integrity:** Ensuring data quality through a structured "Inbox-to-Vault" pipeline.

## 2. System Architecture (High-Level)
The system is divided into decoupled modules to allow for "Context-Limited Vibe Coding".

### Layer 1: Persistence Layer (The Vault)
*   **Source of Truth:** Local Markdown files (Human-readable, Git-versionable).
*   **Vector Store:** **ChromaDB** (Local instance for semantic search).
*   **Graph Store:** **SQLite-backed Adjacency List.**
    *   *Architectural Decision:* We forgo Neo4j (too heavy) and NetworkX (no persistence). By using SQLite to store nodes and edges, we achieve **Atomic Transactions**. This allows us to update metadata, vector indices, and graph relationships in a single logical transaction, preventing state drift.
*   **Graph-Aware Retrieval:** RAG queries will perform a "Graph-Walk" to fetch related entities (e.g., "Find all notes related to 'Project X' and their associated 'Stakeholders'") rather than just similarity.

### Layer 2: Processing Layer (The Ingestor & Sync Engine)
*   **Tri-State Workflow:**
    *   **Inbox:** Raw data (PDFs, web-scrapes, messy notes).
    *   **Processing:** Cleaning, entity extraction, and chunking. Uses a **Hybrid NER Approach** (e.g., GLiNER or SpaCy) for fast, lightweight entity extraction without waking the large LLM, reserving the LLM for complex graph relations.
    *   **Vault:** Final, structured, and indexed markdown files with structured YAML frontmatter.
*   **State Syncing (CRUD Consistency):**
    *   Every note is assigned a unique `UUID`.
    *   **Update Logic:** When a file change is detected via the `Watcher`, the Ingestor performs a **"Delete-then-Insert"** operation for that UUID in both ChromaDB and the SQLite Graph. This ensures that old, stale embeddings/edges never persist.
*   **Pre-Processor:** Handling multi-modal input (OCR for images/PDFs via Tesseract/PyMuPDF).
*   **Watcher:** Monitors folder changes for real-time ingestion.

### Layer 3: Agentic Layer (The "Engine")
*   **Knowledge Agent:** A **LangGraph**-based agent designed for *cyclic* knowledge curation (Think -> Act -> Observe).
    *   *Scope Constraint:* To maintain "Atomic Simplicity," the agent is restricted to **Knowledge Curation only** (tagging, linking, summarizing). It does not manage the system's core files or OS.
*   **Toolbox:** `create_note`, `delete_note`, `update_metadata`, `generate_graph_link`.
*   **Human-in-the-Loop (HITL) via Action Queue:**
    *   Agentic actions that modify the file system (e.g., moving a file) are not executed immediately.
    *   The agent writes a "Proposed Action" to a `pending_actions` table in SQLite.
    *   The UI/User reviews this queue and "approves" or "rejects" the action, triggering the actual file system mutation.

### Layer 4: Interaction Layer
*   **Web UI:** Streamlit/Next.js dashboard featuring the "Vault View" and the "Action Review" queue.
*   **API Gateway:** FastAPI endpoints providing a `/query` (RAG) and `/actions` (HITL management) for OpenWebUI tool integration.

## 3. Tech Stack & Hardware Strategy
- **Language:** Python 3.12+
- **LLM Inference:** `llama-swap` (llama.cpp) with partial RAM offloading.
    *   *Model Strategy:* Given the hardware constraints (approx. 13 GB free VRAM after Windows overhang and 36 GB free system RAM after Docker/OS deductions), a 12B model like gemma4-12b fits purely in VRAM but lacks the reasoning/coding capabilities needed for agentic tasks. We will use a larger, more capable model, offloading the extra layers to the system RAM. This is viable because the agent uses the offloaded layers only in short bursts during reasoning.
- **Orchestration:** LangChain / LangGraph
- **Database:** ChromaDB (Vector), SQLite (Metadata & Graph)
- **API:** FastAPI
- **Containerization:** Docker & Docker Compose

## 4. Module Roadmap (Phase-based)

### Phase 1: The Foundation (Ingestion & Sync)
- [x] Setup Docker environment (ChromaDB, SQLite, llama-swap).
- [x] Build `Pre-Processor` (PDF/OCR).
- [x] Build `Ingestor` with **Atomic Sync** (UUID-based Delete-then-Insert).
- [x] Implement basic Metadata extraction (Tags, Title, Date).

### Phase 2: The Brain (Graph-Aware RAG)
- [x] Build `QueryEngine` with **Graph-Walk** logic.
- [x] Implement **Hybrid Entity Extraction (NER)**: Use a lightweight NLP model (like GLiNER) to populate the SQLite Graph efficiently, preventing the large LLM from bottlenecking the ingestion pipeline.
- [x] Create FastAPI Wrapper for the Query Engine.
- [x] **Evaluation:** Implement a "Golden Set" of 50 questions to measure Hit Rate (Retrieval accuracy).

### Phase 3: The Secretary (Autonomy & HITL)
- [x] Build the `Knowledge Agent` using LangGraph.
- [x] Implement the `Action Queue` and `HITL` logic.
- [x] Integrate "Self-Organization" (Agent suggests links based on Graph-proximity).

### Phase 4: The Face (UI & Integration)
- [ ] Build the Streamlit Web UI with "Action Review" queue.
- [ ] Create the OpenWebUI Tool definition (JSON/Python).
- [ ] Final Polish & Documentation for GitHub.
- [ ] Deployment & User Testing.

## 5. Development Principles
- **Atomic Modules:** Each script must do one thing.
- **Contract-based Coding:** Define inputs/outputs clearly before coding the logic.
- **Full File Delivery:** Always provide complete files for seamless copy-pasting.
- **Local-First:** Any external dependency must be containerized or local.
- **Consistency First:** The Markdown file is the source of truth; DBs are projections.
