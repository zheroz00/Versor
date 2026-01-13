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
let currentFormat = 'svg';
let currentPresets = {
    potrace: 'cnc_precise',
    centerline: 'line_art',
    vtracer: 'smooth_color'
};

// Track what settings were used for the last conversion
let lastConversion = {
    method: null,
    preset: null,
    format: null,
    customHash: null,  // Hash of custom settings to detect changes
    hasResults: false
};

// Generate a hash of current custom settings to detect changes
function getCustomSettingsHash(method) {
    const values = [];
    if (method === 'potrace') {
        values.push(document.getElementById('cornerThreshold')?.value);
        values.push(document.getElementById('optimizeTolerance')?.value);
        values.push(document.getElementById('despeckle')?.value);
        values.push(document.getElementById('threshold')?.value);
        values.push(document.getElementById('invert')?.checked);
        values.push(document.getElementById('straighten')?.checked);
        values.push(document.getElementById('straightenTolerance')?.value);
        values.push(document.getElementById('simplify')?.checked);
        values.push(document.getElementById('simplifyTolerance')?.value);
    } else if (method === 'centerline') {
        values.push(document.getElementById('cl-despeckleLevel')?.value);
        values.push(document.getElementById('cl-cornerThreshold')?.value);
        values.push(document.getElementById('cl-lineThreshold')?.value);
        values.push(document.getElementById('cl-threshold')?.value);
        values.push(document.getElementById('cl-invert')?.checked);
    } else if (method === 'vtracer') {
        values.push(document.getElementById('vt-mode')?.value);
        values.push(document.getElementById('vt-colorPrecision')?.value);
        values.push(document.getElementById('vt-gradientStep')?.value);
        values.push(document.getElementById('vt-corner')?.value);
        values.push(document.getElementById('vt-segment')?.value);
        values.push(document.getElementById('vt-splice')?.value);
        values.push(document.getElementById('vt-filterSpeckle')?.value);
    }
    return values.join('|');
}

// Check if current settings differ from last conversion and update indicator
function updateStaleIndicator() {
    const indicator = document.getElementById('staleIndicator');
    if (!indicator) return;

    const currentCustomHash = currentPresets[currentMethod] === 'custom'
        ? getCustomSettingsHash(currentMethod)
        : null;

    const settingsChanged = lastConversion.hasResults &&
        (lastConversion.method !== currentMethod ||
         lastConversion.preset !== currentPresets[currentMethod] ||
         lastConversion.format !== currentFormat ||
         (currentPresets[currentMethod] === 'custom' && lastConversion.customHash !== currentCustomHash));

    if (settingsChanged) {
        indicator.classList.add('visible');
        resultsDiv.classList.add('stale');
    } else {
        indicator.classList.remove('visible');
        resultsDiv.classList.remove('stale');
    }
}

// Initialize sliders for each method
function initSliders() {
    // Potrace sliders
    setupSlider('cornerThreshold', 'cornerValue');
    setupSlider('optimizeTolerance', 'optimizeValue');
    setupSlider('despeckle', 'despeckleValue');
    setupSlider('threshold', 'thresholdValue');
    setupSlider('simplifyTolerance', 'simplifyValue');
    setupSlider('straightenTolerance', 'straightenValue');

    // Setup straighten checkbox to show/hide tolerance slider
    const straightenCheckbox = document.getElementById('straighten');
    const straightenSettings = document.getElementById('straightenSettings');
    if (straightenCheckbox && straightenSettings) {
        straightenCheckbox.addEventListener('change', () => {
            if (straightenCheckbox.checked) {
                straightenSettings.classList.add('visible');
            } else {
                straightenSettings.classList.remove('visible');
            }
            updateStaleIndicator();
        });
    }

    // Setup simplify checkbox to show/hide tolerance slider
    const simplifyCheckbox = document.getElementById('simplify');
    const simplifySettings = document.getElementById('simplifySettings');
    if (simplifyCheckbox && simplifySettings) {
        simplifyCheckbox.addEventListener('change', () => {
            if (simplifyCheckbox.checked) {
                simplifySettings.classList.add('visible');
            } else {
                simplifySettings.classList.remove('visible');
            }
            updateStaleIndicator();
        });
    }

    // Setup invert checkbox change detection
    const invertCheckbox = document.getElementById('invert');
    if (invertCheckbox) {
        invertCheckbox.addEventListener('change', updateStaleIndicator);
    }
    const clInvertCheckbox = document.getElementById('cl-invert');
    if (clInvertCheckbox) {
        clInvertCheckbox.addEventListener('change', updateStaleIndicator);
    }

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

    // vtracer mode dropdown change detection
    const vtMode = document.getElementById('vt-mode');
    if (vtMode) {
        vtMode.addEventListener('change', updateStaleIndicator);
    }
}

// Initialize format selector
function initFormatSelector() {
    const formatButtons = document.getElementById('formatButtons');
    const formatNote = document.getElementById('formatNote');
    if (!formatButtons) return;

    formatButtons.addEventListener('click', (e) => {
        const btn = e.target.closest('.format-btn');
        if (!btn) return;

        // Update active state
        formatButtons.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        currentFormat = btn.dataset.format;
        updateStaleIndicator();
        updateFormatNote();
    });

    updateFormatNote();
}

function updateFormatNote() {
    const formatNote = document.getElementById('formatNote');
    if (!formatNote) return;

    // vtracer only supports SVG
    if (currentMethod === 'vtracer' && currentFormat !== 'svg') {
        formatNote.textContent = 'Note: vtracer only supports SVG output';
        formatNote.style.display = 'block';
    } else if (currentFormat !== 'svg') {
        formatNote.textContent = 'Note: Preview only available for SVG format';
        formatNote.style.display = 'block';
    } else {
        formatNote.textContent = '';
        formatNote.style.display = 'none';
    }
}

function setupSlider(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const valueSpan = document.getElementById(valueId);
    if (slider && valueSpan) {
        slider.addEventListener('input', () => {
            valueSpan.textContent = slider.value;
            updateStaleIndicator();
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

        // Check if results are now stale
        updateStaleIndicator();
        // Update format note (vtracer only supports SVG)
        updateFormatNote();
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

            // Check if results are now stale
            updateStaleIndicator();

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
        formData.append('output_format', currentFormat);

        // Add method-specific custom parameters
        if (currentPresets[currentMethod] === 'custom') {
            appendCustomParams(formData, currentMethod);
        }

        // Always send post-processing options for potrace (available for all presets)
        if (currentMethod === 'potrace') {
            appendPotracePostProcessParams(formData);
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
                // Track what settings were used for this conversion
                lastConversion.method = currentMethod;
                lastConversion.preset = currentPresets[currentMethod];
                lastConversion.format = currentFormat;
                lastConversion.customHash = currentPresets[currentMethod] === 'custom'
                    ? getCustomSettingsHash(currentMethod)
                    : null;
                lastConversion.hasResults = true;
                updateStaleIndicator();
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

function appendPotracePostProcessParams(formData) {
    // Post-processing options are available for all potrace presets
    formData.append('invert', document.getElementById('invert').checked);
    formData.append('straighten', document.getElementById('straighten').checked);
    formData.append('straighten_tolerance', document.getElementById('straightenTolerance').value);
    formData.append('simplify', document.getElementById('simplify').checked);
    formData.append('simplify_tolerance', document.getElementById('simplifyTolerance').value);
}

function appendCustomParams(formData, method) {
    if (method === 'potrace') {
        formData.append('corner_threshold', document.getElementById('cornerThreshold').value);
        formData.append('optimize_tolerance', document.getElementById('optimizeTolerance').value);
        formData.append('despeckle', document.getElementById('despeckle').value);
        formData.append('threshold', document.getElementById('threshold').value);
        // Note: post-processing params are added separately by appendPotracePostProcessParams
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

            if (result.preview_url) {
                const convertedImg = document.createElement('img');
                // Add cache-busting timestamp to prevent browser caching old results
                convertedImg.src = result.preview_url + '?t=' + Date.now();
                convertedImg.alt = 'Converted SVG';
                afterContent.appendChild(convertedImg);
            } else {
                const noPreview = document.createElement('div');
                noPreview.className = 'no-preview-msg';
                const formatUpper = (result.output_format || 'svg').toUpperCase();
                const badge = document.createElement('span');
                badge.className = 'format-badge';
                badge.textContent = formatUpper;
                const msg = document.createElement('p');
                msg.textContent = `Preview not available for ${formatUpper} format`;
                noPreview.appendChild(badge);
                noPreview.appendChild(msg);
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
            const formatUpper = (result.output_format || 'svg').toUpperCase();
            downloadLink.textContent = `Download ${formatUpper}`;

            actions.appendChild(downloadLink);

            // Only show "Open in Tab" for SVG
            if (result.preview_url) {
                const previewLink = document.createElement('a');
                previewLink.href = '/preview/' + encodeURIComponent(result.output_filename);
                previewLink.className = 'btn-preview';
                previewLink.target = '_blank';
                previewLink.textContent = 'Open in Tab';
                actions.appendChild(previewLink);
            }

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
    initFormatSelector();
    initConvertButton();
});
