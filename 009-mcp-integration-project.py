from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    ClientSession = None  # type: ignore[assignment]
    stdio_client = None  # type: ignore[assignment]
    FastMCP = None  # type: ignore[assignment]


CUSTOMER_DB = {
    "CUST-1001": {"customer_id": "CUST-1001", "name": "Anaya Sharma", "tier": "gold", "status": "active"},
    "CUST-1002": {"customer_id": "CUST-1002", "name": "Rahul Mehta", "tier": "silver", "status": "active"},
}


class CustomerState(TypedDict):
    customer_id: str
    available_tools: NotRequired[list[str]]
    tool_result: NotRequired[dict[str, Any]]
    tool_errors: NotRequired[list[str]]
    final_answer: NotRequired[str]


@dataclass(frozen=True)
class MCPConfig:
    command: str
    args: tuple[str, ...] = ()
    tool_name: str = "customer_lookup"


def _server_config() -> MCPConfig:
    command = os.getenv("MCP_SERVER_COMMAND", "python3")
    args = tuple(filter(None, os.getenv("MCP_SERVER_ARGS", "").split()))
    return MCPConfig(command=command, args=args)


async def _discover_tools(config: MCPConfig) -> list[str]:
    if ClientSession is None or stdio_client is None:
        raise RuntimeError("mcp package is not installed")

    async with stdio_client(command=config.command, args=list(config.args)) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            response = await session.list_tools()
            return [tool.name for tool in response.tools]


async def _call_customer_lookup(config: MCPConfig, customer_id: str) -> dict[str, Any]:
    if ClientSession is None or stdio_client is None:
        raise RuntimeError("mcp package is not installed")

    async with stdio_client(command=config.command, args=list(config.args)) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(config.tool_name, {"customer_id": customer_id})
            if not result.content:
                return {}
            item = result.content[0]
            if hasattr(item, "text") and item.text:
                try:
                    return json.loads(item.text)
                except json.JSONDecodeError:
                    return {"text": item.text}
            if hasattr(item, "data") and item.data:
                return item.data
            return {"content": str(item)}


def discover_mcp_tools(state: CustomerState) -> dict:
    config = _server_config()
    if ClientSession is None or stdio_client is None:
        return {
            "tool_errors": ["mcp package missing"],
            "final_answer": "MCP runtime is not installed.",
        }

    try:
        tools = asyncio.run(_discover_tools(config))
    except Exception as error:
        return {"tool_errors": [f"tool discovery failed: {error}"], "final_answer": "Could not discover MCP tools."}

    if config.tool_name not in tools:
        return {
            "available_tools": tools,
            "tool_errors": [f"required tool '{config.tool_name}' not found"],
            "final_answer": "Customer lookup tool is unavailable.",
        }

    return {"available_tools": tools}


def fetch_customer(state: CustomerState) -> dict:
    config = _server_config()
    if ClientSession is None or stdio_client is None:
        return {}

    try:
        result = asyncio.run(_call_customer_lookup(config, state["customer_id"]))
    except Exception as error:
        return {"tool_errors": [f"tool invocation failed: {error}"], "final_answer": "Customer lookup failed."}

    if not result:
        return {"tool_errors": ["empty tool result"], "final_answer": "No customer data returned."}

    return {"tool_result": result}


def summarize_customer(state: CustomerState) -> dict:
    customer = state.get("tool_result", {})
    if not customer:
        return {"final_answer": "No customer record was available."}

    return {
        "final_answer": (
            f"Customer {customer.get('customer_id', state['customer_id'])}: "
            f"{customer.get('name', 'Unknown')} is {customer.get('status', 'unknown')} "
            f"with {customer.get('tier', 'unknown')} tier."
        )
    }


def route_after_discovery(state: CustomerState) -> str:
    if state.get("final_answer"):
        return "finish"
    return "lookup"


def route_after_lookup(state: CustomerState) -> str:
    if state.get("tool_result"):
        return "summarize"
    return "finish"


builder = StateGraph(CustomerState)
builder.add_node("discover_mcp_tools", discover_mcp_tools)
builder.add_node("fetch_customer", fetch_customer)
builder.add_node("summarize_customer", summarize_customer)

builder.add_edge(START, "discover_mcp_tools")
builder.add_conditional_edges(
    "discover_mcp_tools",
    route_after_discovery,
    {"lookup": "fetch_customer", "finish": END},
)
builder.add_conditional_edges(
    "fetch_customer",
    route_after_lookup,
    {"summarize": "summarize_customer", "finish": END},
)
builder.add_edge("summarize_customer", END)

graph = builder.compile()


def _server() -> None:
    if FastMCP is None:
        raise RuntimeError("mcp package is not installed")

    app = FastMCP("customer-service")

    @app.tool()
    def customer_lookup(customer_id: str) -> dict[str, Any]:
        record = CUSTOMER_DB.get(customer_id)
        if not record:
            return {"customer_id": customer_id, "status": "not_found"}
        return record

    app.run()


def _client(customer_id: str) -> None:
    result = graph.invoke({"customer_id": customer_id})
    print(result.get("final_answer", "No answer produced."))
    if result.get("tool_errors"):
        print("Errors:", result["tool_errors"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--customer-id", default="CUST-1001")
    args = parser.parse_args()

    if args.server:
        _server()
    else:
        _client(args.customer_id)
