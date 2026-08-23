from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client
    from mcp.types import CallToolResult, Tool
except ImportError:  # pragma: no cover - optional dependency fallback
    ClientSession = None  # type: ignore[assignment,misc]
    stdio_client = None  # type: ignore[assignment,misc]
    CallToolResult = None  # type: ignore[assignment,misc]
    Tool = None  # type: ignore[assignment,misc]


AllowedTool = Literal["customer_lookup", "finish"]
NextStep = Literal["discover", "lookup", "summarize", "finish"]


class MCPState(TypedDict):
    customer_id: str
    requested_tool: NotRequired[AllowedTool]
    tool_result: NotRequired[dict]
    tool_errors: NotRequired[list[str]]
    discovered_tools: NotRequired[list[str]]
    next_step: NotRequired[NextStep]
    final_answer: NotRequired[str]


@dataclass(frozen=True)
class MCPConfig:
    command: str
    args: tuple[str, ...] = ()
    env: dict[str, str] | None = None
    tool_name: str = "customer_lookup"


DEFAULT_MCP_CONFIG = MCPConfig(
    command=os.getenv("MCP_SERVER_COMMAND", "python3"),
    args=tuple(filter(None, os.getenv("MCP_SERVER_ARGS", "").split())),
    env=None,
)


def _ensure_mcp_available() -> None:
    if ClientSession is None or stdio_client is None:
        raise RuntimeError(
            "The 'mcp' package is not installed. Install an MCP SDK to run this example."
        )


async def _list_tools(config: MCPConfig) -> list[str]:
    _ensure_mcp_available()

    async with stdio_client(
        command=config.command,
        args=list(config.args),
        env=config.env,
    ) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [tool.name for tool in tools.tools]


async def _call_tool(config: MCPConfig, customer_id: str) -> dict:
    _ensure_mcp_available()

    async with stdio_client(
        command=config.command,
        args=list(config.args),
        env=config.env,
    ) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result: CallToolResult = await session.call_tool(
                config.tool_name,
                {"customer_id": customer_id},
            )
            content = result.content[0] if result.content else None
            if content is None:
                return {}
            if hasattr(content, "text"):
                return {"text": content.text}
            if hasattr(content, "data"):
                return content.data
            return {"content": str(content)}


def discover_tool(state: MCPState) -> dict:
    if not state.get("customer_id"):
        return {
            "requested_tool": "finish",
            "next_step": "finish",
            "tool_errors": ["Missing customer id."],
        }

    config = DEFAULT_MCP_CONFIG
    try:
        tool_names = asyncio.run(_list_tools(config))
    except Exception as error:
        return {
            "requested_tool": "finish",
            "next_step": "finish",
            "tool_errors": [f"MCP discovery failed: {error}"],
        }

    if config.tool_name not in tool_names:
        return {
            "requested_tool": "finish",
            "next_step": "finish",
            "discovered_tools": tool_names,
            "tool_errors": [f"Tool '{config.tool_name}' not found on MCP server."],
        }

    return {
        "requested_tool": "customer_lookup",
        "discovered_tools": tool_names,
        "next_step": "lookup",
    }


def invoke_tool(state: MCPState) -> dict:
    if state.get("requested_tool") != "customer_lookup":
        return {"next_step": "finish"}

    config = DEFAULT_MCP_CONFIG
    try:
        result = asyncio.run(_call_tool(config, state["customer_id"]))
        return {"tool_result": result, "next_step": "summarize"}
    except Exception as error:
        return {
            "next_step": "finish",
            "tool_errors": [f"MCP tool call failed: {error}"],
        }


def summarize(state: MCPState) -> dict:
    result = state.get("tool_result", {})
    if not result:
        return {
            "final_answer": "No customer record was returned.",
            "next_step": "finish",
        }

    name = result.get("name") or result.get("text") or "Unknown customer"
    status = result.get("status", "unknown")
    tier = result.get("tier", "unknown")
    return {
        "final_answer": (
            f"Customer {state['customer_id']}: {name} ({status}, tier {tier})."
        ),
        "next_step": "finish",
    }


def route(state: MCPState) -> str:
    return state.get("next_step", "finish")


builder = StateGraph(MCPState)
builder.add_node("discover_tool", discover_tool)
builder.add_node("invoke_tool", invoke_tool)
builder.add_node("summarize", summarize)

builder.add_edge(START, "discover_tool")
builder.add_conditional_edges(
    "discover_tool",
    route,
    {
        "discover": "discover_tool",
        "lookup": "invoke_tool",
        "summarize": "summarize",
        "finish": END,
    },
)
builder.add_conditional_edges(
    "invoke_tool",
    route,
    {
        "discover": "discover_tool",
        "lookup": "invoke_tool",
        "summarize": "summarize",
        "finish": END,
    },
)
builder.add_conditional_edges(
    "summarize",
    route,
    {
        "discover": "discover_tool",
        "lookup": "invoke_tool",
        "summarize": "summarize",
        "finish": END,
    },
)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"customer_id": "CUST-1001"})
    print(result.get("final_answer", "No answer produced."))
    if result.get("tool_errors"):
        print("Errors:", result["tool_errors"])
