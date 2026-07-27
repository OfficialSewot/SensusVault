import streamlit as st
import requests
import logging
import sys

# Configure logging to output to standard output
# Use force=True to override any existing configuration (Python 3.8+)
try:
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True
    )
except TypeError:
    # Fallback for Python < 3.8
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


import pandas as pd
from typing import List

# Configuration
# Use the environment variable for API_BASE_URL, defaulting to localhost:2200
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:2200")

st.set_page_config(
    page_title="SensusVault - Second Brain",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 SensusVault")
st.markdown("---")

# Sidebar for navigation
menu = st.sidebar.selectbox("Navigation", ["Vault View", "Quick Capture", "Inbox Feed", "Project View", "Knowledge Graph", "Action Review", "DEBUG: Delete Note"])

def fetch_actions() -> List[dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/actions")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching actions: {e}")
        return []

def fetch_notes() -> List[dict]:
    """Fetches all notes from the database."""
    try:
        response = requests.get(f"{API_BASE_URL}/notes")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching notes: {e}")
        return []

if menu == "Vault View":
    st.header("📖 Vault View")
    st.write("Browse your organized knowledge.")
    
    notes = fetch_notes()
    if notes:
        # Display notes in a table
        df = pd.DataFrame([
            {
                "ID": note.get("id"),
                "Title": note.get("metadata", {}).get("title"),
                "Tags": ", ".join(note.get("metadata", {}).get("tags", [])),
                "Summary": note.get("metadata", {}).get("content_summary")
            } for note in notes
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No notes found in the vault.")

elif menu == "Quick Capture":
    st.header("⚡ Quick Capture")
    st.write("Capture a new note quickly.")
    
    with st.form("capture_form", clear_on_submit=True):
        title = st.text_input("Title")
        content = st.text_area("Content")
        project_id = st.text_input("Project ID (Optional)")
        submitted = st.form_submit_button("Capture")
        
        if submitted:
            if title and content:
                payload = {
                    "title": title,
                    "content": content,
                    "project_id": project_id if project_id else None
                }
                res = requests.post(f"{API_BASE_URL}/notes/capture", json=payload)
                if res.status_code == 200:
                    st.success("Note captured!")
                else:
                    st.error(f"Error capturing note: {res.text}")
            else:
                st.warning("Title and Content are required.")

elif menu == "Inbox Feed":
    st.header("📥 Inbox Feed")
    st.write("Notes awaiting processing.")
    
    notes = fetch_notes()
    # Filter notes with status 'raw'
    inbox_notes = [n for n in notes if n.get("metadata", {}).get("status") == "raw"]
    
    if inbox_notes:
        df = pd.DataFrame([
            {
                "ID": note.get("id"),
                "Title": note.get("metadata", {}).get("title"),
                "Tags": ", ".join(note.get("metadata", {}).get("tags", [])),
                "Summary": note.get("metadata", {}).get("content_summary")
            } for note in inbox_notes
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Inbox is empty.")

elif menu == "Project View":
    st.header("📂 Project View")
    st.write("Filter notes by project.")
    
    # Get unique project IDs from all notes
    notes = fetch_notes()
    project_ids = list(set(n.get("metadata", {}).get("project_id") for n in notes if n.get("metadata", {}).get("project_id")))
    
    selected_project = st.selectbox("Select Project", ["None"] + project_ids)
    
    if selected_project and selected_project != "None":
        filtered_notes = [n for n in notes if n.get("metadata", {}).get("project_id") == selected_project]
        if filtered_notes:
            df = pd.DataFrame([
                {
                    "ID": note.get("id"),
                    "Title": note.get("metadata", {}).get("title"),
                    "Tags": ", ".join(note.get("metadata", {}).get("tags", [])),
                    "Summary": note.get("metadata", {}).get("content_summary")
                } for note in filtered_notes
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No notes for this project.")
    else:
        st.info("Select a project to see its notes.")

elif menu == "Knowledge Graph":
    st.header("🕸️ Knowledge Graph")
    st.write("Visualize the connections between your notes.")
    
    try:
        response = requests.get(f"{API_BASE_URL}/graph")
        response.raise_for_status()
        data = response.json()
        
        # WICHTIG: Hier importieren wir Node, Edge und Config direkt mit
        from streamlit_agraph import agraph, Node, Edge, Config
        
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        
        # Prepare nodes
        formatted_nodes = []
        for node in nodes:
            if not node:
                continue
            
            if isinstance(node, dict):
                node_id = str(node.get("id", ""))
                metadata = node.get("metadata", {})
            else:
                node_id = str(getattr(node, "id", ""))
                metadata = getattr(node, "metadata", {}) or {}
            
            # FIX: Wir nutzen die echte 'Node'-Klasse der Bibliothek
            formatted_nodes.append(Node(
                id=node_id,
                label=metadata.get("title", "Unnamed Note"),
                size=20, # Etwas größer für bessere Lesbarkeit
                shape="dot"
            ))
        
        # Prepare edges
        formatted_edges = []
        for edge in edges:
            # FIX: Wir nutzen die echte 'Edge'-Klasse der Bibliothek
            formatted_edges.append(Edge(
                source=edge["source"],
                target=edge["target"],
                label=edge["relation"]
            ))
        
        # Config definieren für das Layout (verhindert Darstellungsfehler)
        config = Config(
            width="100%",
            height=600,
            directed=True, 
            physics=True, 
            hierarchical=False
        )
        
        # Graph rendern
        agraph(nodes=formatted_nodes, edges=formatted_edges, config=config)
        
    except Exception as e:
        st.error(f"Error rendering Knowledge Graph: {e}")
        st.info("Ensure 'streamlit-agraph' is installed and the API is reachable.")

elif menu == "Action Review":
    st.header("⚖️ Action Review")
    st.write("Review and approve actions proposed by the Knowledge Agent.")
    
    actions = fetch_actions()
    if actions:
        for action in actions:
            with st.expander(f"Action: {action['type']} ({action['id']})"):
                st.json(action['payload'])
                col1, col2 = st.columns(2)
                
                if col1.button("Approve", key=f"app_{action['id']}"):
                    res = requests.post(f"{API_BASE_URL}/actions/{action['id']}/approve")
                    if res.status_code == 200:
                        st.success("Action approved!")
                        st.rerun()
                    else:
                        st.error("Failed to approve.")
                        
                if col2.button("Reject", key=f"rej_{action['id']}"):
                    res = requests.post(f"{API_BASE_URL}/actions/{action['id']}/reject")
                    if res.status_code == 200:
                        st.warning("Action rejected.")
                        st.rerun()
    else:
        st.success("No pending actions.")

if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []

elif menu == "DEBUG: Delete Note":
    if st.button("Clear Logs"):
        st.session_state.debug_logs = []
        st.rerun()

    st.error("⚠️ WARNING: DEBUG TOOL - PERMANENT DELETION")
    st.markdown("### This tool will permanently remove a note from the database and vector store.")
    st.warning("Use this ONLY for debugging purposes. Data recovery is not possible.")
    
    notes = fetch_notes()
    if notes:
        note_options = {note['id']: note['metadata'].get('title', 'No Title') for note in notes}
        selected_id = st.selectbox("Select Note ID to Delete", options=list(note_options.keys()),
                                    format_func=lambda x: f"{x} - {note_options[x]}")
        
        # 1. State für die Bestätigung initialisieren
        if "show_delete_confirm" not in st.session_state:
            st.session_state.show_delete_confirm = False

        # 2. Erster Button setzt den State auf True
        if st.button("PROCEED WITH DELETION", type="primary", use_container_width=True):
            st.session_state.show_delete_confirm = True
            st.rerun() # UI sofort aktualisieren

        # 3. Wenn State True ist, zeige die Bestätigung an
        if st.session_state.show_delete_confirm:
            st.warning(f"Are you absolutely sure you want to delete {selected_id}?")
            col1, col2 = st.columns(2)
            
            # Bestätigen
            if col1.button("✔️ CONFIRM PERMANENT DELETION", type="primary"):
                try:
                    log_msg = f"Attempting to delete note {selected_id}"
                    logging.info(log_msg)
                    st.session_state.debug_logs.append(f"INFO: {log_msg}")
                    
                    res = requests.delete(f"{API_BASE_URL}/notes/{selected_id}")
                    
                    log_msg = f"Delete request returned status {res.status_code}"
                    logging.info(log_msg)
                    st.session_state.debug_logs.append(f"INFO: {log_msg}")
                    
                    st.session_state.debug_logs.append(f"DEBUG: Response body: {res.text}")

                    if res.status_code == 200:
                        st.success(f"Note {selected_id} deleted successfully.")
                    elif res.status_code == 404:
                        st.error(f"Error: Note {selected_id} not found.")
                    else:
                        st.error(f"Failed to delete. Status Code: {res.status_code}")
                        st.error(f"Response: {res.text}")
                
                except Exception as e:
                    log_msg = f"Error during deletion of note {selected_id}: {str(e)}"
                    logging.exception(log_msg)
                    st.session_state.debug_logs.append(f"ERROR: {log_msg}")
                    st.error(f"An unexpected error occurred: {str(e)}")
                
                # Nach Abschluss den State zurücksetzen
                st.session_state.show_delete_confirm = False
                # Wir verzichten hier kurz auf st.rerun(), damit du die Erfolgs-/Fehlermeldung noch lesen kannst.
            
            # Abbrechen
            if col2.button("❌ CANCEL"):
                st.session_state.show_delete_confirm = False
                st.rerun()
    else:
        st.info("No notes available to delete.")

    st.markdown("---")
    st.subheader("📜 Debug Logs")
    if "debug_logs" in st.session_state and st.session_state.debug_logs:
        st.code("\n".join(st.session_state.debug_logs))
    else:
        st.info("No logs yet.")