# Roo Custom Modes Editor

A web-based editor for creating and managing custom modes for Roo.
## Quickstart

### Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Running the Server

```bash
uvicorn main:app --reload
```

## Defining the Edited File Path

The Roo Custom Modes Editor now uses a configuration file, [`config/file_sources.toml`](config/file_sources.toml:1), to determine which JSON files it can edit. This file allows you to define a list of custom mode files, and the editor will provide a dropdown menu to switch between them. See the section below for details on how to configure [`config/file_sources.toml`](config/file_sources.toml:1).

## Configuring File Sources (`config/file_sources.toml`)

The editor uses a TOML file named [`config/file_sources.toml`](config/file_sources.toml:1) located in the `config/` directory of the application to manage the list of JSON files available for editing.

### Location
`config/file_sources.toml`

### Purpose
This file defines a list of JSON configuration files that the Roo Custom Modes Editor can load, display, and save. Each entry in this file will appear as an option in a dropdown menu within the editor's user interface.

### Format
The file must contain an array of `sources` tables. Each table requires two keys:
*   `name`: A descriptive string that will be displayed in the dropdown menu.
*   `path`: The **absolute path** to the JSON file.

**Example:**
```toml
# Example: config/file_sources.toml
[[sources]]
name = "Descriptive Name for Dropdown"
path = "/absolute/path/to/your/custom_modes.json"

[[sources]]
name = "Another Example"
path = "/another/absolute/path/to/another_modes.json"
```

**Important:**
*   Paths **must be absolute**. Relative paths are not supported.
*   If a file path specified in [`config/file_sources.toml`](config/file_sources.toml:1) is invalid (e.g., the file doesn't exist, is not readable, or is not valid JSON), that option will be disabled in the dropdown menu, and an error message may be logged in the server console.

## Using the File Selector Dropdown

The editor's user interface now features a dropdown menu. This menu is populated with the `name` entries from the [`config/file_sources.toml`](config/file_sources.toml:1) file.

*   **Switching Files**: Selecting an option from the dropdown will load the corresponding JSON file into the editor.
*   **Default File**: The first valid file listed in [`config/file_sources.toml`](config/file_sources.toml:1) will be loaded by default when the application starts.
*   **Saving Changes**: When you save your changes, they will be written back to the currently selected JSON file.

## Usage / Working with Example Files

To use the editor with an example configuration file, such as [`examples/cline_custom_modes.json`](examples/cline_custom_modes.json:1), you need to add it to your [`config/file_sources.toml`](config/file_sources.toml:1) file.

1.  **Locate `config/file_sources.toml`**: This file is in the `config/` directory of the application. If it doesn't exist, you may need to create it based on the format described above.

2.  **Add the Example File**: Edit [`config/file_sources.toml`](config/file_sources.toml:1) and add a new source entry for the example file. You will need to provide its **absolute path**.

    For example, if your application is cloned at `/home/user/dev/roomodes-editor`, the entry might look like this:

    ```toml
    [[sources]]
    name = "Example Cline Custom Modes"
    path = "/home/user/dev/roomodes-editor/examples/cline_custom_modes.json"
    ```
    **Note:** Replace `/home/user/dev/roomodes-editor` with the actual absolute path to your project directory.

3.  **Run the Editor**: Start the Roo Custom Modes Editor as described in the "Running the Server" section.

4.  **Select the Example File**: In the editor's UI, use the dropdown menu to select "Example Cline Custom Modes" (or whatever name you provided).

5.  **Edit and Save**: You can now view, modify, and save the [`examples/cline_custom_modes.json`](examples/cline_custom_modes.json:1) file directly through the editor. Changes will be saved to the path specified in [`config/file_sources.toml`](config/file_sources.toml:1).

