// Global variables for dashboard and logging
let dashboardInterval = null;
let eventSource = null;
let isStreamPaused = false;
let logHistoryCache = [];
let lastDashboardStatus = null;
const departmentCache = new Map();
const docTypeCache = new Map();

function inlineIcon(name) {
    return `<svg class="ui-icon" aria-hidden="true" focusable="false"><use href="#icon-${name}"></use></svg>`;
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    }[character]));
}

function parsePathPatterns(value) {
    return value.split('\n').map(pattern => pattern.trim()).filter(Boolean);
}

// Helper API Request wrapper
async function apiRequest(url, options = {}) {
    options.headers = options.headers || {};
    if (!(options.body instanceof FormData) && typeof options.body === 'object') {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    const res = await fetch(url, options);
    if (res.status === 401) {
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        throw new Error(data.detail || data.message || 'API Request Failed');
    }
    return data;
}

// --- DASHBOARD ---
function initDashboard() {
    updateDashboardStatus();
    loadRecentRuns();
    dashboardInterval = setInterval(updateDashboardStatus, 3000);
}

async function updateDashboardStatus() {
    try {
        const data = await apiRequest('/api/index/status');
        const badge = document.getElementById('status-badge');
        const btnStart = document.getElementById('btn-start-index');
        const btnStop = document.getElementById('btn-stop-index');

        if (badge) {
            badge.className = `badge badge-${data.status.toLowerCase()}`;
            badge.innerText = data.status;
        }

        const progressLabel = document.getElementById('progress-percentage');
        const progressBar = document.getElementById('progress-bar-fill');
        const processedCount = document.getElementById('processed-count');
        const discoveredCount = document.getElementById('discovered-count');
        const progressHint = document.getElementById('progress-hint');
        const discoveryIndicator = document.getElementById('discovery-indicator');
        const isDiscovering = data.status === 'RUNNING' && !data.discovery_complete;
        if (progressLabel) progressLabel.innerText = data.progress_percentage == null ? '…' : `${data.progress_percentage}%`;
        if (progressBar) {
            progressBar.style.width = data.progress_percentage == null ? '35%' : `${data.progress_percentage}%`;
            progressBar.classList.toggle('progress-indeterminate', data.progress_percentage == null);
        }
        if (processedCount) processedCount.innerText = data.processed_files || 0;
        if (discoveredCount) discoveredCount.innerText = data.discovery_complete
            ? (data.discovered_files ?? data.total_files ?? 0)
            : `${data.discovered_files || 0}…`;
        if (progressHint) progressHint.innerText = isDiscovering ? 'Discovering files' : (data.status === 'STOPPING' ? 'Stopping — finishing in-progress files...' : '');
        if (discoveryIndicator) discoveryIndicator.style.display = isDiscovering ? 'flex' : 'none';
        const indexedCount = document.getElementById('indexed-count');
        if (indexedCount) indexedCount.innerText = data.indexed_files || 0;

        document.getElementById('stat-indexed').innerText = data.indexed_files || 0;
        const statDiscovered = document.getElementById('stat-discovered');
        if (statDiscovered) statDiscovered.innerText = data.discovered_files || 0;
        document.getElementById('stat-skipped').innerText = data.skipped_files || 0;
        document.getElementById('stat-failed').innerText = data.failed_files || 0;
        document.getElementById('stat-deleted').innerText = data.deleted_files || 0;

        if (data.status === 'RUNNING') {
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = false;
        } else if (data.status === 'STOPPING') {
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = true;
        } else {
            if (btnStart) btnStart.disabled = false;
            if (btnStop) btnStop.disabled = true;
            if ((data.status === 'COMPLETED' || data.status === 'STOPPED' || data.status === 'FAILED') && lastDashboardStatus !== data.status) {
                loadRecentRuns();
            }
        }
        lastDashboardStatus = data.status;
    } catch (err) {
        console.error("Dashboard status update error:", err);
    }
}

async function startIndexing() {
    try {
        await apiRequest('/api/index/start', { method: 'POST' });
        updateDashboardStatus();
    } catch (err) {
        alert("Error starting index run: " + err.message);
    }
}

async function stopIndexing() {
    try {
        await apiRequest('/api/index/stop', { method: 'POST' });
        updateDashboardStatus();
    } catch (err) {
        alert("Error stopping index run: " + err.message);
    }
}

async function loadRecentRuns() {
    try {
        const data = await apiRequest('/api/index/runs?page=1&per_page=5');
        const tbody = document.querySelector('#recent-runs-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">No recent runs found</td></tr>';
            return;
        }

        data.items.forEach(run => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${run.id}</td>
                <td><span class="badge badge-${run.status.toLowerCase()}">${run.status}</span></td>
                <td>${run.started_at ? new Date(run.started_at).toLocaleString() : '-'}</td>
                <td>${run.stopped_at ? new Date(run.stopped_at).toLocaleString() : '-'}</td>
                <td>${run.discovered_files ?? run.total_files ?? 0}</td>
                <td>${run.indexed_files}</td>
                <td>${run.skipped_files}</td>
                <td>${run.failed_files}</td>
                <td>${run.deleted_files}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to load recent runs:", err);
    }
}

// --- FOLDERS ---
async function loadFolders() {
    try {
        const folders = await apiRequest('/api/config/folders');
        const tbody = document.querySelector('#folders-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        folders.forEach(f => {
            const tr = document.createElement('tr');
            tr.dataset.folderId = f.id;
            tr.innerHTML = `
                <td>#${f.id}</td>
                <td><code>${escapeHtml(f.path)}</code></td>
                <td><span class="badge badge-idle">${f.status}</span></td>
                <td>${f.updated_at ? new Date(f.updated_at).toLocaleString() : '-'}</td>
                <td><button class="btn btn-danger" data-folder-delete="${f.id}" onclick="deleteFolder(${f.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading folders: " + err.message);
    }
}

async function addFolder() {
    const input = document.getElementById('folder-path-input');
    if (!input.value.trim()) return;
    try {
        await apiRequest('/api/config/folders', { method: 'POST', body: { path: input.value.trim() } });
        input.value = '';
        loadFolders();
    } catch (err) {
        alert(err.message);
    }
}

let folderDeleteTimer = null;
let folderDeleteStartedAt = null;

function setFolderDeleteControlsDisabled(disabled) {
    document.querySelectorAll('#folders-table button[data-folder-delete], #add-folder-form input, #add-folder-form button')
        .forEach(element => {
            element.disabled = disabled;
        });
}

function updateFolderDeleteElapsed() {
    const elapsed = document.getElementById('folder-delete-elapsed');
    if (!elapsed || !folderDeleteStartedAt) return;
    const seconds = Math.max(0, Math.floor((Date.now() - folderDeleteStartedAt) / 1000));
    elapsed.textContent = `Elapsed: ${seconds}s`;
}

function setFolderDeleteStep(step, state) {
    const element = document.querySelector(`[data-delete-step="${step}"]`);
    if (element) element.dataset.state = state;
}

function showFolderDeleteProgress(path) {
    const overlay = document.getElementById('folder-delete-overlay');
    const dialog = overlay?.querySelector('.operation-dialog');
    if (!overlay || !dialog) return;

    folderDeleteStartedAt = Date.now();
    updateFolderDeleteElapsed();
    folderDeleteTimer = window.setInterval(updateFolderDeleteElapsed, 1000);
    overlay.hidden = false;
    overlay.setAttribute('aria-hidden', 'false');
    dialog.dataset.state = 'running';
    document.getElementById('folder-delete-title').textContent = 'Deleting folder';
    document.getElementById('folder-delete-path').textContent = path;
    document.getElementById('folder-delete-message').textContent =
        'The server is removing every matching Qdrant point before deleting the folder configuration. Do not close this page.';
    document.getElementById('folder-delete-close').hidden = true;
    setFolderDeleteStep('verify', 'complete');
    setFolderDeleteStep('qdrant', 'active');
    setFolderDeleteStep('folder', 'pending');
    setFolderDeleteControlsDisabled(true);
}

function updateFolderDeleteProgress(state, message) {
    const overlay = document.getElementById('folder-delete-overlay');
    const dialog = overlay?.querySelector('.operation-dialog');
    if (!dialog) return;
    dialog.dataset.state = state;
    document.getElementById('folder-delete-message').textContent = message;
}

function closeFolderDeleteProgress() {
    const overlay = document.getElementById('folder-delete-overlay');
    if (folderDeleteTimer) {
        window.clearInterval(folderDeleteTimer);
        folderDeleteTimer = null;
    }
    folderDeleteStartedAt = null;
    if (overlay) {
        overlay.hidden = true;
        overlay.setAttribute('aria-hidden', 'true');
    }
    setFolderDeleteControlsDisabled(false);
}

function showFolderDeleteError(message) {
    const closeButton = document.getElementById('folder-delete-close');
    updateFolderDeleteProgress('error', message);
    setFolderDeleteStep('qdrant', 'error');
    setFolderDeleteStep('folder', 'pending');
    if (closeButton) closeButton.hidden = false;
}

async function deleteFolder(id) {
    if (!confirm('This will remove the folder and all of its Qdrant points. Continue?')) return;
    const row = document.querySelector(`#folders-table tr[data-folder-id="${id}"]`);
    const deleteButton = row?.querySelector('[data-folder-delete]');
    const folderPath = row?.querySelector('td:nth-child(2)')?.textContent?.trim() || `folder #${id}`;
    try {
        if (deleteButton) {
            deleteButton.disabled = true;
            deleteButton.textContent = 'Preparing...';
        }
        const challenge = await apiRequest(`/api/config/folders/${id}/delete-challenge`, { method: 'POST' });
        const code = window.prompt(
            `Enter the six-digit verification code to permanently delete this folder:\n\n${challenge.code}`,
            ''
        );
        if (code === null) {
            if (deleteButton) {
                deleteButton.disabled = false;
                deleteButton.textContent = 'Delete';
            }
            return;
        }
        if (!/^\d{6}$/.test(code.trim())) {
            throw new Error('Enter the six-digit verification code exactly as shown.');
        }
        showFolderDeleteProgress(folderPath);
        const result = await apiRequest(`/api/config/folders/${id}`, {
            method: 'DELETE',
            body: {
                challenge_id: challenge.challenge_id,
                code: code.trim()
            }
        });
        const legacyDeleted = result.qdrant_deletion?.legacy_points_deleted || 0;
        const mode = result.qdrant_deletion?.mode || 'filter';
        setFolderDeleteStep('qdrant', 'complete');
        setFolderDeleteStep('folder', 'complete');
        updateFolderDeleteProgress(
            'success',
            `Deletion complete. Qdrant cleanup: ${mode}; legacy points removed: ${legacyDeleted}.`
        );
        document.getElementById('folder-delete-title').textContent = 'Folder deleted';
        await new Promise(resolve => window.setTimeout(resolve, 900));
        closeFolderDeleteProgress();
        await loadFolders();
    } catch (err) {
        const overlay = document.getElementById('folder-delete-overlay');
        if (overlay && !overlay.hidden) {
            showFolderDeleteError(err.message);
        } else {
            alert(err.message);
            if (deleteButton) {
                deleteButton.disabled = false;
                deleteButton.textContent = 'Delete';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('folder-delete-close')?.addEventListener('click', closeFolderDeleteProgress);
});

// --- EXCLUSIONS ---
async function loadExclusions() {
    try {
        const exclusions = await apiRequest('/api/config/exclusions');
        const tbody = document.querySelector('#exclusions-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        exclusions.forEach(ex => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${ex.id}</td>
                <td><code>${ex.value}</code></td>
                <td><span class="badge badge-idle">${ex.type}</span></td>
                <td><button class="btn btn-danger" onclick="deleteExclusion(${ex.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading exclusions: " + err.message);
    }
}

async function addExclusion() {
    const val = document.getElementById('ex-value-input').value.trim();
    const type = document.getElementById('ex-type-select').value;
    if (!val) return;
    try {
        await apiRequest('/api/config/exclusions', { method: 'POST', body: { value: val, type: type } });
        document.getElementById('ex-value-input').value = '';
        loadExclusions();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteExclusion(id) {
    if (!confirm('Delete this exclusion rule?')) return;
    try {
        await apiRequest(`/api/config/exclusions/${id}`, { method: 'DELETE' });
        loadExclusions();
    } catch (err) {
        alert(err.message);
    }
}

// --- FILE TYPES ---
async function loadFileTypes() {
    try {
        const types = await apiRequest('/api/config/file-types');
        const tbody = document.querySelector('#file-types-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        types.forEach(ft => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${ft.extension}</code></td>
                <td>
                    <select onchange="updateFileType(${ft.id}, this.value, ${ft.enabled})">
                        <option value="excel" ${ft.chunker === 'excel' ? 'selected' : ''}>Excel / Tabular</option>
                        <option value="heading" ${ft.chunker === 'heading' ? 'selected' : ''}>Heading-Aware</option>
                        <option value="slide" ${ft.chunker === 'slide' ? 'selected' : ''}>Slide-Based</option>
                        <option value="generic" ${ft.chunker === 'generic' ? 'selected' : ''}>Generic Recursive</option>
                    </select>
                </td>
                <td>
                    <input type="checkbox" ${ft.enabled ? 'checked' : ''} onchange="updateFileType(${ft.id}, '${ft.chunker}', this.checked ? 1 : 0)">
                </td>
                <td><button class="btn btn-danger" onclick="deleteFileType(${ft.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading file types: " + err.message);
    }
}

async function addFileType() {
    const ext = document.getElementById('ft-ext-input').value.trim();
    const chunker = document.getElementById('ft-chunker-select').value;
    if (!ext) return;
    try {
        await apiRequest('/api/config/file-types', { method: 'POST', body: { extension: ext, chunker: chunker, enabled: 1 } });
        document.getElementById('ft-ext-input').value = '';
        loadFileTypes();
    } catch (err) {
        alert(err.message);
    }
}

async function updateFileType(id, chunker, enabled) {
    try {
        await apiRequest(`/api/config/file-types/${id}`, { method: 'PUT', body: { chunker: chunker, enabled: enabled } });
    } catch (err) {
        alert(err.message);
    }
}

async function deleteFileType(id) {
    if (!confirm('Delete this file type mapping?')) return;
    try {
        await apiRequest(`/api/config/file-types/${id}`, { method: 'DELETE' });
        loadFileTypes();
    } catch (err) {
        alert(err.message);
    }
}

// --- DEPARTMENTS ---
async function loadDepartments() {
    try {
        const list = await apiRequest('/api/config/departments');
        const tbody = document.querySelector('#departments-table tbody');
        if (!tbody) return;
        departmentCache.clear();
        tbody.innerHTML = '';

        list.forEach(d => {
            departmentCache.set(d.id, d);
            const tr = document.createElement('tr');
            tr.id = `department-row-${d.id}`;
            tr.innerHTML = `
                <td>#${d.id}</td>
                <td><strong>${escapeHtml(d.name)}</strong></td>
                <td><code>${escapeHtml(d.path_patterns.join(', '))}</code></td>
                <td class="table-actions">
                    <button class="btn btn-secondary btn-sm" onclick="editDepartment(${d.id})">${inlineIcon('edit')} Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDepartment(${d.id})">${inlineIcon('trash')} Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading departments: " + err.message);
    }
}

function editDepartment(id) {
    const department = departmentCache.get(id);
    const row = document.getElementById(`department-row-${id}`);
    if (!department || !row) return;

    row.innerHTML = `
        <td>#${id}</td>
        <td><input type="text" id="department-edit-name-${id}" value="${escapeHtml(department.name)}" aria-label="Department name"></td>
        <td><textarea id="department-edit-patterns-${id}" rows="2" aria-label="Department path patterns">${escapeHtml(department.path_patterns.join('\n'))}</textarea></td>
        <td class="table-actions">
            <button class="btn btn-primary btn-sm" onclick="saveDepartmentEdit(${id})">${inlineIcon('save')} Save</button>
            <button class="btn btn-secondary btn-sm" onclick="loadDepartments()">${inlineIcon('x-circle')} Cancel</button>
        </td>
    `;
    document.getElementById(`department-edit-name-${id}`).focus();
}

async function saveDepartmentEdit(id) {
    const name = document.getElementById(`department-edit-name-${id}`).value.trim();
    const patterns = parsePathPatterns(document.getElementById(`department-edit-patterns-${id}`).value);
    if (!name || patterns.length === 0) {
        alert('Department name and at least one path pattern are required.');
        return;
    }

    try {
        await apiRequest(`/api/config/departments/${id}`, {
            method: 'PUT',
            body: { name, path_patterns: patterns }
        });
        loadDepartments();
    } catch (err) {
        alert(err.message);
    }
}

async function addDepartment() {
    const name = document.getElementById('dept-name').value.trim();
    const patternsRaw = document.getElementById('dept-patterns').value.trim();
    if (!name || !patternsRaw) return;

    const patterns = parsePathPatterns(patternsRaw);
    try {
        await apiRequest('/api/config/departments', { method: 'POST', body: { name: name, path_patterns: patterns } });
        document.getElementById('dept-name').value = '';
        document.getElementById('dept-patterns').value = '';
        loadDepartments();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteDepartment(id) {
    if (!confirm('Delete department rule?')) return;
    try {
        await apiRequest(`/api/config/departments/${id}`, { method: 'DELETE' });
        loadDepartments();
    } catch (err) {
        alert(err.message);
    }
}

// --- DOC TYPES ---
async function loadDocTypes() {
    try {
        const list = await apiRequest('/api/config/doc-types');
        const tbody = document.querySelector('#doctypes-table tbody');
        if (!tbody) return;
        docTypeCache.clear();
        tbody.innerHTML = '';

        list.forEach(dt => {
            docTypeCache.set(dt.id, dt);
            const tr = document.createElement('tr');
            tr.id = `doctype-row-${dt.id}`;
            tr.innerHTML = `
                <td>#${dt.id}</td>
                <td><strong>${escapeHtml(dt.name)}</strong></td>
                <td><code>${escapeHtml(dt.path_patterns.join(', '))}</code></td>
                <td class="table-actions">
                    <button class="btn btn-secondary btn-sm" onclick="editDocType(${dt.id})">${inlineIcon('edit')} Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDocType(${dt.id})">${inlineIcon('trash')} Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading doc types: " + err.message);
    }
}

function editDocType(id) {
    const docType = docTypeCache.get(id);
    const row = document.getElementById(`doctype-row-${id}`);
    if (!docType || !row) return;

    row.innerHTML = `
        <td>#${id}</td>
        <td><input type="text" id="doctype-edit-name-${id}" value="${escapeHtml(docType.name)}" aria-label="Doc type name"></td>
        <td><textarea id="doctype-edit-patterns-${id}" rows="2" aria-label="Doc type path patterns">${escapeHtml(docType.path_patterns.join('\n'))}</textarea></td>
        <td class="table-actions">
            <button class="btn btn-primary btn-sm" onclick="saveDocTypeEdit(${id})">${inlineIcon('save')} Save</button>
            <button class="btn btn-secondary btn-sm" onclick="loadDocTypes()">${inlineIcon('x-circle')} Cancel</button>
        </td>
    `;
    document.getElementById(`doctype-edit-name-${id}`).focus();
}

async function saveDocTypeEdit(id) {
    const name = document.getElementById(`doctype-edit-name-${id}`).value.trim();
    const patterns = parsePathPatterns(document.getElementById(`doctype-edit-patterns-${id}`).value);
    if (!name || patterns.length === 0) {
        alert('Doc type name and at least one path pattern are required.');
        return;
    }

    try {
        await apiRequest(`/api/config/doc-types/${id}`, {
            method: 'PUT',
            body: { name, path_patterns: patterns }
        });
        loadDocTypes();
    } catch (err) {
        alert(err.message);
    }
}

async function addDocType() {
    const name = document.getElementById('dt-name').value.trim();
    const patternsRaw = document.getElementById('dt-patterns').value.trim();
    if (!name || !patternsRaw) return;

    const patterns = parsePathPatterns(patternsRaw);
    try {
        await apiRequest('/api/config/doc-types', { method: 'POST', body: { name: name, path_patterns: patterns } });
        document.getElementById('dt-name').value = '';
        document.getElementById('dt-patterns').value = '';
        loadDocTypes();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteDocType(id) {
    if (!confirm('Delete doc type rule?')) return;
    try {
        await apiRequest(`/api/config/doc-types/${id}`, { method: 'DELETE' });
        loadDocTypes();
    } catch (err) {
        alert(err.message);
    }
}

// --- SYNONYMS ---
async function loadSynonyms() {
    try {
        const list = await apiRequest('/api/config/synonyms');
        const tbody = document.querySelector('#synonyms-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        list.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${s.id}</td>
                <td><strong>${s.term}</strong></td>
                <td><code>${s.synonyms.join(', ')}</code></td>
                <td><button class="btn btn-danger" onclick="deleteSynonym(${s.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading synonyms: " + err.message);
    }
}

async function addSynonym() {
    const term = document.getElementById('syn-term').value.trim();
    const listRaw = document.getElementById('syn-list').value.trim();
    if (!term || !listRaw) return;

    const synonyms = listRaw.split(',').map(s => s.trim()).filter(Boolean);
    try {
        await apiRequest('/api/config/synonyms', { method: 'POST', body: { term: term, synonyms: synonyms } });
        document.getElementById('syn-term').value = '';
        document.getElementById('syn-list').value = '';
        loadSynonyms();
    } catch (err) {
        alert(err.message);
    }
}

async function deleteSynonym(id) {
    if (!confirm('Delete synonym entry?')) return;
    try {
        await apiRequest(`/api/config/synonyms/${id}`, { method: 'DELETE' });
        loadSynonyms();
    } catch (err) {
        alert(err.message);
    }
}

// --- INCREMENTAL XML ---
async function loadXmlConfig() {
    try {
        const data = await apiRequest('/api/incremental/config');
        document.getElementById('changed-xml-path').value = data.changed_xml_path || '';
        document.getElementById('deleted-xml-path').value = data.deleted_xml_path || '';
    } catch (err) {
        console.error("Failed loading incremental XML config:", err);
    }
}

async function saveXmlConfig() {
    const c = document.getElementById('changed-xml-path').value.trim();
    const d = document.getElementById('deleted-xml-path').value.trim();
    try {
        await apiRequest('/api/incremental/config', { method: 'POST', body: { changed_xml_path: c, deleted_xml_path: d } });
        alert("Incremental XML paths saved!");
    } catch (err) {
        alert(err.message);
    }
}

async function previewXml() {
    const c = document.getElementById('changed-xml-path').value.trim();
    const d = document.getElementById('deleted-xml-path').value.trim();
    try {
        const res = await apiRequest('/api/incremental/preview', { method: 'POST', body: { changed_xml_path: c, deleted_xml_path: d } });
        const card = document.getElementById('preview-card');
        const tbody = document.querySelector('#preview-table tbody');
        document.getElementById('preview-count').innerText = res.total_affected;
        tbody.innerHTML = '';
        card.style.display = 'block';

        res.items.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="badge badge-idle">${item.source}</span></td>
                <td><code>${item.type}</code></td>
                <td><code>${item.converted_path}</code></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert(err.message);
    }
}

// --- SETTINGS ---
async function loadSettings() {
    try {
        const cfg = await apiRequest('/api/config/settings');
        const requiredSettings = [
            'conversion_timeout_seconds',
            'qdrant_timeout_seconds',
            'queue_put_timeout_seconds',
            'worker_shutdown_timeout_seconds'
        ];
        const missingSettings = requiredSettings.filter(name => cfg[name] == null);
        if (missingSettings.length > 0) {
            throw new Error(`Settings API response is missing: ${missingSettings.join(', ')}`);
        }
        document.getElementById('embedding-model').value = cfg.embedding_model;
        document.getElementById('embedding-dimensions').value = cfg.embedding_dimensions;
        document.getElementById('parallel-workers').value = cfg.parallel_workers;
        document.getElementById('index-queue-capacity').value = cfg.index_queue_capacity;
        document.getElementById('embedding-batch-size').value = cfg.embedding_batch_size;
        document.getElementById('embedding-concurrency').value = cfg.embedding_concurrency;
        document.getElementById('qdrant-upsert-batch-size').value = cfg.qdrant_upsert_batch_size;
        document.getElementById('qdrant-upsert-max-bytes').value = cfg.qdrant_upsert_max_bytes;
        document.getElementById('max-file-size-mb').value = cfg.max_file_size_mb;
        document.getElementById('max-markdown-chars').value = cfg.max_markdown_chars;
        document.getElementById('max-chunk-chars').value = cfg.max_chunk_chars;
        document.getElementById('conversion-timeout-seconds').value = cfg.conversion_timeout_seconds;
        document.getElementById('qdrant-timeout-seconds').value = cfg.qdrant_timeout_seconds;
        document.getElementById('queue-put-timeout-seconds').value = cfg.queue_put_timeout_seconds;
        document.getElementById('worker-shutdown-timeout-seconds').value = cfg.worker_shutdown_timeout_seconds;
        document.getElementById('chunk-size').value = cfg.chunk_size;
        document.getElementById('chunk-overlap').value = cfg.chunk_overlap;
        document.getElementById('rows-per-chunk').value = cfg.rows_per_chunk;
        document.getElementById('log-level').value = cfg.log_level;
        document.getElementById('qdrant-host').value = cfg.qdrant_host;
        document.getElementById('qdrant-port').value = cfg.qdrant_port;
        document.getElementById('collection-name').value = cfg.collection_name;
        document.getElementById('search-top-k').value = cfg.search_top_k;
        document.getElementById('search-per-page').value = cfg.search_per_page;
        document.getElementById('search-excerpt-count').value = cfg.search_excerpt_count;
    } catch (err) {
        alert("Failed loading settings: " + err.message);
    }
}

async function saveSettings() {
    const payload = {
        embedding_model: document.getElementById('embedding-model').value.trim(),
        embedding_dimensions: parseInt(document.getElementById('embedding-dimensions').value),
        parallel_workers: parseInt(document.getElementById('parallel-workers').value),
        index_workers: parseInt(document.getElementById('parallel-workers').value),
        index_queue_capacity: parseInt(document.getElementById('index-queue-capacity').value),
        embedding_batch_size: parseInt(document.getElementById('embedding-batch-size').value),
        embedding_concurrency: parseInt(document.getElementById('embedding-concurrency').value),
        qdrant_upsert_batch_size: parseInt(document.getElementById('qdrant-upsert-batch-size').value),
        qdrant_upsert_max_bytes: parseInt(document.getElementById('qdrant-upsert-max-bytes').value),
        max_file_size_mb: parseInt(document.getElementById('max-file-size-mb').value),
        max_markdown_chars: parseInt(document.getElementById('max-markdown-chars').value),
        max_chunk_chars: parseInt(document.getElementById('max-chunk-chars').value),
        conversion_timeout_seconds: parseFloat(document.getElementById('conversion-timeout-seconds').value),
        qdrant_timeout_seconds: parseFloat(document.getElementById('qdrant-timeout-seconds').value),
        queue_put_timeout_seconds: parseFloat(document.getElementById('queue-put-timeout-seconds').value),
        worker_shutdown_timeout_seconds: parseFloat(document.getElementById('worker-shutdown-timeout-seconds').value),
        chunk_size: parseInt(document.getElementById('chunk-size').value),
        chunk_overlap: parseInt(document.getElementById('chunk-overlap').value),
        rows_per_chunk: parseInt(document.getElementById('rows-per-chunk').value),
        log_level: document.getElementById('log-level').value,
        qdrant_host: document.getElementById('qdrant-host').value.trim(),
        qdrant_port: parseInt(document.getElementById('qdrant-port').value),
        collection_name: document.getElementById('collection-name').value.trim(),
        search_top_k: parseInt(document.getElementById('search-top-k').value),
        search_per_page: parseInt(document.getElementById('search-per-page').value),
        search_excerpt_count: parseInt(document.getElementById('search-excerpt-count').value),
        old_password: document.getElementById('old-password').value || null,
        new_password: document.getElementById('new-password').value || null
    };

    try {
        const res = await apiRequest('/api/config/settings', { method: 'PUT', body: payload });
        alert(res.message);
        document.getElementById('old-password').value = '';
        document.getElementById('new-password').value = '';
    } catch (err) {
        alert(err.message);
    }
}

async function regenerateApiKey() {
    if (!confirm('Regenerate API Key? The old key will become invalid.')) return;
    try {
        const res = await apiRequest('/api/config/settings', { method: 'PUT', body: { regenerate_api_key: true } });
        if (res.new_api_key) {
            document.getElementById('new-key-display').innerHTML = `
                <div class="alert alert-success margin-top-sm">
                    New API Key: <code>${res.new_api_key}</code>
                </div>
            `;
        }
    } catch (err) {
        alert(err.message);
    }
}

// --- LOGS ---
function initLogsPage() {
    loadLogHistory();
    startLogStream();
}

async function loadLogHistory() {
    try {
        const res = await apiRequest('/api/logs/history?lines=300');
        const consoleEl = document.getElementById('log-console');
        if (!consoleEl) return;
        consoleEl.innerHTML = '';
        logHistoryCache = res.lines || [];
        filterLogs();
    } catch (err) {
        console.error("Failed loading log history:", err);
    }
}

function startLogStream() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource('/api/logs/stream');
    eventSource.onmessage = (event) => {
        if (isStreamPaused) return;
        try {
            const data = JSON.parse(event.data);
            appendLogLine(`[${data.asctime || ''}] [${data.levelname}] run=${data.run_id} file=${data.file_path} — ${data.message}`, data.levelname);
        } catch (e) {
            appendLogLine(event.data, 'INFO');
        }
    };
}

function toggleLogStream() {
    isStreamPaused = !isStreamPaused;
    const btn = document.getElementById('btn-toggle-stream');
    if (btn) {
        btn.innerHTML = isStreamPaused
            ? `${inlineIcon('play')} Resume Live Tail`
            : `${inlineIcon('pause')} Pause Live Tail`;
    }
}

function clearLogConsole() {
    const consoleEl = document.getElementById('log-console');
    if (consoleEl) consoleEl.innerHTML = '';
}

function appendLogLine(lineText, level = 'INFO') {
    const consoleEl = document.getElementById('log-console');
    if (!consoleEl) return;
    const div = document.createElement('div');
    div.className = `log-entry ${level}`;
    div.innerText = lineText;
    consoleEl.appendChild(div);
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

function filterLogs() {
    const filter = document.getElementById('log-level-filter').value;
    const consoleEl = document.getElementById('log-console');
    if (!consoleEl) return;
    consoleEl.innerHTML = '';

    logHistoryCache.forEach(line => {
        if (!filter || line.includes(`[${filter}]`)) {
            const level = line.includes('[ERROR]') ? 'ERROR' : (line.includes('[WARNING]') ? 'WARNING' : 'INFO');
            const div = document.createElement('div');
            div.className = `log-entry ${level}`;
            div.innerText = line;
            consoleEl.appendChild(div);
        }
    });
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function downloadLogHistory() {
    const res = await apiRequest('/api/logs/history?lines=1000');
    const blob = new Blob([res.lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'app.log';
    a.click();
    URL.revokeObjectURL(url);
}
