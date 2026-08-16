from __future__ import annotations
from typing import TypedDict, Any, Literal, NotRequired, Annotated
import os
import logging

# configure the logging
logging.basicConfig(
    level=logging.INFO
 )

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

# Define LLM and its configurations
from langchain_openai import ChatOpenAI

base_llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""), model="gpt-4o-mini", temperature=0)

# Define the application state
class SystemState(TypedDict):
    messages: Annotated[list, add_messages]
    route: NotRequired[Literal["tools", "final"]]
    summary: NotRequired[str]

# Here, LangGraph provides the wrapper for easy tool preparation
@tool
def fetch_customer_info(customer_id: str) -> dict:
    """
    This tool fetches the customer information.
    
    Args:
        - customer_id (str): A unique customer identifier
    
    Returns:
        - info (dict): Dictionary object with customer information
    """
    if not customer_id:
        logging.warning("No customer ID provided")
        return {"error": "No customer ID provided"}

    customer_data = {
        "CUST-001": {
            "customer_id": "CUST-001",
            "customer_name": "Ajit",
            "status": "active"
        },
        "CUST-002": {
            "customer_id": "CUST-002",
            "customer_name": "Vinayak",
            "status": "inactive"
        },
        "CUST-003": {
            "customer_id": "CUST-003",
            "customer_name": "Dipti",
            "status": "active"
        },
        "CUST-004": {
            "customer_id": "CUST-004",
            "customer_name": "Bharti",
            "status": "active"
        }
    }

    logging.info(f"Customer {customer_id} found with name {customer_data[customer_id]['customer_name']}")
    return customer_data[customer_id]

@tool
def fetch_customer_balance(customer_id: str) -> dict:
    """
    This tool fetches the customer account balance

    Args:
        - customer_id (str): A unique customer identifier
    
    Returns:
        - balance (dict): dictionary object containing 'customer_id' and 'balance'
    """
    if not customer_id:
        logging.warning("No customer ID provided")
        return {"error": "No customer ID provided"}

    customer_data = {
        "CUST-001": {
            "customer_id": "CUST-001",
            "balance": 82643837
        },
        "CUST-002": {
            "customer_id": "CUST-002",
            "balance": 46453745
        },
        "CUST-003": {
            "customer_id": "CUST-003",
            "balance": 67875
        },
        "CUST-004": {
            "customer_id": "CUST-004",
            "balance": 0
        }
    }

    logging.info(f"Customer {customer_id} found!")
    return customer_data[customer_id]

# Define the node for LLM Call
def llm_call(state: SystemState) -> dict:
    """
    This funciton/node calls the LLM
    """
    logging.info("Initiating LLM Call")

    messages = state["messages"]

    # connect the tools before making LLM calls
    llm_with_tools = base_llm.bind_tools(tools=[fetch_customer_info, fetch_customer_balance])

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }

# Define the nodes for tool -> ToolNode
tools = ToolNode(tools=[fetch_customer_info, fetch_customer_balance])

# Define the final node
def finalize(state: SystemState):
    # check if any tool calls are there in last message to route to tools
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return {
            "route": "tools"
        }

    return {
        "route": "final"
    }

# define the aditional node for summary
def summarize(state: SystemState) -> dict:
    """
    This node summarizes the customer information in tabular manner via LLM
    """
    messages = state["messages"]

    logging.info("Summarizing the response")

    # form new message layer
    updated_messages = [{"role": "system", "content": "Summarize the customer details"}] + messages

    logging.warning("Summarizing the response with updated messages")
    logging.warning(updated_messages)

    summary_response = base_llm.invoke(updated_messages)

    return {
        "summary": summary_response
    }

# Create Router
def route(state: SystemState):
    last_message = state["messages"][-1]

    tool_calls = getattr(last_message, "tool_calls", None)

    if tool_calls:
        logging.info("Calling Tool")
        return "tools"

    logging.info("Generating Summary")
    return "final"

# initiate the graph
graph_builder = StateGraph(state_schema=SystemState)

# add the llm call node
graph_builder.add_node("llm_call", llm_call)
graph_builder.add_node("tools", tools)
graph_builder.add_node("finalize", finalize)
graph_builder.add_node("summarize", summarize)

# add the edges for movements
graph_builder.add_edge(START, "llm_call")
graph_builder.add_conditional_edges("llm_call", route, {"tools": "tools", "final": "finalize"})
graph_builder.add_edge("tools", "summarize")
graph_builder.add_edge("summarize", "finalize")
graph_builder.add_edge("finalize", END)

graph = graph_builder.compile()

if __name__ == "__main__":
    result = graph.invoke({
        "messages": [
            {
                "role": "user",
                "content": input("Question: ")
            }
        ]
    })
    print("--------------------------------------")
    summary = result["summary"] if "summary" in result else None
    if not summary:
        logging.info("No Summary")
        print(getattr(result["messages"][-1], "content", "NA"))
    else:
        print(getattr(summary, "content", "NA"))
    print("--------------------------------------")