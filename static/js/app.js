/**
 * Versor - Main Application JavaScript
 */

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const convertBtn = document.getElementById('convertBtn');
const resultsDiv = document.getElementById('results');
const loading = document.getElementById('loading');

// State
let selectedFiles = [];
let currentMethod = 'potrace';
let currentPresets = {
    potrace: 'cnc_precise',
    centerline: 'line_art',
    vtracer: 'smooth_color'
};

// Initialize sliders for each method
function initSliders() {
    // Potrace sliders
    setupSlider('cornerThreshold', 'cornerValue');
    setupSlider('optimizeTolerance', 'optimizeValue');
    setupSlider('despeckle', 'despeckleValue');
    setupSlider('threshold', 'thresholdValue');

    // Centerline sliders
    setupSlider('cl-despeckleLevel', 'cl-despeckleValue');
    setupSlider('cl-cornerThreshold', 'cl-cornerValue');
    setupSlider('cl-lineThreshold', 'cl-lineValue');
    setupSlider('cl-threshold', 'cl-thresholdValue');

    // vtracer sliders
    setupSlider('vt-colorPrecision', 'vt-colorValue');
    setupSlider('vt-gradientStep', 'vt-gradientValue');
    setupSlider('vt-corner', 'vt-cornerValue');
    setupSlider('vt-segment', 'vt-segmentValue');
    setupSlider('vt-splice', 'vt-spliceValue');
    setupSlider('vt-filterSpeckle', 'vt-filterValue');
}

function setupSlider(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const valueSpan = document.getElementById(valueId);
    if (slider && valueSpan) {
        slider.addEventListener('input', () => {
            valueSpan.textContent = slider.value;
        });
    }
}

// Drop zone events
function initDropZone() {
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });
}

function handleFiles(files) {
    for (const file of files) {
        if (!selectedFiles.find(f => f.name === file.name)) {
            selectedFiles.push(file);
        }
    }
    renderFileList();
    updateConvertButton();
}

function renderFileList() {
    // Clear existing items
    fileList.textContent = '';

    selectedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'name';
        nameSpan.textContent = file.name;

        const sizeSpan = document.createElement('span');
        sizeSpan.className = 'size';
        sizeSpan.textContent = formatSize(file.size);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove';
        removeBtn.textContent = 'x';
        removeBtn.addEventListener('click', () => removeFile(index));

        item.appendChild(nameSpan);
        item.appendChild(sizeSpan);
        item.appendChild(removeBtn);
        fileList.appendChild(item);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
    updateConvertButton();
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function updateConvertButton() {
    convertBtn.disabled = selectedFiles.length === 0;
}

// Tab switching
function initTabs() {
    const tabContainer = document.querySelector('.tab-container');
    if (!tabContainer) return;

    tabContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.tab-btn');
        if (!btn || btn.disabled) return;

        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update tab content
        const method = btn.dataset.method;
        currentMethod = method;
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`tab-${method}`).classList.add('active');
    });
}

// Preset selection (per-method)
function initPresetSelection() {
    document.querySelectorAll('.tab-content').forEach(tabContent => {
        const presetGrid = tabContent.querySelector('.preset-grid');
        if (!presetGrid) return;

        presetGrid.addEventListener('click', (e) => {
            const btn = e.target.closest('.preset-btn');
            if (!btn) return;

            const method = btn.dataset.method;

            // Update active state within this tab only
            tabContent.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            currentPresets[method] = btn.dataset.preset;

            // Show/hide custom settings
            const customPanel = document.getElementById(`customSettings-${method}`);
            if (btn.dataset.preset === 'custom') {
                customPanel.classList.add('visible');
            } else {
                customPanel.classList.remove('visible');
                // Update slider values from preset data attributes
                updateSlidersFromPreset(method, btn);
            }
        });
    });
}

function updateSlidersFromPreset(method, btn) {
    if (method === 'potrace') {
        setSliderValue('cornerThreshold', 'cornerValue', btn.dataset.corner);
        setSliderValue('optimizeTolerance', 'optimizeValue', btn.dataset.optimize);
        setSliderValue('despeckle', 'despeckleValue', btn.dataset.despeckle);
        setSliderValue('threshold', 'thresholdValue', btn.dataset.threshold);
    } else if (method === 'centerline') {
        setSliderValue('cl-despeckleLevel', 'cl-despeckleValue', btn.dataset.despeckleLevel);
        setSliderValue('cl-cornerThreshold', 'cl-cornerValue', btn.dataset.corner);
        setSliderValue('cl-lineThreshold', 'cl-lineValue', btn.dataset.lineThreshold);
        setSliderValue('cl-threshold', 'cl-thresholdValue', btn.dataset.threshold);
    } else if (method === 'vtracer') {
        const modeSelect = document.getElementById('vt-mode');
        if (modeSelect) modeSelect.value = btn.dataset.mode;
        setSliderValue('vt-colorPrecision', 'vt-colorValue', btn.dataset.colorPrecision);
        setSliderValue('vt-gradientStep', 'vt-gradientValue', btn.dataset.gradientStep);
        setSliderValue('vt-corner', 'vt-cornerValue', btn.dataset.corner);
        setSliderValue('vt-segment', 'vt-segmentValue', btn.dataset.segment);
        setSliderValue('vt-splice', 'vt-spliceValue', btn.dataset.splice);
        setSliderValue('vt-filterSpeckle', 'vt-filterValue', btn.dataset.filterSpeckle);
    }
}

function setSliderValue(sliderId, valueId, value) {
    const slider = document.getElementById(sliderId);
    const valueSpan = document.getElementById(valueId);
    if (slider && value !== undefined) {
        slider.value = value;
        if (valueSpan) valueSpan.textContent = value;
    }
}

// Form submission
function initConvertButton() {
    convertBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        loading.classList.add('visible');
        resultsDiv.textContent = '';

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        formData.append('method', currentMethod);
        formData.append('preset', currentPresets[currentMethod]);

        // Add method-specific custom parameters
        if (currentPresets[currentMethod] === 'custom') {
            appendCustomParams(formData, currentMethod);
        }

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.error) {
                showError(data.error);
            } else {
                renderResults(data.results);
            }
        } catch (error) {
            showError('Error: ' + error.message);
        } finally {
            loading.classList.remove('visible');
        }
    });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-banner';
    errorDiv.textContent = message;
    resultsDiv.appendChild(errorDiv);
}

function appendCustomParams(formData, method) {
    if (method === 'potrace') {
        formData.append('corner_threshold', document.getElementById('cornerThreshold').value);
        formData.append('optimize_tolerance', document.getElementById('optimizeTolerance').value);
        formData.append('despeckle', document.getElementById('despeckle').value);
        formData.append('threshold', document.getElementById('threshold').value);
        formData.append('invert', document.getElementById('invert').checked);
    } else if (method === 'centerline') {
        formData.append('despeckle_level', document.getElementById('cl-despeckleLevel').value);
        formData.append('cl_corner_threshold', document.getElementById('cl-cornerThreshold').value);
        formData.append('line_threshold', document.getElementById('cl-lineThreshold').value);
        formData.append('threshold', document.getElementById('cl-threshold').value);
        formData.append('invert', document.getElementById('cl-invert').checked);
    } else if (method === 'vtracer') {
        formData.append('mode', document.getElementById('vt-mode').value);
        formData.append('color_precision', document.getElementById('vt-colorPrecision').value);
        formData.append('gradient_step', document.getElementById('vt-gradientStep').value);
        formData.append('vt_corner_threshold', document.getElementById('vt-corner').value);
        formData.append('segment_length', document.getElementById('vt-segment').value);
        formData.append('splice_threshold', document.getElementById('vt-splice').value);
        formData.append('filter_speckle', document.getElementById('vt-filterSpeckle').value);
    }
}

function normalizeSvgForPreview(svg) {
    // Ensure SVG displays properly by setting viewBox if missing
    // and removing fixed dimensions that prevent scaling

    let viewBox = svg.getAttribute('viewBox');
    const width = svg.getAttribute('width');
    const height = svg.getAttribute('height');

    // If no viewBox but has width/height, create viewBox from those
    if (!viewBox && width && height) {
        // Parse width/height, removing any units
        const w = parseFloat(width);
        const h = parseFloat(height);
        if (!isNaN(w) && !isNaN(h) && w > 0 && h > 0) {
            svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
        }
    }

    // If still no viewBox, try to calculate from bounding box after insertion
    // This is a fallback - we set a reasonable default
    if (!svg.getAttribute('viewBox')) {
        // Default viewBox for SVGs without dimensions
        svg.setAttribute('viewBox', '0 0 100 100');
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    }

    // Remove fixed width/height to let CSS handle sizing
    svg.removeAttribute('width');
    svg.removeAttribute('height');

    // Ensure aspect ratio is preserved
    if (!svg.getAttribute('preserveAspectRatio')) {
        svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    }
}

function renderResults(results) {
    resultsDiv.textContent = '';

    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'result-item';

        // Header
        const header = document.createElement('div');
        header.className = 'result-header';

        const filename = document.createElement('span');
        filename.className = 'filename';
        filename.textContent = result.output_filename;

        const status = document.createElement('span');
        status.className = 'status ' + (result.success ? 'success' : 'error');
        status.textContent = result.success ? 'Success' : 'Failed';

        header.appendChild(filename);
        header.appendChild(status);
        item.appendChild(header);

        if (result.success) {
            // Before/After comparison container
            const comparison = document.createElement('div');
            comparison.className = 'result-comparison';

            // Original (Before) panel
            const beforePanel = document.createElement('div');
            beforePanel.className = 'comparison-panel';

            const beforeLabel = document.createElement('div');
            beforeLabel.className = 'comparison-label';
            beforeLabel.textContent = 'Original';

            const beforeContent = document.createElement('div');
            beforeContent.className = 'comparison-content';

            if (result.original_preview) {
                const originalImg = document.createElement('img');
                originalImg.src = result.original_preview;
                originalImg.alt = 'Original image';
                beforeContent.appendChild(originalImg);
            } else {
                const noOriginal = document.createElement('p');
                noOriginal.textContent = 'Original not available';
                noOriginal.style.color = '#999';
                beforeContent.appendChild(noOriginal);
            }

            beforePanel.appendChild(beforeLabel);
            beforePanel.appendChild(beforeContent);

            // Converted (After) panel
            const afterPanel = document.createElement('div');
            afterPanel.className = 'comparison-panel';

            const afterLabel = document.createElement('div');
            afterLabel.className = 'comparison-label';
            afterLabel.textContent = 'Converted';

            const afterContent = document.createElement('div');
            afterContent.className = 'comparison-content';

            if (result.svg_content) {
                // Parse SVG safely - only allow SVG elements from our backend
                const parser = new DOMParser();
                const svgDoc = parser.parseFromString(result.svg_content, 'image/svg+xml');
                const svgElement = svgDoc.documentElement;

                // Check if parsing was successful (no parsererror)
                if (svgElement && svgElement.nodeName === 'svg') {
                    const importedSvg = document.importNode(svgElement, true);

                    // Normalize SVG for consistent preview display
                    normalizeSvgForPreview(importedSvg);

                    afterContent.appendChild(importedSvg);
                } else {
                    const noPreview = document.createElement('p');
                    noPreview.textContent = 'Preview not available';
                    noPreview.style.color = '#999';
                    afterContent.appendChild(noPreview);
                }
            } else {
                const noPreview = document.createElement('p');
                noPreview.textContent = result.preview_unavailable_reason || 'Preview not available';
                noPreview.style.color = '#999';
                afterContent.appendChild(noPreview);
            }

            afterPanel.appendChild(afterLabel);
            afterPanel.appendChild(afterContent);

            comparison.appendChild(beforePanel);
            comparison.appendChild(afterPanel);
            item.appendChild(comparison);

            // Action buttons
            const actions = document.createElement('div');
            actions.className = 'result-actions';

            const downloadLink = document.createElement('a');
            downloadLink.href = result.download_url;
            downloadLink.className = 'btn-download';
            downloadLink.download = '';
            downloadLink.textContent = 'Download SVG';

            const previewLink = document.createElement('a');
            previewLink.href = '/preview/' + encodeURIComponent(result.output_filename);
            previewLink.className = 'btn-preview';
            previewLink.target = '_blank';
            previewLink.textContent = 'Open in Tab';

            actions.appendChild(downloadLink);
            actions.appendChild(previewLink);
            item.appendChild(actions);
        } else {
            const errorMsg = document.createElement('p');
            errorMsg.style.color = '#e74c3c';
            errorMsg.textContent = result.message;
            item.appendChild(errorMsg);
        }

        resultsDiv.appendChild(item);
    });
}

// Initialize everything on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initSliders();
    initDropZone();
    initTabs();
    initPresetSelection();
    initConvertButton();
});
