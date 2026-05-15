import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from store import store_context
from get import get_context

load_dotenv()

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", 8002))

security = TransportSecuritySettings(
    allowed_hosts=["fulginn.local", "localhost", "127.0.0.1"],
    allowed_origins=["http://fulginn.local", "http://localhost"]
)

mcp = FastMCP("Fulginn", host=MCP_HOST, port=MCP_PORT, transport_security=security)

@mcp.tool()
def store(surface_id: str, payload: str) -> str:
    """Store context from a surface into Fulginn."""
    id = store_context(surface_id, payload)
    return f"Stored context id={id} from surface='{surface_id}'"

@mcp.tool()
def search(query: str, limit: int = 5) -> str:
    """Search Fulginn for semantically relevant context."""
    results = get_context(query, limit)
    if not results:
        return "No results found."
    output = []
    for id, surface_id, payload, created_at, similarity in results:
        output.append(f"[{surface_id}] (similarity={similarity:.4f})\n  {payload}")
    return "\n\n".join(output)

if __name__ == "__main__":
    mcp.run(transport="sse")
