from fastapi import FastAPI
from contextlib import asynccontextmanager

from discovery import discover_agents
from mcp_discovery import discover_tools

from registry import (
    AGENT_REGISTRY,
    build_index,
    resolve_agent
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    agents = await discover_agents()
    tools = await discover_tools()

    AGENT_REGISTRY.update(agents)
    AGENT_REGISTRY.update(tools)

    build_index()

    print("Unified registry:", AGENT_REGISTRY)

    yield

app = FastAPI(lifespan=lifespan)