import os
import json
import asyncio
from dotenv import load_dotenv
import anthropic

# Import the async functions from our client that actually interact with the MCP server
from claude_tool_client import list_files_in_safe_folder, read_file_from_safe_folder

# --- Configuration ---
# Load environment variables from .env file (especially ANTHROPIC_API_KEY)
# Specify the correct path if using .env.local
load_dotenv(dotenv_path='.env.local')

# Get the API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("❌ ANTHROPIC_API_KEY not found in .env file or environment variables.")

# Initialize the Anthropic client
# Use the async client as our tool functions are async
client = anthropic.AsyncAnthropic(api_key=api_key)

MODEL_NAME = "claude-3-sonnet-20240229" # Or another model that supports tools

# --- Tool Definition ---
# Define the tools for the Claude API based on our client functions
tools = [
    {
        "name": "list_files_in_safe_folder",
        "description": "Lists the names of all available files in the pre-configured secure folder. Use this to find out what files can be read.",
        "input_schema": {
            "type": "object",
            "properties": {}, # No input parameters needed for listing
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

# --- Main Interaction Logic ---
async def run_conversation():
    """Handles the conversation loop with Claude, including tool use."""
    print("✅ Anthropic client initialized.")
    print(f"🤖 Model: {MODEL_NAME}")
    print("🛠️ Tools Registered: list_files_in_safe_folder, read_file_from_safe_folder")
    print("\n---")
    print("🗣️ Starting conversation with Claude. Type 'quit' to exit.")
    print("   Ask about files (e.g., 'What files are available?', 'Can you read test.txt?')")
    print("---")

    # Store the conversation history
    messages = []

    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == 'quit':
            print("👋 Exiting conversation.")
            break

        if not user_input:
            continue

        # Add user message to history
        messages.append({"role": "user", "content": user_input})

        print("⏳ Thinking...")
        try:
            # Initial call to Claude
            response = await client.messages.create(
                model=MODEL_NAME,
                max_tokens=1024,
                messages=messages,
                tools=tools,
            )

            # --- Corrected Response Handling ---
            # Always append the full assistant response structure first
            # The response object itself has the role attribute.
            assistant_response_content = response.content
            messages.append({"role": response.role, "content": assistant_response_content})
            # --- End Corrected Response Handling ---


            while response.stop_reason == "tool_use":
                # Find all tool use requests in the last assistant message
                tool_uses = [block for block in assistant_response_content if block.type == "tool_use"]

                if not tool_uses:
                     print("⚠️ Error: Stop reason is 'tool_use' but no tool_use blocks found in content.")
                     # Break the inner loop, maybe print final text if available
                     break

                # Prepare tool results message content
                tool_results_content = []

                # --- Execute tools and gather results ---
                for tool_use in tool_uses:
                    tool_name = tool_use.name
                    tool_input = tool_use.input
                    tool_use_id = tool_use.id

                    print(f"🛠️ Claude wants to use tool: {tool_name}")
                    print(f"   Input: {tool_input}")

                    tool_result_data = None # Renamed from tool_result_content to avoid confusion
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

                    # Append individual tool result to the list for the next API call
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(tool_result_data), # Content should be a JSON string
                        "is_error": tool_result_data.get("status") == "error"
                    })
                # --- End Tool Execution Loop ---

                # Add the user message containing all tool results
                messages.append({
                    "role": "user", # Role must be 'user' for tool_result type
                    "content": tool_results_content # Send all results back
                })

                # Make follow-up call to Claude with the tool results
                print("⏳ Sending tool result(s) back to Claude...")
                response = await client.messages.create(
                    model=MODEL_NAME,
                    max_tokens=1024,
                    messages=messages,
                    tools=tools,
                )

                # Append the new assistant response to history
                assistant_response_content = response.content # Update content for the next loop check
                messages.append({"role": response.role, "content": assistant_response_content})
                # Now the loop condition 'while response.stop_reason == "tool_use":' will check the new response


            # After the while loop (or if stop_reason wasn't 'tool_use' initially)
            # Find and print the final text response from the *last* assistant message
            final_text = next((block.text for block in assistant_response_content if block.type == "text"), None)
            if final_text:
                print(f"🤖 Claude: {final_text}")
            elif response.stop_reason != "tool_use": # Don't print error if we just finished tool use
                 print("🤖 Claude: (No final text content found in the last response)")


        except anthropic.APIError as e:
            print(f"❌ Anthropic API Error: {e}")
            # Consider adding more specific error handling if needed
            # e.g., print(e.status_code, e.response)
        except Exception as e:
            # Print the exception traceback for better debugging
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
    except ValueError as e: # Catch the API key error specifically
        print(e)
    except Exception as e:
        print(f"❌ A critical error occurred: {e}")
        print("   Make sure 'python run.py' is running and accessible.")
        print("   Check network connection and API key validity.") 