# Roo Custom Modes Editor - Project Plan

## Overview
This document outlines the plan for creating a web-based editor for the `custom_modes.json` file used by Roo. The editor will allow users to view, edit, add, and delete custom modes through a browser interface.

## Project Structure
```
/home/marc/devel/ai-coding-prompts/roomodes-editor/
├── main.py                # FastAPI application
├── models.py              # Pydantic models
├── templates/
│   └── index.html          # HTML template
├── static/
│   ├── style.css           # CSS styles
│   └── app.js              # JavaScript logic
├── pyproject.toml         # Project metadata
└── README.md               # Project information
```

## Technical Stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Validation**: Pydantic
- **Templating**: Jinja2

## Implementation Details

### 1. Backend (FastAPI)

#### main.py
- FastAPI application setup
- API endpoints:
  - `GET /`: Serve the main HTML page
  - `GET /api/modes`: Return current modes data
  - `POST /api/modes`: Save updated modes data
- File operations:
  - Read from `/home/marc/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json`
  - Create backup before saving changes
  - Write updates to the same file

#### models.py
- Pydantic models for data validation:
  - `ModeDetail`: For group details structure
  - `Mode`: For individual mode structure
  - `CustomModes`: For the complete modes list

### 2. Frontend

#### templates/index.html
- HTML structure with:
  - Table for displaying modes
  - Add/Delete/Save buttons
  - Status message area
- Embedded JavaScript for:
  - Fetching modes data
  - Rendering table
  - Handling edits/adds/deletes
  - Saving changes

#### static/style.css
- CSS styling for:
  - Table layout
  - Input fields
  - Buttons
  - Status messages

#### static/app.js
- JavaScript functions for:
  - `fetchModes()`: Load data from API
  - `renderTable()`: Display modes in table
  - `handleAddMode()`: Add new mode
  - `handleDeleteMode()`: Delete mode
  - `handleSaveChanges()`: Save changes to API

### 3. Project Configuration

#### pyproject.toml
```toml
[project]
name = "roomodes-editor"
version = "0.1.0"
description = "Web editor for Roo custom_modes.json"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.20.0",
    "pydantic>=2.0.0",
    "jinja2>=3.0.0",
    "python-multipart>=0.0.6"
]
```

## Workflow

1. User opens the editor in browser
2. Frontend fetches current modes data from backend
3. Data is displayed in editable table format
4. User makes changes (edit/add/delete)
5. Changes are saved back to the JSON file via backend

## Next Steps

1. Create project directory
2. Implement backend (FastAPI)
3. Develop frontend (HTML/JS)
4. Test and refine

## Notes

- The application will run locally
- Backup is created before each save operation
- All fields are editable with raw JSON for complex fields