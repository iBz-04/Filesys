import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["run.py"])
    
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                resources = await session.list_resources()
                print(f"\nFound {len(resources.resources)} resources:")
                for r in resources.resources:
                    print(f"- {r.uri}")
                
                files_result = await session.read_resource("files://list")
                
                
                try:
                    files_json = files_result.contents[0].text
                    files_data = json.loads(files_json)
                    print("\nAvailable files:")
                    if "error" in files_data:
                        print(f"Error: {files_data['error']}")
                    elif "files" in files_data:
                        for file in files_data["files"]:
                            print(f"- {file}")
                        
                       
                        if "test.txt" in files_data["files"]:
                            file_result = await session.read_resource("files://read/test.txt")
                            file_json = file_result.contents[0].text
                            file_data = json.loads(file_json)
                            
                            print("\nFile content:")
                            if "error" in file_data:
                                print(f"Error: {file_data['error']}")
                            else:
                                print(f"Content: {file_data['content']}")
                                print(f"Size: {file_data['metadata']['size']} bytes")
                                print(f"Modified: {file_data['metadata']['modified']}")
                except Exception as e:
                    print(f"Error parsing response: {e}")
                    print("Raw response:", files_result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 