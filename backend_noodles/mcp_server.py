from fastmcp import FastMCP


mcp = FastMCP("Hospital")

@mcp.tool("Hello")
def hello(name: str) -> str:
    """
    A simple hello world function.
    
    Args:
        name (str): The name to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, Bro {name}!"



if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8005,
        log_level="debug"
    )