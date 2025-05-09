import json
import os
import shutil
from datetime import datetime
from typing import List, Optional
import toml
from pathlib import Path
import sys
 
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from models import RooModeConfig

# Pydantic model for file sources
class FileSourceConfig(BaseModel):
    name: str
    path: str # Store as string, will be validated as absolute path
    is_valid: bool = True
    error_message: Optional[str] = None

# Pydantic model for the POST request body
class ModesUpdateRequest(BaseModel):
    modes: List[RooModeConfig]
    file_path: str

app = FastAPI()

# Configuration
CONFIG_FILE_PATH = Path("config/file_sources.toml")
BACKUP_DIR = Path("backup_modes") # Changed to relative path as per plan

# Ensure backup directory exists
BACKUP_DIR.mkdir(parents=True, exist_ok=True) # Use Path.mkdir

# Global variable for available file sources
AVAILABLE_FILES: List[FileSourceConfig] = []

def load_file_sources() -> List[FileSourceConfig]:
    """
    Reads and parses config/file_sources.toml, validates each source.
    Logs errors and raises SystemExit if the config is missing or invalid.
    """
    loaded_sources: List[FileSourceConfig] = []
    if not CONFIG_FILE_PATH.exists():
        print(f"Error: Configuration file {CONFIG_FILE_PATH} not found.", file=sys.stderr)
        raise SystemExit(1)

    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            data = toml.load(f)
    except toml.TomlDecodeError as e:
        print(f"Error: Invalid TOML in {CONFIG_FILE_PATH}: {e}", file=sys.stderr)
        raise SystemExit(1)
    except IOError as e:
        print(f"Error: Could not read {CONFIG_FILE_PATH}: {e}", file=sys.stderr)
        raise SystemExit(1)

    raw_sources_data = data.get('sources', [])

    if not isinstance(raw_sources_data, list):
        print(f"Error: 'sources' key in {CONFIG_FILE_PATH} must be a list of tables. Found: {type(raw_sources_data)}", file=sys.stderr)
        raw_sources_data = []

    for idx, source_config_item in enumerate(raw_sources_data):
        if not isinstance(source_config_item, dict):
            print(f"Warning: Source item at index {idx} is not a dictionary, skipping.", file=sys.stderr)
            loaded_sources.append(FileSourceConfig(
                name=f"Invalid Source Entry {idx+1}",
                path="N/A",
                is_valid=False,
                error_message="Source entry in TOML is not a valid structure (expected a table/dictionary)."
            ))
            continue

        name = source_config_item.get('name')
        path_str = source_config_item.get('path')
        current_is_valid = True
        error_parts = []

        if not name or not isinstance(name, str):
            name_to_use = f"Unnamed Source {idx + 1}"
            error_parts.append("Source 'name' is missing or not a string.")
            current_is_valid = False
        else:
            name_to_use = name

        if not path_str or not isinstance(path_str, str):
            path_to_store = "N/A"
            error_parts.append("Source 'path' is missing or not a string.")
            current_is_valid = False
        else:
            path_to_store = path_str
            try:
                path_obj = Path(path_str)
                if not path_obj.is_absolute():
                    error_parts.append(f"Path '{path_str}' is not an absolute path.")
                    current_is_valid = False
                else:
                    if not path_obj.exists():
                        error_parts.append(f"File '{path_str}' does not exist.")
                        current_is_valid = False
                    elif not path_obj.is_file():
                        error_parts.append(f"Path '{path_str}' exists but is not a file.")
                        current_is_valid = False
                    else:
                        try:
                            with open(path_obj, 'r', encoding='utf-8') as json_file:
                                json.load(json_file) # Validate JSON structure
                        except json.JSONDecodeError as json_e:
                            error_parts.append(f"Invalid JSON in file '{path_str}': {json_e}.")
                            current_is_valid = False
                        except IOError as io_e: # Catch issues like permission errors for the JSON file
                            error_parts.append(f"Could not read file '{path_str}': {io_e}.")
                            current_is_valid = False
            except Exception as e_path: # Catch any other errors related to path processing
                error_parts.append(f"Error processing path '{path_str}': {e_path}.")
                current_is_valid = False
        
        current_error_message = " | ".join(error_parts) if error_parts else None
        loaded_sources.append(FileSourceConfig(
            name=name_to_use,
            path=path_to_store,
            is_valid=current_is_valid,
            error_message=current_error_message
        ))
    return loaded_sources

# Initialize AVAILABLE_FILES at startup
try:
    AVAILABLE_FILES = load_file_sources()
except SystemExit as e:
    print(f"SystemExit during file source initialization: {e}. Application will likely terminate.", file=sys.stderr)
    if 'AVAILABLE_FILES' not in globals(): AVAILABLE_FILES = [] # Ensure defined for safety, though `raise` is next
    raise # Re-raise SystemExit to ensure termination or proper handling by FastAPI
except Exception as e:
    print(f"Unexpected error during file source initialization: {e}. AVAILABLE_FILES set to empty.", file=sys.stderr)
    AVAILABLE_FILES = [] # Ensure it's defined in case of other unexpected errors

def read_modes_file(file_path: str) -> List[RooModeConfig]:
    """Read and parse the custom modes JSON file from the given path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [RooModeConfig(**mode) for mode in json.load(f)]
    except FileNotFoundError:
        # Ensure this error is specific enough for the calling endpoint
        raise HTTPException(status_code=404, detail=f"Modes file not found at path: {file_path}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in modes file: {file_path}")
    except Exception as e: # Catch other potential IO errors
        raise HTTPException(status_code=500, detail=f"Error reading modes file {file_path}: {str(e)}")

def write_modes_file(modes: List[RooModeConfig], file_path: str):
    """Write the custom modes data to the specified file with backup."""
    
    # Ensure BACKUP_DIR exists (it's also done at startup, but good practice here too)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    original_file_path_obj = Path(file_path)
    # Sanitize filename for backup: replace slashes and other problematic chars if any, though Path.name should be safe.
    # For simplicity, using Path.name directly. If more complex sanitization is needed, it can be added.
    sanitized_name = original_file_path_obj.name
    backup_filename = f"{sanitized_name}_{timestamp}.json_backup"
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        # Check if the source file exists before trying to back it up
        if original_file_path_obj.exists() and original_file_path_obj.is_file():
            shutil.copy2(str(original_file_path_obj), str(backup_path))
        # If the file doesn't exist (e.g., creating a new one), no backup is made of a non-existent file.
    except Exception as e:
        # Log or handle backup failure, but proceed with writing the main file if possible
        print(f"Warning: Could not create backup for {file_path} to {backup_path}: {e}", file=sys.stderr)

    # Write new file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([mode.dict() for mode in modes], f, indent=2)
    except Exception as e: # Catch potential IO errors during write
        raise HTTPException(status_code=500, detail=f"Error writing modes file {file_path}: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("templates/index.html")

@app.get("/api/modes", response_model=List[RooModeConfig])
async def get_modes(file_path: Optional[str] = None):
    """Return modes data from the specified file or the default valid file."""
    target_file_path = None

    if file_path:
        # Validate provided file_path
        source_config = next((f for f in AVAILABLE_FILES if f.path == file_path), None)
        if not source_config:
            raise HTTPException(status_code=404, detail=f"File source not found for path: {file_path}")
        if not source_config.is_valid:
            raise HTTPException(status_code=400, detail=f"File source is not valid: {file_path}. Error: {source_config.error_message}")
        target_file_path = source_config.path
    else:
        # Find the first valid file in AVAILABLE_FILES
        default_source = next((f for f in AVAILABLE_FILES if f.is_valid), None)
        if not default_source:
            # If no file_path is given and no default valid file exists, return empty or error
            # Plan: "If no valid files exist, return an appropriate response (e.g., empty list or an error)."
            # Returning an error seems more informative.
            raise HTTPException(status_code=404, detail="No valid mode file sources configured or available to serve as default.")
        target_file_path = default_source.path
    
    if not target_file_path: # Should not happen if logic above is correct, but as a safeguard
        raise HTTPException(status_code=500, detail="Could not determine target file path for modes.")

    return read_modes_file(target_file_path)

@app.post("/api/modes", response_model=List[RooModeConfig])
async def update_modes(request_data: ModesUpdateRequest):
    """Save updated modes data to the specified file."""
    
    # Validate file_path from request body
    source_config = next((f for f in AVAILABLE_FILES if f.path == request_data.file_path), None)
    if not source_config:
        raise HTTPException(status_code=404, detail=f"File source not found for path: {request_data.file_path}")
    if not source_config.is_valid:
        raise HTTPException(status_code=400, detail=f"File source is not valid: {request_data.file_path}. Error: {source_config.error_message}")

    try:
        write_modes_file(request_data.modes, request_data.file_path)
        return request_data.modes
    except HTTPException: # Re-raise HTTPExceptions from write_modes_file
        raise
    except Exception as e: # Catch other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while updating modes: {str(e)}")

@app.get("/api/file-sources", response_model=List[FileSourceConfig])
async def get_file_sources():
    """Return the list of available (and validated) file sources."""
    return AVAILABLE_FILES

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")