# Safe File Server

## Overview
Safe File Server is a lightweight file server built with Python and the mcp library that securely exposes file contents and metadata from a preconfigured directory. The project leverages FastMCP to provide a set of endpoints that allow:
- Listing all files in a specified directory.
- Reading the contents and metadata of a specified file.

The project ensures safe file access by validating paths and preventing directory traversal attacks.

## How It Works
The core functionality is divided into two main components:

- **Resources:**  
  In `src/resources.py`, two functions are responsible for file operations:
  - `list_files()`: Scans the base directory (configured in `config/config.json`) to return a list of visible files.
  - `read_file(filename)`: Reads the content of the specified file and returns it along with metadata (size and last modified timestamp), while ensuring that the file access is safe.

- **Server:**  
  In `src/server.py`, a FastMCP server is initialized and registers two resource endpoints:
  - `files://list`: Invokes `list_files_resource()`, which returns the list of files.
  - `files://read/{filename}`: Invokes `read_file_resource(filename)`, which returns the file's content and metadata.
  
The server is started via `run.py`, and it utilizes the mcp library to handle resource requests.

- **Client & Testing:**  
  An example client in `example_client.py` demonstrates how to connect to the server, list resources, and read file contents using the MCP protocol.  
  Unit tests in `tests/test_resources.py` ensure that the file listing and reading functionalities work as expected.

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   ```
2. **Navigate to the Project Directory:**
   ```bash
   cd yourproject
   ```
3. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
The file server reads its configuration from `config/config.json`. By default, the server operates on the directory specified below:
```json
{
  "directory": "./safe_folder"
}
```
You can modify this file to point to a different directory if needed.

## Usage
1. **Start the Server:**
   ```bash
   python run.py
   ```
   This command will initialize the FastMCP server and register the file listing and reading endpoints.

2. **Interact with the Server:**
   - **Using the Example Client:**  
     You can run the provided example client to interact with the server:
     ```bash
     python example_client.py
     ```
   - **Direct Requests:**  
     Use any MCP-compatible client to access the endpoints:  
     - **List Files:** Request `files://list` to get the list of files.
     - **Read a File:** Request `files://read/{filename}` (replace `{filename}` with the actual file name) to retrieve the file's content and metadata.

## Testing
Run the unit tests to verify the functionality:
```bash
python -m unittest discover tests
```
This command will execute the tests in `tests/test_resources.py` to ensure that file operations perform correctly.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with detailed messages.
4. Push your branch and open a pull request.



## Additional Notes
- Customize the configuration as needed.
- This project implements basic security measures to restrict file access to the configured directory.
- Update this documentation as new features are added or changes are made. 