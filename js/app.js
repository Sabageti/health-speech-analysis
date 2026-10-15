// Utility
const getEl = (id) => document.getElementById(id);
const apiBase = location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';

let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = getEl('drop-zone');
    const fileInput = getEl('file-input');
    const fileInfo = getEl('file-info');
    const filenameDisplay = getEl('filename-display');
    const filesizeDisplay = getEl('filesize-display');
    const analyzeBtn = getEl('analyze-btn');
    const uploadCard = getEl('upload-card');
    const statusPanel = getEl('status-panel');
    const progressBar = getEl('progress-bar');
    const estimateDisplay = getEl('estimate-display');
    const resultsArea = getEl('results-area');
    const metricsContainer = getEl('metrics-container');
    const transcriptContent = getEl('transcript-content');

    // Drag & Drop
    if (dropZone) {
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragging');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragging');
            handleFile(e.dataTransfer.files[0]);
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    }

    // Handle file selection
    function handleFile(file) {
        if (!file) return;
        selectedFile = file;
        if (filenameDisplay) filenameDisplay.textContent = file.name;
        if (filesizeDisplay) filesizeDisplay.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
        if (fileInfo) fileInfo.style.display = 'block';
        if (dropZone) dropZone.style.display = 'none';

        // Fetch estimate
        fetch(`${apiBase}/estimate?size_bytes=${file.size}`)
            .then(res => res.json())
            .then(data => {
                if (analyzeBtn) analyzeBtn.textContent = `Start Analysis (~${data.estimated_seconds}s)`;
            }).catch(() => { });
    }

    // Start Analysis
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            if (uploadCard) uploadCard.style.display = 'none';
            if (statusPanel) statusPanel.style.display = 'block';

            // Initial estimate
            let estData = { estimated_seconds: 10 };
            try {
                const estRes = await fetch(`${apiBase}/estimate?size_bytes=${selectedFile.size}`);
                if (estRes.ok) estData = await estRes.json();
            } catch { }

            let remaining = estData.estimated_seconds;

            // Timer for estimate & progress simulation
            const timer = setInterval(() => {
                remaining = Math.max(0.1, remaining - 0.1);
                if (estimateDisplay) estimateDisplay.textContent = `Estimated time remaining: ${remaining.toFixed(1)}s`;
                if (progressBar) progressBar.style.width = `${Math.min(95, ((estData.estimated_seconds - remaining) / estData.estimated_seconds) * 100)}%`;
            }, 100);

            // Upload file
            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch(`${apiBase}/analyze`, { method: 'POST', body: formData });
                if (!response.ok) {
                    if (response.status === 404 || response.status === 405) {
                        throw new Error('Open http://127.0.0.1:8000 with the Python backend running to analyze audio.');
                    }
                    const text = await response.text();
                    throw new Error(text || 'Analysis failed');
                }

                const data = await response.json();
                clearInterval(timer);
                showResults(data);
            } catch (err) {
                clearInterval(timer);
                alert('Error: ' + (err instanceof TypeError
                    ? 'Cannot reach the analysis backend. Start it and open http://127.0.0.1:8000.'
                    : err.message));
                if (statusPanel) statusPanel.style.display = 'none';
                if (uploadCard) uploadCard.style.display = 'block';
            }
        });
    }

    // Display results safely
    function showResults(data) {
        if (!data) return;

        const metricsContainer = document.getElementById('metrics-container');
        const transcriptContent = document.getElementById('transcript-content');
        const statusPanel = document.getElementById('status-panel');
        const resultsArea = document.getElementById('results-area');
        const timeDisplay = document.getElementById('actual-time-display');

        if (!metricsContainer || !transcriptContent || !resultsArea || !timeDisplay) {
            console.error('Missing one or more DOM elements!');
            return;
        }

        if (statusPanel) statusPanel.style.display = 'none';
        resultsArea.style.display = 'block';

        timeDisplay.textContent = `Completed in ${data.processing_time_sec ?? '-'}s`;

        metricsContainer.innerHTML = '';

        const categories = [
            { key: 'acoustic', label: 'Acoustic' },
            { key: 'lexical', label: 'Lexical' }
        ];

        categories.forEach(cat => {
            const metrics = data[cat.key];
            if (metrics && typeof metrics === 'object' && Object.keys(metrics).length > 0) {
                const title = document.createElement('div');
                title.className = 'metric-category-title';
                title.textContent = cat.label;
                metricsContainer.appendChild(title);

                const grid = document.createElement('div');
                grid.className = 'metrics-grid';

                for (const [key, value] of Object.entries(metrics)) {
                    const val = (value !== null && value !== undefined) ? value : '-';
                    const card = document.createElement('div');
                    card.className = 'metric-card';
                    card.innerHTML = `
                        <div class="metric-label">${key.replace(/_/g, ' ')}</div>
                        <div class="metric-value">${val}</div>
                    `;
                    grid.appendChild(card);
                }

                metricsContainer.appendChild(grid);
            }
        });

        transcriptContent.textContent = data.transcript ?? "No speech detected.";
    }
});
