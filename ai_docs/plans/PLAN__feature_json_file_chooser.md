# Plan: Feature - JSON File Chooser for Roo Custom Modes Editor

This document outlines the plan to implement a feature allowing users to select which JSON configuration file the Roo Custom Modes Editor works with, using a dropdown menu. The list of available files will be defined in a `config/file_sources.toml` file.

## Summary of Decisions

1.  **`file_sources.toml` Missing/Invalid:** If `config/file_sources.toml` is missing or contains invalid TOML, the application will prevent startup, log an error, and exit.
2.  **Default Selection:** The first valid file listed in `config/file_sources.toml` will be selected by default when the editor loads.
3.  **Error Handling for Individual Files:** When the application starts, it will parse `config/file_sources.toml`. If any JSON file path listed therein is found to be non-existent or the JSON content is invalid, its corresponding entry in the dropdown menu will be disabled.
4.  **File Paths in Config:** `config/file_sources.toml` will support **absolute paths only** for the JSON files.
5.  **Location of `file_sources.toml`:** The configuration file will be located at `config/file_sources.toml`.

## Detailed Plan

### 1. Create `config/file_sources.toml`

*   Create a new directory named `config` in the project root.
*   Inside `config/`, create a file named `file_sources.toml`.
*   **Structure:**
    ```toml
    # Example: config/file_sources.toml
    [[sources]]
    name = "Default Cline Modes"
    path = "/home/marc/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline/settings/custom_modes.json"
    # This 'path' must be an absolute path.

    [[sources]]
    name = "Project Example Modes"
    path = "/home/marc/devel/roomodes-editor/examples/cline_custom_modes.json"
    # This 'path' must be an absolute path.
    ```

### 2. Backend Modifications (`main.py`)

*   **Dependencies:** Add `toml` to `pyproject.toml` dependencies (e.g., `"toml>=0.10.2",`).
*   **Configuration Loading:**
    *   Define `CONFIG_FILE_PATH = "config/file_sources.toml"`.
    *   Create a Pydantic model `FileSourceConfig(name: str, path: str, is_valid: bool = True, error_message: Optional[str] = None)`.
    *   Implement `load_file_sources()`:
        *   Reads `config/file_sources.toml`. Handles missing/invalid TOML by logging and raising `SystemExit`.
        *   Validates each entry: `path` must be absolute. Checks JSON file existence and validity, updating `is_valid` and `error_message` on the `FileSourceConfig` instance.
        *   Returns `List[FileSourceConfig]`.
    *   Store loaded sources in global `AVAILABLE_FILES: List[FileSourceConfig]`, called at startup.
*   **API Endpoint for File Sources:**
    *   `GET /api/file-sources`: Returns `AVAILABLE_FILES`.
*   **Modify `read_modes_file()` and `write_modes_file()`:**
    *   Accept `file_path: str` as an argument.
    *   Use `file_path` instead of global `MODES_FILE_PATH`.
    *   `write_modes_file`: Keep central backup in `BACKUP_DIR`, ensuring unique backup filenames (e.g., by incorporating parts of the source path or a unique ID if base names conflict).
*   **Update `/api/modes` Endpoints:**
    *   `GET /api/modes`: Accept query parameter `file_path: str`. Validate against `AVAILABLE_FILES`. Call `read_modes_file(file_path)`.
    *   `POST /api/modes`: Accept `file_path: str` in request body (alongside `modes`). Validate. Call `write_modes_file(modes, file_path)`.
*   **Remove Old Hardcoded Path:** Delete/comment out old `MODES_FILE_PATH`.

### 3. Frontend Modifications (`static/app.js` and `templates/index.html`)

*   **`templates/index.html`:**
    *   Add HTML for file selector dropdown:
        ```html
        <div class="file-selector-container">
            <label for="fileSelector">Select Configuration File:</label>
            <select id="fileSelector"></select>
        </div>
        ```
*   **`static/app.js`:**
    *   Globals: `let currentFilePath = null;`, `let availableFiles = [];`.
    *   `fetchFileSources()`: GET `/api/file-sources`, store in `availableFiles`, call `populateFileSelector()`.
    *   `populateFileSelector()`:
        *   Populates `<select id="fileSelector">` with options from `availableFiles`.
        *   `option.value = file.path; option.textContent = file.name;`.
        *   If `!file.is_valid`, set `option.disabled = true;` and append `(file.error_message)`.
        *   Set `currentFilePath` to the first valid file's path. Set `fileSelector.value`. Trigger `fetchModes()`.
    *   **Event Listener for Dropdown:** On `change`, update `currentFilePath`, call `fetchModes()`.
    *   Modify `fetchModes()`: Use `currentFilePath` in URL: `/api/modes?file_path=\${encodeURIComponent(currentFilePath)}`. Handle null `currentFilePath`.
    *   Modify `handleSaveChanges()`: Include `currentFilePath` in POST body: `{ modes: updatedModes, file_path: currentFilePath }`. Handle null `currentFilePath`.
    *   **Initialization (`DOMContentLoaded`):** Call `fetchFileSources()` to start the process.

### 4. Documentation Updates (`README.md`)

*   Update "Defining the Edited File Path" section.
*   Explain `config/file_sources.toml` (location, purpose, format, absolute paths).
*   Explain the new dropdown menu functionality.
*   Update "Usage / Working with Example Files".

## Mermaid Diagram (Workflow Visualization)

```mermaid
sequenceDiagram
    participant User
    participant Frontend (app.js)
    participant Backend (main.py)
    participant ConfigFile (config/file_sources.toml)
    participant JSONFiles (custom_modes.json, etc.)

    Note over Backend: Application Startup
    Backend->>ConfigFile: Read and parse config/file_sources.toml
    alt config/file_sources.toml missing or invalid
        Backend-->>User: Log error, Exit application
    else config/file_sources.toml valid
        Backend->>JSONFiles: Validate each path and JSON content
        Note over Backend: Stores list of FileSourceConfig (with validity)
    end

    User->>Frontend: Loads page
    Frontend->>Backend: GET /api/file-sources
    Backend-->>Frontend: Returns list of available files (name, path, is_valid, error_message)
    Frontend->>Frontend: populateFileSelector() (disables invalid options)
    Note over Frontend: Selects first valid file as default (currentFilePath)
    Frontend->>Backend: GET /api/modes?file_path=<default_path>
    Backend->>JSONFiles: read_modes_file(default_path)
    Backend-->>Frontend: Returns modes data for default file
    Frontend->>Frontend: renderTable()

    User->>Frontend: Selects a different file from dropdown
    Frontend->>Frontend: Updates currentFilePath
    Frontend->>Backend: GET /api/modes?file_path=<new_selected_path>
    Backend->>JSONFiles: read_modes_file(new_selected_path)
    Backend-->>Frontend: Returns modes data for new file
    Frontend->>Frontend: renderTable()

    User->>Frontend: Edits modes and clicks "Save Changes"
    Frontend->>Backend: POST /api/modes (body: { modes: [...], file_path: currentFilePath })
    Backend->>JSONFiles: write_modes_file(modes, currentFilePath) (with backup)
    Backend-->>Frontend: Returns updated modes data (or success status)
    Frontend->>Frontend: Shows success message, potentially calls fetchModes() to refresh