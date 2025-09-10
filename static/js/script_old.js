// KyndVibes Command Center JavaScript

class CommandCenter {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.setupUploadArea();
        this.checkSystemHealth();
    }

    setupEventListeners() {
        // Calendar period selector
        const periodSelector = document.getElementById('calendar-period');
        if (periodSelector) {
            periodSelector.addEventListener('change', (e) => {
                this.loadCalendarData(e.target.value);
            });
        }

        // File input change
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files);
            });
        }
    }

    setupUploadArea() {
        const uploadArea = document.getElementById('upload-area');
        if (!uploadArea) return;

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFileUpload(files);
        });

        // Click to upload
        uploadArea.addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
    }

    async loadInitialData() {
        await Promise.all([
            this.loadCalendarData('7day'),
            this.loadAssets(),
            this.loadDeliverables()
        ]);
    }

    async loadCalendarData(period = '7day') {
        const container = document.getElementById('calendar-content');
        if (!container) return;

        try {
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch(`/api/calendar/${period}`);
            const data = await response.json();

            if (response.ok) {
                container.innerHTML = this.renderCalendarEvents(data.events);
            } else {
                container.innerHTML = this.getErrorHTML(data.error || 'Failed to load calendar');
            }
        } catch (error) {
            container.innerHTML = this.getErrorHTML('Network error loading calendar');
            console.error('Calendar load error:', error);
        }
    }

    async loadAssets() {
        const container = document.getElementById('assets-content');
        if (!container) return;

        try {
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch('/api/assets');
            const data = await response.json();

            if (response.ok) {
                container.innerHTML = this.renderAssets(data.assets);
            } else {
                container.innerHTML = this.getErrorHTML(data.error || 'Failed to load assets');
            }
        } catch (error) {
            container.innerHTML = this.getErrorHTML('Network error loading assets');
            console.error('Assets load error:', error);
        }
    }

    async loadDeliverables() {
        const container = document.getElementById('deliverables-content');
        if (!container) return;

        try {
            container.innerHTML = this.getLoadingHTML();
            
            const response = await fetch('/api/deliverables');
            const data = await response.json();

            if (response.ok) {
                container.innerHTML = this.renderDeliverables(data.deliverables);
            } else {
                container.innerHTML = this.getErrorHTML(data.error || 'Failed to load deliverables');
            }
        } catch (error) {
            container.innerHTML = this.getErrorHTML('Network error loading deliverables');
            console.error('Deliverables load error:', error);
        }
    }

    async handleFileUpload(files) {
        if (!files || files.length === 0) return;

        const progressContainer = document.getElementById('upload-progress');
        const resultsContainer = document.getElementById('upload-results');
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');

        progressContainer.classList.remove('hidden');
        resultsContainer.innerHTML = '';

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);

            try {
                progressText.textContent = `Uploading ${file.name}...`;
                progressFill.style.width = `${((i + 0.5) / files.length) * 100}%`;

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    this.showUploadResult(file.name, 'success', 'Upload successful');
                    this.showToast(`${file.name} uploaded successfully`, 'success');
                } else {
                    this.showUploadResult(file.name, 'error', result.error || 'Upload failed');
                    this.showToast(`Failed to upload ${file.name}`, 'error');
                }

                progressFill.style.width = `${((i + 1) / files.length) * 100}%`;
            } catch (error) {
                this.showUploadResult(file.name, 'error', 'Network error');
                this.showToast(`Network error uploading ${file.name}`, 'error');
                console.error('Upload error:', error);
            }
        }

        progressText.textContent = 'Upload complete';
        setTimeout(() => {
            progressContainer.classList.add('hidden');
            progressFill.style.width = '0%';
        }, 2000);

        // Refresh assets after upload
        this.loadAssets();
    }

    async checkSystemHealth() {
        const statusElement = document.getElementById('api-status');
        const lastUpdatedElement = document.getElementById('last-updated');

        try {
            const response = await fetch('/healthz');
            const data = await response.json();

            if (response.ok && data.ok) {
                statusElement.textContent = 'Healthy ✅';
                statusElement.style.color = 'var(--lime-green)';
                lastUpdatedElement.textContent = new Date(data.time).toLocaleString();
            } else {
                statusElement.textContent = 'Unhealthy ❌';
                statusElement.style.color = 'var(--bright-pink)';
            }
        } catch (error) {
            statusElement.textContent = 'Error ❌';
            statusElement.style.color = 'var(--bright-pink)';
            console.error('Health check error:', error);
        }
    }

    renderCalendarEvents(events) {
        if (!events || events.length === 0) {
            return '<p class="text-center" style="color: var(--warm-gray);">No events found for this period.</p>';
        }

        return events.map(event => `
            <div class="event-item">
                <div class="event-header">
                    <div class="event-title">${this.escapeHtml(event.title)}</div>
                    <div class="event-meta">
                        <span class="event-date">📅 ${this.formatDate(event.date)}</span>
                        <span class="event-type">${this.escapeHtml(event.type)}</span>
                    </div>
                </div>
                ${event.description ? `<div class="event-description">${this.escapeHtml(event.description)}</div>` : ''}
            </div>
        `).join('');
    }

    renderAssets(assets) {
        if (!assets || assets.length === 0) {
            return '<p class="text-center" style="color: var(--warm-gray);">No assets found.</p>';
        }

        return assets.map(asset => `
            <div class="asset-item clickable" onclick="window.open('${asset.url}', '_blank')">
                <div class="asset-header">
                    <div class="asset-name">${this.escapeHtml(asset.name)}</div>
                    <div class="asset-actions">
                        <button class="btn-icon" onclick="event.stopPropagation(); window.open('${asset.url}', '_blank')" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" onclick="event.stopPropagation(); this.downloadAsset('${asset.url}', '${asset.name}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
                <div class="asset-meta">
                    <span class="asset-type">🎨 ${this.escapeHtml(asset.type)}</span>
                    <span class="asset-date">${this.formatDate(asset.created_date)}</span>
                    <span class="asset-size">${asset.file_size || 'Unknown size'}</span>
                    ${asset.is_uploaded ? '<span class="uploaded-badge">Uploaded</span>' : ''}
                </div>
            </div>
        `).join('');
    }

    renderDeliverables(deliverables) {
        if (!deliverables || deliverables.length === 0) {
            return '<p class="text-center" style="color: var(--warm-gray);">No deliverables found.</p>';
        }

        return deliverables.map(deliverable => `
            <div class="deliverable-item">
                <div class="deliverable-title">${this.escapeHtml(deliverable.title)}</div>
                <div class="deliverable-status">
                    <span class="status-badge status-${deliverable.status.replace('_', '-')}">${deliverable.status}</span>
                    📅 Due: ${this.formatDate(deliverable.due_date)}
                </div>
                ${deliverable.description ? `<div class="deliverable-description">${this.escapeHtml(deliverable.description)}</div>` : ''}
            </div>
        `).join('');
    }

    showUploadResult(filename, type, message) {
        const container = document.getElementById('upload-results');
        const resultDiv = document.createElement('div');
        resultDiv.className = `upload-result ${type}`;
        resultDiv.innerHTML = `
            <strong>${this.escapeHtml(filename)}</strong>: ${this.escapeHtml(message)}
        `;
        container.appendChild(resultDiv);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getLoadingHTML() {
        return `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Loading...</p>
            </div>
        `;
    }

    getErrorHTML(message) {
        return `
            <div class="text-center" style="color: var(--bright-pink);">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p><strong>Error:</strong> ${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Quick Action Functions
function refreshAssets() {
    commandCenter.loadAssets();
    commandCenter.showToast('Assets refreshed', 'success');
}

function refreshDeliverables() {
    commandCenter.loadDeliverables();
    commandCenter.showToast('Deliverables refreshed', 'success');
}

function checkHealth() {
    commandCenter.checkSystemHealth();
    commandCenter.showToast('Health check performed', 'info');
}

function exportData() {
    commandCenter.showToast('Export functionality coming soon', 'info');
}

function viewBrandGuide() {
    window.open('/static/assets/brand-guide.pdf', '_blank');
}

function openFrequencyCollective() {
    commandCenter.showToast('Opening Frequency Collective portal...', 'info');
    // Add actual URL when available
}

// Initialize the command center when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.commandCenter = new CommandCenter();
});

// Add some energy to the page with subtle animations
document.addEventListener('DOMContentLoaded', () => {
    // Animate energy rays
    const rays = document.querySelectorAll('.ray');
    rays.forEach((ray, index) => {
        ray.style.animationDelay = `${index * 0.1}s`;
        ray.style.animation = 'pulse 2s ease-in-out infinite';
    });

    // Add pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});

