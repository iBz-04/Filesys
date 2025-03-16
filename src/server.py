from mcp.server.fastmcp import FastMCP
from .resources import list_files, read_file

mcp = FastMCP("FileSystemServer")

@mcp.resource("files://list")
def list_files_resource():
    """List all files in the configured directory"""
    return list_files()

@mcp.resource("files://read/{filename}")
def read_file_resource(filename: str):
    """Read contents of a specified file"""
    return read_file(filename)

server = mcp