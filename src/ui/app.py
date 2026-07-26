import streamlit as st
import requests
import pandas as pd
from typing import List

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SensusVault - Second Brain",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 SensusVault")
st.markdown("---")

# Sidebar for navigation
menu = st.sidebar.selectbox("Navigation", ["Vault View", "Action Review"])

def fetch_actions() -> List[dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/actions")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching actions: {e}")
        return []

def fetch_notes() -> List[dict]:
    # For now, we'll use a dummy query to get notes if a specific endpoint doesn't exist
    # Or we can add a /notes endpoint to the API.
    # Let's assume for now we might want to add one, but I'll stick to the plan.
    # Actually, I'll try to call /query with a dummy embedding.
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query_text": "all", "top_k": 100, "walk_depth": 1}
        )
        response.raise_for_status()
        return response.json().get("results", [])
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
                "Title": note.get("title"),
                "Tags": ", ".join(note.get("tags", [])),
                "Summary": note.get("content_summary")
            } for note in notes
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No notes found in the vault.")

elif menu == "Action Review":
    st.header("⚖️ Action Review")
    st.write("Review and approve actions proposed by the Knowledge Agent.")
    
    actions = fetch_actions()
    if actions:
        if not actions:
            st.success("No pending actions.")
        else:
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
