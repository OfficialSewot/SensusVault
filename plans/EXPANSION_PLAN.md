# SensusVault Expansion Plan: The "Second Brain" Evolution

## 1. Vision & Objective
Transform SensusVault from a basic note-taking tool into an autonomous knowledge engine. The goal is to move from **manual entry** to **intelligent ingestion**, where data is captured in a raw state and automatically processed into a structured, interconnected knowledge graph.

## 2. Current System Architecture Analysis
- **Persistence:** SQLite for relational data (Notes, Graph Nodes/Edges, Action Queue) and ChromaDB for vector embeddings.
- **Agentic Workflow:** LangGraph-based Knowledge Agent that proposes changes via an **Action Queue**.
- **Human-in-the-Loop (HITL):** The `Action Review` system ensures the agent cannot modify the vault without explicit user approval.
- **Retrieval:** Graph-aware RAG that traverses relationships to find contextually relevant notes.

## 3. Expansion Modules

### Module A: The "Inbox" & Ingestion Pipeline
*Current State:* Notes are created directly with metadata.
*Proposed Expansion:*
- **Capture Gateway:** A "Quick Capture" UI for raw text entry with minimal friction (Title/Content only).
- **Ingestion Queue:** New notes enter the system with a `status="raw"`.
- **Automated Processing:** A background worker (or triggered API call) uses the `pre_processor` to:
    - Extract entities via GLiNER.
    - Generate a `content_summary`.
    - Assign mandatory tags (e.g., `#status:raw`, `#source:manual`).
- **Review Loop:** If the LLM/Pre-processor confidence is low, the note is flagged in the UI for manual metadata correction.

### Module B: Multi-Faceted Vault Organization (SubViews)
*Current State:* A single "Vault View" showing all notes.
*Proposed Expansion:* Implement a multi-tab or sidebar navigation for specialized views:
- **Project View:** Filtered by a `project_id` (new mandatory metadata). Groups notes by active workstreams.
- **Research Lab:** A view showing "High-Density" notes—those with the most edges/links in the graph.
- **Quick Capture (Inbox):** A chronological feed of notes with `status="raw"` awaiting processing.
- **Knowledge Graph Visualization:** A visual representation of notes and their relations (using a library like `streamlit-agraph` or similar).

### Module C: Enhanced Knowledge Agent
*Current State:* Agent proposes links, summaries, and deletions.
*Proposed Expansion:*
- **Proactive Connection Logic:** Agent identifies "orphaned" notes (no links) and proposes connections based on semantic similarity or shared entities.
- **Research Proposals:** Agent can propose "Research Tasks" (e.g., "I see you have notes on 'Quantum Computing' but no notes on 'Qubits'. Should I create a research task?").
- **Recursive Summarization:** Agent identifies long notes and proposes breaking them into smaller, linked "Atomic Notes".

### Module D: Auditability & Systemic Actions
*Current State:* Actions are approved/rejected.
*Proposed Expansion:*
- **Action History:** A persistent log of all approved/rejected/completed actions to track the "evolution" of the vault.
- **Execution Logging:** Detailed logs for every system-level change (e.g., "Action X executed: Moved Note Y to Project Z").
- **Scheduled Tasks:** Ability for the agent to propose "Daily Summaries" or "Weekly Review" actions.

## 4. Technical Specifications

### Database Schema Updates
- `notes` table: Add `project_id` (UUID), `status` (TEXT: raw, processed, archived).
- `pending_actions` table: Add `user_feedback` (TEXT) to store why an action was rejected.
- `action_history` table: New table to archive completed actions.

### API Contract Changes
- `POST /notes/capture`: For the raw input gateway.
- `GET /notes/search`: Support for faceted filtering (by project, status, or tag).
- `GET /actions/history`: Retrieve past actions.

### Metadata Requirements (Mandatory)
Every note MUST possess:
1. `source_type` (Web, Manual, AI, Book)
2. `status` (Raw, Processed, Archived)
3. `project_id` (Optional, but required for Project View)
4. `tags` (Minimum 2 tags)

## 5. Implementation Roadmap

### Phase 1: The Ingestion Foundation (Short-term)
- [x] Implement `status` and `project_id` in the database schema.
- [x] Build the "Quick Capture" UI component.
- [x] Connect the `pre_processor` to an automated "Processing" trigger.
- [x] Refactor `app.py` to handle "Raw" vs "Processed" states.

### Phase 2: Advanced Organization (Medium-term)
- [ ] Implement Project and Research SubViews in the UI.
- [ ] Develop the faceted search API.
- [ ] Integrate the "Action History" dashboard.

### Phase 3: Advanced Autonomy (Long-term)
- [ ] Enhance Knowledge Agent with "Connection Logic" and "Research Proposals".
- [ ] Implement recursive note decomposition.
- [ ] Finalize automated execution for simple system tasks.

## 6. Testing Strategy
- **Pipeline Test:** Create 10 "Raw" notes and verify automated processing (tagging, summary generation, entity extraction).
- **Graph Walk Test:** Verify that a query for "Project X" correctly retrieves notes linked via the graph even if they don't contain "Project X" in the title.
- **HITL Test:** Verify that rejected actions do not trigger the execution logic and remain in history.
