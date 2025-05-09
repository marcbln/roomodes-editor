let modes = [];
let selectedModes = new Set();
let currentFilePath = null;
let availableFiles = [];

// Fetch file sources from the API
async function fetchFileSources() {
    try {
        const response = await fetch('/api/file-sources');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        availableFiles = await response.json();
        populateFileSelector();
        showStatus('File sources loaded successfully', false);
    } catch (error) {
        console.error('Error fetching file sources:', error);
        showStatus(`Error fetching file sources: ${error.message}`, true);
    }
}

// Populate the file selector dropdown
function populateFileSelector() {
    const fileSelector = document.getElementById('fileSelector');
    if (!fileSelector) {
        console.error('File selector element not found');
        return;
    }
    fileSelector.innerHTML = ''; // Clear existing options

    let firstValidPath = null;

    availableFiles.forEach(file => {
        const option = document.createElement('option');
        option.value = file.path;
        option.textContent = file.name;
        if (!file.is_valid) {
            option.disabled = true;
            option.textContent += ` (Error: ${file.error_message || 'Invalid or unreadable'})`;
        } else if (!firstValidPath) {
            firstValidPath = file.path;
        }
        fileSelector.appendChild(option);
    });

    if (firstValidPath) {
        currentFilePath = firstValidPath;
        fileSelector.value = currentFilePath;
        fetchModes(); // Load modes for the default valid file
    } else {
        currentFilePath = null;
        // Optionally, display a message or disable UI elements
        // For now, ensure fetchModes handles currentFilePath being null
        fetchModes(); // This will now handle null currentFilePath
    }
}


// Fetch modes from the API
async function fetchModes() {
    if (!currentFilePath) {
        const tableBody = document.getElementById('modesTableBody');
        if (tableBody) tableBody.innerHTML = ''; // Clear table
        modes = []; // Clear modes array
        showStatus('No file selected. Please select a file to load modes.', true);
        return;
    }
    try {
        const response = await fetch(`/api/modes?file_path=${encodeURIComponent(currentFilePath)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        modes = await response.json();
        renderTable();
        showStatus('Modes loaded successfully', false);
    } catch (error) {
        console.error('Error fetching modes:', error);
        showStatus(`Error fetching modes: ${error.message}`, true);
    }
}

// Render the modes table
function renderTable() {
    const tableBody = document.getElementById('modesTableBody');
    tableBody.innerHTML = '';

    modes.forEach(mode => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><input type="checkbox" class="mode-checkbox" data-slug="${mode.slug}"></td>
            <td><input type="text" value="${mode.slug}" data-field="slug"></td>
            <td><input type="text" value="${mode.name}" data-field="name"></td>
            <td><input type="text" value="${mode.description}" data-field="description"></td>
            <td><input type="text" value="${mode.model}" data-field="model"></td>
            <td><input type="text" value="${mode.system_prompt}" data-field="system_prompt"></td>
        `;
        tableBody.appendChild(row);
    });

    // Add event listeners to checkboxes
    document.querySelectorAll('.mode-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                selectedModes.add(this.dataset.slug);
            } else {
                selectedModes.delete(this.dataset.slug);
            }
        });
    });
}

// Add a new mode
function handleAddMode() {
    const newMode = {
        slug: 'new-mode',
        name: 'New Mode',
        description: 'Description for new mode',
        model: 'default-model',
        system_prompt: 'System prompt for new mode'
    };

    modes.push(newMode);
    renderTable();
    showStatus('New mode added. Edit the details and save changes.', false);
}

// Delete selected modes
function handleDeleteMode() {
    if (selectedModes.size === 0) {
        showStatus('Please select at least one mode to delete.', true);
        return;
    }

    modes = modes.filter(mode => !selectedModes.has(mode.slug));
    selectedModes.clear();
    renderTable();
    showStatus('Selected modes deleted successfully.', false);
}

// Save changes to the API
async function handleSaveChanges() {
    if (!currentFilePath) {
        showStatus('No file selected. Please select a file before saving.', true);
        return;
    }
    // Collect updated mode data from the table
    const updatedModes = [];
    const rows = document.querySelectorAll('#modesTableBody tr');

    rows.forEach(row => {
        const slugInput = row.querySelector('[data-field="slug"]');
        const nameInput = row.querySelector('[data-field="name"]');
        const descriptionInput = row.querySelector('[data-field="description"]');
        const modelInput = row.querySelector('[data-field="model"]');
        const systemPromptInput = row.querySelector('[data-field="system_prompt"]');

        updatedModes.push({
            slug: slugInput.value,
            name: nameInput.value,
            description: descriptionInput.value,
            model: modelInput.value,
            system_prompt: systemPromptInput.value
        });
    });

    try {
        const response = await fetch('/api/modes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ modes: updatedModes, file_path: currentFilePath })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        showStatus('Changes saved successfully!', false);
        // Refresh the data after saving
        await fetchModes();
    } catch (error) {
        console.error('Error saving changes:', error);
        showStatus(`Error saving changes: ${error.message}`, true);
    }
}

// Initialize the editor
document.addEventListener('DOMContentLoaded', function() {
    fetchFileSources(); // Fetch file sources first
    // fetchModes(); // fetchModes will be called by populateFileSelector
    setupEventListeners();
});

function setupEventListeners() {
    const fileSelector = document.getElementById('fileSelector');
    if (fileSelector) {
        fileSelector.addEventListener('change', function(event) {
            currentFilePath = event.target.value;
            fetchModes();
        });
    } else {
        console.error('File selector element not found for event listener setup');
    }

    document.getElementById('addModeBtn').addEventListener('click', handleAddMode);
    document.getElementById('deleteModeBtn').addEventListener('click', handleDeleteMode);
    document.getElementById('saveChangesBtn').addEventListener('click', handleSaveChanges);
}

function showStatus(message, isError = false) {
    const statusElement = document.getElementById('statusMessage');
    statusElement.textContent = message;
    statusElement.className = isError ? 'status-message error' : 'status-message success';
}
