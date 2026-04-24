from mcp.server.fastmcp import FastMCP
from store import store_context
from get import get_context

mcp = FastMCP("Fulgin")

@mcp.tool()
def store(surface_id: str, payload: str) -> str:
    """Store context from a surface into Fulgin."""
    id = store_context(surface_id, payload)
    return f"Stored context id={id} from surface='{surface_id}'"

@mcp.tool()
def search(query: str, limit: int = 5) -> str:
    """Search Fulgin for semantically relevant context."""
    results = get_context(query, limit)
    if not results:
        return "No results found."
    output = []
    for id, surface_id, payload, created_at, similarity in results:
        output.append(f"[{surface_id}] (similarity={similarity:.4f})\n  {payload}")
    return "\n\n".join(output)

if __name__ == "__main__":
    mcp.run()
