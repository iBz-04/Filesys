import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_COMMAND = "python"
SERVER_ARGS = ["run.py"]
SERVER_PARAMS = StdioServerParameters(command=SERVER_COMMAND, args=SERVER_ARGS)

async def _execute_mcp_request(resource_uri: str) -> dict:
    """
    Internal helper function to connect to the Filesys MCP server,
    execute a single read request, and return the parsed JSON response.
    """
   
    try:
       
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                result = await session.read_resource(resource_uri)


                if result.contents and result.contents[0].text:
                    try:
                      
                        data = json.loads(result.contents[0].text)
                        
                        return data
                    except json.JSONDecodeError as json_e:
                        print(f"[MCP Client] Error parsing JSON: {json_e}") # Keep error
                        return {"error": f"Failed to parse JSON response from server: {json_e}", "raw_response": result.contents[0].text}
                elif result.error:
                     print(f"[MCP Client] Received error from server: {result.error.message}") # Keep error
                     return {"error": f"Server returned error: {result.error.message}"}
                else:
                    
                    return {"error": "Received empty or non-text content from Filesys server"}
    except Exception as e:
       
        print(f"[MCP Client] Exception during MCP request: {e}") 
        return {"error": f"Failed to execute MCP request '{resource_uri}': {type(e).__name__}: {e}"}

async def list_files_in_safe_folder() -> dict:
    """
    Claude Tool Function: Lists files in the configured safe folder.

    Connects to the local Filesys MCP server and requests the 'files://list' resource.
    Returns a dictionary indicating success or failure, containing the list of
    files or an error message.
    """
   
    response = await _execute_mcp_request("files://list")

   
    if "error" in response:
        print(f"[Tool] list_files failed: {response['error']}") 
        return {"status": "error", "message": response["error"]}
    elif "files" in response:
       
        return {"status": "success", "files": response["files"]}
    else:
        print(f"[Tool] list_files failed: Unexpected response format: {response}") 
        return {"status": "error", "message": "Unexpected response format from Filesys server", "details": response}


async def read_file_from_safe_folder(filename: str) -> dict:
    """
    Claude Tool Function: Reads a specific file from the configured safe folder.

    Connects to the local Filesys MCP server and requests the 'files://read/{filename}' resource.
    Performs basic validation on the filename. Returns a dictionary indicating success or failure,
    containing the file content and metadata or an error message.

    Args:
        filename: The name of the file to read (e.g., "test.txt").
    """
   
    if not filename or "/" in filename or "\\" in filename or filename.startswith("."):
         print(f"[Tool] Invalid filename received: '{filename}'") 
         return {"status": "error", "message": "Invalid or potentially unsafe filename provided."}

    resource_uri = f"files://read/{filename}"
    response = await _execute_mcp_request(resource_uri)

   
    if "error" in response:
       
        print(f"[Tool] read_file failed for '{filename}': {response['error']}") 
        return {"status": "error", "filename": filename, "message": response["error"]}
    elif "content" in response and "metadata" in response:
        return {
            "status": "success",
            "filename": filename,
            "content": response["content"],
            "metadata": response["metadata"] 
        }
    else:
        print(f"[Tool] read_file failed for '{filename}': Unexpected response format: {response}") 
        return {"status": "error", "filename": filename, "message": "Unexpected response format from Filesys server", "details": response}

# --- Example Usage ---
async def test_tool_functions():
    print("--- Testing Tool: list_files_in_safe_folder ---")
    list_result = await list_files_in_safe_folder()
    print(f"Result:\n{json.dumps(list_result, indent=2)}\n")


    files_to_read = list_result.get("files", ["test.txt", "some.py"])
    if not files_to_read:
         print("No files found to test reading.")
         files_to_read = ["test.txt"] 
    print(f"--- Testing Tool: read_file_from_safe_folder ({files_to_read[0]}) ---")
    if files_to_read:
        read_result_1 = await read_file_from_safe_folder(files_to_read[0])
        print(f"Result:\n{json.dumps(read_result_1, indent=2)}\n")
    else:
        print("Skipping read test as no files were listed.")


    print("--- Testing Tool: read_file_from_safe_folder (nonexistent.txt) ---")
    read_result_nonexistent = await read_file_from_safe_folder("nonexistent.txt")
    print(f"Result:\n{json.dumps(read_result_nonexistent, indent=2)}\n")

    print("--- Testing Tool: read_file_from_safe_folder (Invalid Path: ../config.json) ---")
    read_result_invalid = await read_file_from_safe_folder("../config.json")
    print(f"Result:\n{json.dumps(read_result_invalid, indent=2)}\n")


if __name__ == "__main__":
    print("*"*50)
    print("Running Claude Tool Client Test")
    print("IMPORTANT: Ensure the Filesys server is running in another terminal:")
    print("  python run.py")
    print("*"*50 + "\n")
    try:
        asyncio.run(test_tool_functions())
    except Exception as e:
        print(f"\n--- Top-level Error during testing ---")
        print(f"{type(e).__name__}: {e}")
        print("This might indicate an issue starting the server process via StdioServerParameters.")
        print("Try running 'python run.py' manually in another terminal first.") 