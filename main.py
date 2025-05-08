import json
import os
import shutil
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from models import RooModeConfig

app = FastAPI()

# Configuration
MODES_FILE_PATH = "/home/marc/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json"
BACKUP_DIR = "/home/marc/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/backups"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def read_modes_file() -> List[RooModeConfig]:
    """Read and parse the custom modes JSON file."""
    try:
        with open(MODES_FILE_PATH, 'r') as f:
            return [RooModeConfig(**mode) for mode in json.load(f)]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Modes file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in modes file")

def write_modes_file(modes: List[RooModeConfig]):
    """Write the custom modes data to file with backup."""
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"custom_modes_backup_{timestamp}.json")
    shutil.copy2(MODES_FILE_PATH, backup_path)

    # Write new file
    with open(MODES_FILE_PATH, 'w') as f:
        json.dump([mode.dict() for mode in modes], f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("templates/index.html")

@app.get("/api/modes", response_model=List[RooModeConfig])
async def get_modes():
    """Return current modes data."""
    return read_modes_file()

@app.post("/api/modes", response_model=List[RooModeConfig])
async def update_modes(modes: List[RooModeConfig]):
    """Save updated modes data."""
    try:
        write_modes_file(modes)
        return modes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")