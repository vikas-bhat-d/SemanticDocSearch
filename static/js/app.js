// Global variables for dashboard and logging
let dashboardInterval = null;
let eventSource = null;
let isStreamPaused = false;
let logHistoryCache = [];

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

        document.getElementById('progress-percentage').innerText = `${data.progress_percentage || 0}%`;
        document.getElementById('progress-bar-fill').style.width = `${data.progress_percentage || 0}%`;
        document.getElementById('indexed-count').innerText = data.indexed_files || 0;
        document.getElementById('total-count').innerText = data.total_files || 0;

        document.getElementById('stat-indexed').innerText = data.indexed_files || 0;
        document.getElementById('stat-skipped').innerText = data.skipped_files || 0;
        document.getElementById('stat-failed').innerText = data.failed_files || 0;
        document.getElementById('stat-deleted').innerText = data.deleted_files || 0;

        if (data.status === 'RUNNING' || data.status === 'STOPPING') {
            if (btnStart) btnStart.disabled = true;
            if (btnStop) btnStop.disabled = (data.status === 'STOPPING');
        } else {
            if (btnStart) btnStart.disabled = false;
            if (btnStop) btnStop.disabled = true;
        }
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
                <td>${run.total_files}</td>
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
            tr.innerHTML = `
                <td>#${f.id}</td>
                <td><code>${f.path}</code></td>
                <td><span class="badge badge-idle">${f.status}</span></td>
                <td>${f.updated_at ? new Date(f.updated_at).toLocaleString() : '-'}</td>
                <td><button class="btn btn-danger" onclick="deleteFolder(${f.id})">Delete</button></td>
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

async function deleteFolder(id) {
    if (!confirm('Remove this folder from indexing?')) return;
    try {
        await apiRequest(`/api/config/folders/${id}`, { method: 'DELETE' });
        loadFolders();
    } catch (err) {
        alert(err.message);
    }
}

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
        tbody.innerHTML = '';

        list.forEach(d => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${d.id}</td>
                <td><strong>${d.name}</strong></td>
                <td><code>${d.path_patterns.join(', ')}</code></td>
                <td><button class="btn btn-danger" onclick="deleteDepartment(${d.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading departments: " + err.message);
    }
}

async function addDepartment() {
    const name = document.getElementById('dept-name').value.trim();
    const patternsRaw = document.getElementById('dept-patterns').value.trim();
    if (!name || !patternsRaw) return;

    const patterns = patternsRaw.split('\n').map(p => p.trim()).filter(Boolean);
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
        tbody.innerHTML = '';

        list.forEach(dt => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${dt.id}</td>
                <td><strong>${dt.name}</strong></td>
                <td><code>${dt.path_patterns.join(', ')}</code></td>
                <td><button class="btn btn-danger" onclick="deleteDocType(${dt.id})">Delete</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        alert("Error loading doc types: " + err.message);
    }
}

async function addDocType() {
    const name = document.getElementById('dt-name').value.trim();
    const patternsRaw = document.getElementById('dt-patterns').value.trim();
    if (!name || !patternsRaw) return;

    const patterns = patternsRaw.split('\n').map(p => p.trim()).filter(Boolean);
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
        document.getElementById('embedding-model').value = cfg.embedding_model;
        document.getElementById('embedding-dimensions').value = cfg.embedding_dimensions;
        document.getElementById('parallel-workers').value = cfg.parallel_workers;
        document.getElementById('max-file-size-mb').value = cfg.max_file_size_mb;
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
        max_file_size_mb: parseInt(document.getElementById('max-file-size-mb').value),
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
        btn.innerText = isStreamPaused ? '▶ Resume Live Tail' : '⏸️ Pause Live Tail';
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
