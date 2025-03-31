import os
import json
import asyncio
from dotenv import load_dotenv
import anthropic

from claude_tool_client import list_files_in_safe_folder, read_file_from_safe_folder

load_dotenv(dotenv_path='.env.local')

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ ANTHROPIC_API_KEY not found in .env file or environment variables.")

client = anthropic.AsyncAnthropic(api_key=api_key)

MODEL_NAME = "claude-3-sonnet-20240229" 

tools = [
    {
        "name": "list_files_in_safe_folder",
        "description": "Lists the names of all available files in the pre-configured secure folder. Use this to find out what files can be read.",
        "input_schema": {
            "type": "object",
            "properties": {}, 
        }
    },
    {
        "name": "read_file_from_safe_folder",
        "description": "Reads the content and metadata (size, modified time) of a specific file from the pre-configured secure folder. Only use filenames returned by 'list_files_in_safe_folder'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The exact name of the file to read (e.g., 'test.txt'). Must be one of the files listed previously."
                }
            },
            "required": ["filename"]
        }
    }
]

async def run_conversation():
    """Handles the conversation loop with Claude, including tool use."""
    print("✅ Anthropic client initialized.")
    print(f"🤖 Model: {MODEL_NAME}")
    print("🛠️ Tools Registered: list_files_in_safe_folder, read_file_from_safe_folder")
    print("\n---")
    print("🗣️ Starting conversation with Claude. Type 'quit' to exit.")
    print("   Ask about files (e.g., 'What files are available?', 'Can you read test.txt?')")
    print("---")

    messages = []

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == 'quit':
            print("👋 Exiting conversation.")
            break

        if not user_input:
            continue

        
        messages.append({"role": "user", "content": user_input})

        print("⏳ Thinking...")
        try:
            
            response = await client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                messages=messages,
                tools=tools,
            )

            assistant_response_content = response.content
            messages.append({"role": response.role, "content": assistant_response_content})
            


            while response.stop_reason == "tool_use":
               
                tool_uses = [block for block in assistant_response_content if block.type == "tool_use"]

                if not tool_uses:
                     print("⚠️ Error: Stop reason is 'tool_use' but no tool_use blocks found in content.")
                    
                     break

            
                tool_results_content = []

                
                for tool_use in tool_uses:
                    tool_name = tool_use.name
                    tool_input = tool_use.input
                    tool_use_id = tool_use.id

                    print(f"🛠️ Claude wants to use tool: {tool_name}")
                    print(f"   Input: {tool_input}")

                    tool_result_data = None 
                    if tool_name == "list_files_in_safe_folder":
                        tool_result_data = await list_files_in_safe_folder()
                    elif tool_name == "read_file_from_safe_folder":
                        filename = tool_input.get("filename")
                        if filename:
                            tool_result_data = await read_file_from_safe_folder(filename)
                        else:
                            tool_result_data = {"status": "error", "message": "Missing required 'filename' parameter."}
                    else:
                        print(f"⚠️ Error: Unknown tool '{tool_name}' requested.")
                        tool_result_data = {"status": "error", "message": f"Unknown tool '{tool_name}'."}

                    print(f"   Result: {tool_result_data}")

                    
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(tool_result_data), 
                        "is_error": tool_result_data.get("status") == "error"
                    })
                # --- End Tool Execution Loop ---

               
                messages.append({
                    "role": "user", 
                    "content": tool_results_content 
                })

                
                print("⏳ Sending tool result(s) back to Claude...")
                response = await client.messages.create(
                    model=MODEL_NAME,
                    max_tokens=1024,
                    messages=messages,
                    tools=tools,
                )

                assistant_response_content = response.content 
                messages.append({"role": response.role, "content": assistant_response_content})
              



            final_text = next((block.text for block in assistant_response_content if block.type == "text"), None)
            if final_text:
                print(f"🤖 Claude: {final_text}")
            elif response.stop_reason != "tool_use":
                 print("🤖 Claude: (No final text content found in the last response)")


        except anthropic.APIError as e:
            print(f"❌ Anthropic API Error: {e}")
            
        except Exception as e:
            import traceback
            print(f"❌ An unexpected error occurred: {type(e).__name__}: {e}")
            print("Traceback:")
            traceback.print_exc()


if __name__ == "__main__":
    print("*" * 60)
    print(" Claude Interaction Script for Local Filesys ")
    print("*" * 60)
    print("\n🚨 IMPORTANT: Ensure the Filesys MCP server is running!")
    print("   In another terminal, run: python run.py\n")

    try:
        asyncio.run(run_conversation())
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Exiting.")
    except ValueError as e: 
        print(e)
    except Exception as e:
        print(f"❌ A critical error occurred: {e}")
        print("   Make sure 'python run.py' is running and accessible.")
        print("   Check network connection and API key validity.") 