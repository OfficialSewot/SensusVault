from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.agent.tools import AgentTools
from src.database.manager import DatabaseManager
from src.llm.factory import LLMFactory
import json

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]

class KnowledgeAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.tools = AgentTools(db_manager)
        
        # Define tools for LangChain/LangGraph
        self.langchain_tools = [
            StructuredTool.from_function(
                func=self.tools.create_note,
                name="create_note",
                description="Creates a new note in the vault. Requires content, title, source, and tags."
            ),
            StructuredTool.from_function(
                func=self.tools.delete_note,
                name="delete_note",
                description="Proposes the deletion of a note. Requires note_id."
            ),
            StructuredTool.from_function(
                func=self.tools.update_metadata,
                name="update_metadata",
                description="Proposes a metadata update for a note. Requires note_id and a dictionary of metadata."
            ),
            StructuredTool.from_function(
                func=self.tools.generate_graph_link,
                name="generate_graph_link",
                description="Proposes a new link between two notes in the knowledge graph."
            ),
            StructuredTool.from_function(
                func=self.tools.summarize_note,
                name="summarize_note",
                description="Proposes a summary for a note. Requires note_id."
            ),
        ]
        
        # Use the Factory to get the provider
        self.provider = LLMFactory.get_provider()
        self.llm_with_tools = self.provider.bind_tools(self.langchain_tools)

        # Build the graph
        builder = StateGraph(AgentState)
        
        builder.add_node("oracle", self.call_model)
        builder.add_node("tools", ToolNode(self.langchain_tools))
        
        builder.set_entry_point("oracle")
        builder.add_edge("oracle", "tools")
        builder.add_edge("tools", "oracle")
        
        self.graph = builder.compile()

    def call_model(self, state: AgentState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def run(self, user_input: str) -> str:
        """
        Runs the knowledge agent and returns the final response.
        """
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        final_state = self.graph.invoke(initial_state)
        
        # Extract the last message's content
        last_message = final_state["messages"][-1]
        
        # Check if the last message is a tool call that needs HITL
        # In our current implementation, tools like create_note, delete_note,
        # update_metadata, and generate_graph_link already add to the Action Queue.
        # The agent's response to the user should reflect that the action was proposed.
        
        return last_message.content
