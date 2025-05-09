# Plan: Update README.md and pyproject.toml

**Objective:**
1.  Correct the dependencies and other metadata in `roomodes-editor/pyproject.toml`.
2.  Add a "Quickstart" section to `roomodes-editor/README.md` with installation and server run instructions.

## Detailed Plan

### 1. Update `roomodes-editor/pyproject.toml`

*   **Modify the `[project]` section:**
    *   Replace the current `dependencies` list with:
        ```toml
        dependencies = [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0", # For running the server
            "pydantic>=2.0.0",  # For data validation (used in models.py)
            "jinja2>=3.0.0",    # For HTML templating
            "python-multipart>=0.0.6" # For form data, often useful with FastAPI
        ]
        ```
    *   Add the Python version requirement:
        ```toml
        requires-python = ">=3.10"
        ```
    *   Update the `authors` field to use the placeholder:
        ```toml
        authors = [
            {name = "AI Developer", email = "ai@example.com"},
        ]
        ```
*   **Modify the `[tool.hatch.build.targets.wheel]` section:**
    *   Remove the line `packages = ["src/roomodes-editor"]`.

### 2. Update `roomodes-editor/README.md`

*   Add a new level 2 heading: `## Quickstart`
*   Under "Quickstart", add a level 3 heading: `### Installation`
    *   Include the installation commands:
        ```bash
        uv venv
        source .venv/bin/activate
        uv pip install -e .
        ```
*   Under "Quickstart", add another level 3 heading: `### Running the Server`
    *   Include the command to run the FastAPI server:
        ```bash
        uvicorn main:app --reload
        ```

## Visual Plan (Mermaid Diagram)

```mermaid
graph TD
    A[Start Task] --> B{Update pyproject.toml};
    B --> B1[Replace 'flask' with FastAPI dependencies];
    B --> B2[Add 'requires-python = ">=3.10"'];
    B --> B3[Use placeholder 'authors' details];
    B --> B4[Remove 'packages' line from [tool.hatch.build.targets.wheel]];
    
    A --> C{Update README.md};
    C --> C1[Add '## Quickstart' section];
    C1 --> C2[Add '### Installation' subsection with commands];
    C1 --> C3[Add '### Running the Server' subsection with 'uvicorn main:app --reload'];
    
    B4 --> D[pyproject.toml Updated];
    C3 --> E[README.md Updated];
    D --> F[Task Steps Complete];
    E --> F;
```

**Plan Confirmation:**
*   Author details for `pyproject.toml`: Placeholder "AI Developer" and "ai@example.com".
*   Overall plan approved by user.