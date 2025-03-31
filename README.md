# File system MCP

## Overview
filesys is a lightweight mcp server built with Python and the mcp library that securely exposes file contents and metadata from a preconfigured directory. The project leverages FastMCP to provide a set of endpoints that allow:
- Listing all files in a specified directory.
- Reading the contents and metadata of a specified file.

**New:** It now includes an integration with Anthropic's Claude AI, allowing users to interact with the file system through natural language conversation, using Claude Tools to securely access the defined MCP resources.

The project ensures safe file access by validating paths and preventing directory traversal attacks.

## Preview
- Interacting with Claude to list and read files from the `safe_folder`:

<img src="https://res.cloudinary.com/diekemzs9/image/upload/v1743439706/screenshot_vxq1ym.jpg" alt="My Image" width="2000"/>

## How It Works
The core functionality is divided into several components:

- **Resources:**  
  In `src/resources.py`, two functions are responsible for file operations:
  - `list_files()`: Scans the base directory (configured in `config/config.json`) to return a list of visible files.
  - `read_file(filename)`: Reads the content of the specified file and returns it along with metadata (size and last modified timestamp), while ensuring that the file access is safe.

- **Server:**  
  In `src/server.py`, a FastMCP server is initialized and registers two resource endpoints:
  - `files://list`: Invokes `list_files()`.
  - `files://read/{filename}`: Invokes `read_file(filename)`.
  
The server is started via `run.py`, and it utilizes the mcp library to handle resource requests.

- **Claude Tool Client:**
  In `claude_tool_client.py`, functions (`list_files_in_safe_folder`, `read_file_from_safe_folder`) are defined to interact with the running Filesys MCP server. These functions act as a bridge, translating simple function calls into MCP requests and parsing the responses. They are designed to be easily consumable by Claude Tools.

- **Claude Interaction Script:**
  The `interact_with_claude.py` script sets up an Anthropic client, defines Claude Tools based on the functions in `claude_tool_client.py`, and runs a command-line conversation loop. Users can ask Claude questions like "What files are available?" or "Read test.txt", and Claude will use the provided tools (which securely call the MCP server) to fulfill the requests.

- **Testing:**  
  Unit tests in `tests/test_resources.py` ensure that the file listing and reading functionalities work as expected.

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/iBz-04/Filesys.git
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd Filesys
   ```
3. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install Dependencies:**
   Make sure you have Python installed. Then install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure API Key:**
   - Create a file named `.env.local` in the project's root directory.
   - Add your Anthropic API key to this file:
     ```env
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - **Note:** The `.gitignore` file is configured to prevent this file from being committed to Git.

## Configuration
The file server reads its configuration from `config/config.json`. By default, the server operates on the directory specified below:
```json
{
  "directory": "./safe_folder"
}
```
You can modify this file to point to a different directory if needed.

- **Anthropic API Key:** The Claude interaction script reads the `ANTHROPIC_API_KEY` from the `.env.local` file (see Installation step 5).

## Usage
1. **Start the MCP Server:**
   First, ensure the Filesys MCP server is running in a terminal:
   ```bash
   python run.py
   ```
   This command initializes the FastMCP server and makes the `files://list` and `files://read/{filename}` endpoints available.

2. **Interact with Claude:**
   In a **separate terminal** (while the server from step 1 is still running), run the Claude interaction script:
   ```bash
   python interact_with_claude.py
   ```
   You can then ask Claude to interact with the files in the configured `safe_folder`. Examples:
   - "What files can you see?"
   - "List the available files."
   - "Can you read test.txt for me?"
   - "Tell me the contents of the file named test.txt"

3. **Direct MCP Requests (Optional):**
   You can also interact with the server directly using any MCP-compatible client:
   - **List Files:** Request `files://list`.
   - **Read a File:** Request `files://read/{filename}` (replace `{filename}` with the actual file name).

## Testing
- **MCP Client Functions:** You can test the functions that communicate with the MCP server by running:
  ```bash
  python claude_tool_client.py
  ```
  This executes the `test_tool_functions` defined at the end of the script. Ensure the MCP server (`python run.py`) is running beforehand.
- **Core Resources (if tests exist):** If unit tests are created in the `tests/` directory (e.g., `tests/test_resources.py`), you can run them using:
  ```bash
  python -m unittest discover tests
  ```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with detailed messages.
4. Push your branch and open a pull request.

## Additional Notes
- Customize the configuration (`config/config.json`, `.env.local`) as needed.
- **Important:** The Claude interaction script (`interact_with_claude.py`) requires the Filesys MCP server (`run.py`) to be running in a separate process.
- This project implements basic security measures to restrict file access to the configured directory and prevent directory traversal.
- Update this documentation as new features are added or changes are made. 