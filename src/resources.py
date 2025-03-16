from pathlib import Path
import json

# Load config safely
config_path = Path(__file__).parent.parent / "config/config.json"
with open(config_path, "r") as f:
    config = json.load(f)
BASE_DIR = Path(config["directory"]).expanduser().resolve()

def list_files():
    """List all files in the configured directory with safety checks"""
    try:
        return {
            "files": [
                f.name for f in BASE_DIR.iterdir() 
                if f.is_file() and not f.name.startswith('.')
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def read_file(filename: str):
    """Read file contents with security validation"""
    try:
        target_path = (BASE_DIR / filename).resolve()
        
        # Prevent directory traversal
        if BASE_DIR not in target_path.parents:
            return {"error": "Access denied"}
            
        return {
            "content": target_path.read_text(encoding="utf-8"),
            "metadata": {
                "size": target_path.stat().st_size,
                "modified": target_path.stat().st_mtime
            }
        }
    except Exception as e:
        return {"error": str(e)}