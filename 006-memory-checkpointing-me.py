from __future__ import annotations
import os
from typing import TypedDict, Annotated, NotRequired
import logging

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI

# Connfigure the Logging only for Errors. You can change to INFO to see all the logs
logging.basicConfig(level=logging.ERROR)

# create the MemoryState: To store all the conversational history
class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]
    user_name: NotRequired[str]

# Create the Node for Communication: Communicate
def communicate(state: MemoryState) -> dict:
    """
    This node simply takes the query input from the user
    and start the conversation with AI
    """
    logging.info("Communicating...")

    # Get all the messages
    messages = state["messages"]

    # Initiate the LLM
    llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.5)
    response = llm.invoke(messages)

    logging.info("LLM Call Finished")
    print("AI: ", getattr(response, "content"))

    return {
        "messages": [response]
    }

# Create the State Graph
logging.info("Initiating the StateGraph")
graph_builder = StateGraph(state_schema=MemoryState)

# Add the node
logging.info("Adding Node to Graph")
graph_builder.add_node("communicate", communicate)

# Add the flow
logging.info("Creating the edges")
graph_builder.add_edge(START, "communicate")
graph_builder.add_edge("communicate", END)

# Create the checkpointer
checkpointer = MemorySaver()
logging.info("Checkpointer Created")

graph = graph_builder.compile(checkpointer=checkpointer)
logging.info("Graph Compilation Done")

if __name__ == "__main__":

    # lets initate the chat
    print("Starting Chat 1")

    config1 = {"configurable": {"thread_id": "thread-001"}}

    should_chat = 0
    while should_chat < 3:
        query = input("You: ")
        if query == "exit":
            break
        response = graph.invoke({
            "messages": [{
                "role": "user",
                "content": query
            }]
        }, config=config1)
        should_chat += 1

    print("Chat 1 closed!!")

    print("Starting Chat 2")

    config2 = {"configurable": {"thread_id": "thread-002"}}

    should_chat = 0
    while should_chat < 3:
        query = input("You: ")
        if query == "exit":
            break
        response = graph.invoke({
            "messages": [{
                "role": "user",
                "content": query
            }]
        }, config=config2)
        should_chat += 1

    print("Chat 2 closed!!")

    # lets continue our Chat 1
    print("Re-starting Chat 1")

    config1 = {"configurable": {"thread_id": "thread-001"}}

    should_chat = 0
    while should_chat < 3:
        query = input("You: ")
        if query == "exit":
            break
        response = graph.invoke({
            "messages": [{
                "role": "user",
                "content": query
            }]
        }, config=config1)
        should_chat += 1

    print("Chat 1 closed!!")

