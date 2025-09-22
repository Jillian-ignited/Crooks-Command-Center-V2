// Enhanced Collaborative Crooks & Castles Command Center JavaScript
class CrooksCommandCenter {
    constructor() {
        this.currentTab = 'dashboard';
        this.intelligenceData = {};
        this.culturalData = {};
        this.competitiveRankings = {};
        this.fileLibrary = [];
        this.projects = [];
        this.assets = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDropzones();
        this.loadInitialData();
        this.setupCharts();
        this.startDataRefreshInterval();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.showTab(tab);
            });
        });

        // Upload tabs
        document.querySelectorAll('.upload-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchUploadTab(e.currentTarget.dataset.type);
            });
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.applyFilter(e.currentTarget);
            });
        });

        // Modal close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    setupDropzones() {
        // Intelligence Data Dropzone
        if (document.getElementById('intelligence-dropzone')) {
            this.intelligenceDropzone = new Dropzone('#intelligence-dropzone', {
                url: '/api/upload_intelligence',
                paramName: 'file',
                maxFilesize: 16, // MB
                acceptedFiles: '.jsonl,.json,.csv',
                addRemoveLinks: true,
                dictDefaultMessage: `
                    <i class="fas fa-cloud-upload-alt"></i>
                    <h4>Drop JSONL files here or click to upload</h4>
                    <p>Upload your Apify intelligence data for processing</p>
                `,
                init: function() {
                    this.on('sending', function(file, xhr, formData) {
                        const activeTab = document.querySelector('.upload-tab.active');
                        const dataType = activeTab ? activeTab.dataset.type : 'instagram';
                        formData.append('data_type', dataType);
                    });

                    this.on('success', function(file, response) {
                        commandCenter.showNotification('success', 'Upload Successful', 
                            `${response.records_processed} records processed successfully`);
                        commandCenter.refreshIntelligenceData();
                    });

                    this.on('error', function(file, errorMessage) {
                        commandCenter.showNotification('error', 'Upload Failed', 
                            typeof errorMessage === 'string' ? errorMessage : 'Upload failed');
                    });
                }
            });
        }

        // Asset Dropzone
        if (document.getElementById('asset-dropzone')) {
            this.assetDropzone = new Dropzone('#asset-dropzone', {
                url: '/api/assets',
                paramName: 'file',
                maxFilesize: 50, // MB
                acceptedFiles: 'image/*,video/*,.pdf,.doc,.docx,.ai,.psd,.sketch,.fig',
                addRemoveLinks: true,
                dictDefaultMessage: `
                    <i class="fas fa-images"></i>
                    <h4>Drop assets here or click to upload</h4>
                    <p>Upload images, videos, documents, and design files</p>
                `,
                init: function() {
                    this.on('sending', function(file, xhr, formData) {
                        const category = document.getElementById('asset-category').value;
                        formData.append('category', category);
                        formData.append('name', file.name);
                        formData.append('created_by', 'current_user');
                    });

                    this.on('success', function(file, response) {
                        commandCenter.showNotification('success', 'Asset Uploaded', 
                            'Asset uploaded successfully and added to library');
                        commandCenter.refreshAssets();
                    });

                    this.on('error', function(file, errorMessage) {
                        commandCenter.showNotification('error', 'Upload Failed', 
                            typeof errorMessage === 'string' ? errorMessage : 'Asset upload failed');
                    });
                }
            });
        }

        // Document Dropzone
        if (document.getElementById('document-dropzone')) {
            this.documentDropzone = new Dropzone('#document-dropzone', {
                url: '/api/documents',
                paramName: 'file',
                maxFilesize: 25, // MB
                acceptedFiles: '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt',
                addRemoveLinks: true,
                dictDefaultMessage: `
                    <i class="fas fa-file-alt"></i>
                    <h4>Drop documents here or click to upload</h4>
                    <p>Upload reports, presentations, and planning documents</p>
                `,
                init: function() {
                    this.on('success', function(file, response) {
                        commandCenter.showNotification('success', 'Document Uploaded', 
                            'Document uploaded successfully');
                        commandCenter.refreshFileLibrary();
                    });

                    this.on('error', function(file, errorMessage) {
                        commandCenter.showNotification('error', 'Upload Failed', 
                            typeof errorMessage === 'string' ? errorMessage : 'Document upload failed');
                    });
                }
            });
        }
    }

    showTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    loadTabData(tabName) {
        switch(tabName) {
            case 'intelligence':
                this.loadIntelligenceData();
                break;
            case 'cultural-radar':
                this.loadCulturalRadarData();
                break;
            case 'projects':
                this.loadProjectsData();
                break;
            case 'assets':
                this.loadAssetsData();
                break;
            case 'calendar':
                this.loadCalendarData();
                break;
            case 'file-manager':
                this.loadFileLibrary();
                break;
            case 'reports':
                this.loadReportsData();
                break;
        }
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/intelligence/summary');
            const data = await response.json();
            
            this.intelligenceData = data.summary;
            this.culturalData = data.cultural_radar;
            this.competitiveRankings = data.competitive_rankings;
            
            this.updateDashboardMetrics();
            this.updateIntelligenceDisplay();
            this.updateCulturalRadarDisplay();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('error', 'Data Load Error', 'Failed to load intelligence data');
        }
    }

    async refreshIntelligenceData() {
        try {
            const response = await fetch('/api/intelligence/summary');
            const data = await response.json();
            
            this.intelligenceData = data.summary;
            this.competitiveRankings = data.competitive_rankings;
            
            this.updateDashboardMetrics();
            this.updateIntelligenceDisplay();
            
            this.showNotification('success', 'Data Refreshed', 'Intelligence data updated successfully');
            
        } catch (error) {
            console.error('Error refreshing intelligence data:', error);
            this.showNotification('error', 'Refresh Failed', 'Failed to refresh intelligence data');
        }
    }

    updateDashboardMetrics() {
        // Update competitive rank
        const rankElement = document.querySelector('.metric-card.competitive .metric-value');
        if (rankElement && this.intelligenceData.crooks_rank) {
            rankElement.innerHTML = `#${this.intelligenceData.crooks_rank}<span>/${this.intelligenceData.total_brands}</span>`;
        }

        // Update cultural trends count
        const trendsElement = document.querySelector('.metric-card.cultural .metric-value');
        if (trendsElement && this.culturalData.trending_hashtags) {
            trendsElement.innerHTML = `${this.culturalData.trending_hashtags.length}<span> trending</span>`;
        }

        // Update intelligence data count
        const dataElement = document.querySelector('.metric-card.intelligence .metric-value');
        if (dataElement && this.intelligenceData.data_sources) {
            const total = Object.values(this.intelligenceData.data_sources).reduce((a, b) => a + b, 0);
            dataElement.innerHTML = `${total}<span> records</span>`;
        }
    }

    updateIntelligenceDisplay() {
        const rankingsBody = document.getElementById('rankings-body');
        if (!rankingsBody || !this.competitiveRankings) return;

        rankingsBody.innerHTML = '';

        // Sort brands by rank
        const sortedBrands = Object.entries(this.competitiveRankings)
            .sort(([,a], [,b]) => a.rank - b.rank);

        sortedBrands.forEach(([brand, data]) => {
            const row = document.createElement('div');
            row.className = 'ranking-row';
            
            const rankClass = data.rank <= 4 ? 'top' : data.rank <= 8 ? 'middle' : 'bottom';
            const performanceClass = data.performance_tier || 'medium';
            const isCrooks = brand === 'Crooks & Castles';
            
            row.innerHTML = `
                <div class="rank-col">
                    <div class="rank-badge ${rankClass}">${data.rank}</div>
                </div>
                <div class="brand-col">
                    <div class="brand-name ${isCrooks ? 'crooks' : ''}">${brand}</div>
                </div>
                <div class="posts-col">${data.metrics?.total_posts || 0}</div>
                <div class="engagement-col">${data.metrics?.avg_engagement || 0}</div>
                <div class="performance-col">
                    <div class="performance-indicator ${performanceClass}">${performanceClass}</div>
                </div>
                <div class="actions-col">
                    <button class="btn btn-secondary btn-sm" onclick="commandCenter.viewBrandDetails('${brand}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
            `;
            
            rankingsBody.appendChild(row);
        });
    }

    updateCulturalRadarDisplay() {
        // Update trending hashtags
        const hashtagsContainer = document.getElementById('trending-hashtags');
        if (hashtagsContainer && this.culturalData.trending_hashtags) {
            hashtagsContainer.innerHTML = '';
            
            this.culturalData.trending_hashtags.forEach(hashtag => {
                const item = document.createElement('div');
                item.className = 'hashtag-item';
                item.innerHTML = `
                    <div class="hashtag-name">#${hashtag.hashtag}</div>
                    <div class="hashtag-velocity velocity-positive">+${hashtag.velocity}%</div>
                `;
                hashtagsContainer.appendChild(item);
            });
        }

        // Update TikTok insights
        const tiktokContainer = document.getElementById('tiktok-insights');
        if (tiktokContainer && this.culturalData.tiktok_insights) {
            const insights = this.culturalData.tiktok_insights;
            tiktokContainer.innerHTML = `
                <div class="insight-item">
                    <strong>Viral Content:</strong> ${insights.viral_content_count || 0} pieces
                </div>
                <div class="insight-item">
                    <strong>Trend Potential:</strong> ${Math.round(insights.trend_potential_avg || 0)}%
                </div>
                <div class="insight-item">
                    <strong>Cultural Moments:</strong> ${insights.cultural_moments?.length || 0} detected
                </div>
            `;
        }
    }

    async loadIntelligenceData() {
        // Already loaded in loadInitialData, just update display
        this.updateIntelligenceDisplay();
        
        // Update opportunities
        const opportunitiesContainer = document.getElementById('opportunities-list');
        if (opportunitiesContainer && this.culturalData.strategic_opportunities) {
            opportunitiesContainer.innerHTML = '';
            
            this.culturalData.strategic_opportunities.forEach(opportunity => {
                const item = document.createElement('div');
                item.className = 'opportunity-item';
                item.innerHTML = `
                    <div class="opportunity-header">
                        <h4>${opportunity.title}</h4>
                        <span class="priority-badge ${opportunity.priority}">${opportunity.priority}</span>
                    </div>
                    <p>${opportunity.description}</p>
                    <div class="opportunity-action">
                        <strong>Action:</strong> ${opportunity.action}
                    </div>
                `;
                opportunitiesContainer.appendChild(item);
            });
        }
    }

    async loadCulturalRadarData() {
        // Already loaded in loadInitialData, just update display
        this.updateCulturalRadarDisplay();
    }

    async loadProjectsData() {
        try {
            const response = await fetch('/api/projects');
            const projects = await response.json();
            
            const projectsGrid = document.getElementById('projects-grid');
            if (projectsGrid) {
                projectsGrid.innerHTML = '';
                
                projects.forEach(project => {
                    const card = document.createElement('div');
                    card.className = 'project-card';
                    card.innerHTML = `
                        <div class="project-header">
                            <h3>${project.name}</h3>
                            <span class="status-badge ${project.status}">${project.status}</span>
                        </div>
                        <p>${project.description}</p>
                        <div class="project-meta">
                            <div class="project-team">
                                <i class="fas fa-users"></i>
                                ${project.team_members?.length || 0} members
                            </div>
                            <div class="project-deadline">
                                <i class="fas fa-calendar"></i>
                                ${project.deadline || 'No deadline'}
                            </div>
                        </div>
                        <div class="project-actions">
                            <button class="btn btn-primary" onclick="commandCenter.openProject('${project.id}')">
                                Open Project
                            </button>
                        </div>
                    `;
                    projectsGrid.appendChild(card);
                });
            }
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    async loadAssetsData() {
        try {
            const response = await fetch('/api/assets');
            const assets = await response.json();
            
            const assetsGrid = document.getElementById('assets-grid');
            if (assetsGrid) {
                assetsGrid.innerHTML = '';
                
                assets.forEach(asset => {
                    const card = document.createElement('div');
                    card.className = 'asset-card';
                    card.innerHTML = `
                        <div class="asset-preview">
                            <i class="fas fa-${this.getAssetIcon(asset.file_type)}"></i>
                        </div>
                        <div class="asset-info">
                            <h4>${asset.name}</h4>
                            <p>${asset.category}</p>
                            <div class="asset-meta">
                                <span>${asset.file_type.toUpperCase()}</span>
                                <span>${asset.created_by}</span>
                            </div>
                        </div>
                        <div class="asset-actions">
                            <button class="btn btn-secondary" onclick="commandCenter.downloadAsset('${asset.id}')">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-secondary" onclick="commandCenter.viewAsset('${asset.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    `;
                    assetsGrid.appendChild(card);
                });
            }
        } catch (error) {
            console.error('Error loading assets:', error);
        }
    }

    async loadFileLibrary() {
        try {
            const response = await fetch('/api/files');
            const files = await response.json();
            
            const fileGrid = document.getElementById('file-library-grid');
            if (fileGrid) {
                fileGrid.innerHTML = '';
                
                files.forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.innerHTML = `
                        <div class="file-icon">
                            <i class="fas fa-${this.getFileIcon(file.type)}"></i>
                        </div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-meta">
                            ${file.size} • ${file.uploaded_date}
                        </div>
                    `;
                    item.addEventListener('click', () => this.downloadFile(file.id));
                    fileGrid.appendChild(item);
                });
            }
        } catch (error) {
            console.error('Error loading file library:', error);
        }
    }

    setupCharts() {
        // Performance Chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            this.performanceChart = new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Crooks & Castles',
                        data: [180, 195, 210, 225],
                        borderColor: '#d4af37',
                        backgroundColor: 'rgba(212, 175, 55, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Industry Average',
                        data: [1200, 1250, 1300, 1350],
                        borderColor: '#666',
                        backgroundColor: 'rgba(102, 102, 102, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#cccccc'
                            },
                            grid: {
                                color: '#333'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#cccccc'
                            },
                            grid: {
                                color: '#333'
                            }
                        }
                    }
                }
            });
        }

        // Velocity Chart
        const velocityCtx = document.getElementById('velocityChart');
        if (velocityCtx) {
            this.velocityChart = new Chart(velocityCtx, {
                type: 'bar',
                data: {
                    labels: ['#streetwear', '#y2kfashion', '#vintage', '#archive', '#heritage'],
                    datasets: [{
                        label: 'Velocity %',
                        data: [340, 280, 220, 180, 150],
                        backgroundColor: [
                            'rgba(212, 175, 55, 0.8)',
                            'rgba(255, 193, 7, 0.8)',
                            'rgba(40, 167, 69, 0.8)',
                            'rgba(23, 162, 184, 0.8)',
                            'rgba(108, 117, 125, 0.8)'
                        ],
                        borderColor: [
                            '#d4af37',
                            '#ffc107',
                            '#28a745',
                            '#17a2b8',
                            '#6c757d'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#cccccc'
                            },
                            grid: {
                                color: '#333'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#cccccc'
                            },
                            grid: {
                                color: '#333'
                            }
                        }
                    }
                }
            });
        }
    }

    switchUploadTab(type) {
        document.querySelectorAll('.upload-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');
    }

    applyFilter(filterBtn) {
        const container = filterBtn.closest('.file-library, .assets-filter').parentElement;
        const items = container.querySelectorAll('.file-item, .asset-card');
        const filter = filterBtn.dataset.filter || filterBtn.dataset.category;

        // Update active filter
        filterBtn.parentElement.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        filterBtn.classList.add('active');

        // Apply filter
        items.forEach(item => {
            if (filter === 'all') {
                item.style.display = 'block';
            } else {
                const itemCategory = item.dataset.category || item.dataset.filter;
                item.style.display = itemCategory === filter ? 'block' : 'none';
            }
        });
    }

    showNotification(type, title, message) {
        const container = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const iconMap = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${iconMap[type]}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    showModal(title, content, footer = '') {
        const overlay = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalFooter = document.getElementById('modal-footer');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modalFooter.innerHTML = footer;
        
        overlay.classList.add('active');
    }

    closeModal() {
        const overlay = document.getElementById('modal-overlay');
        overlay.classList.remove('active');
    }

    getAssetIcon(fileType) {
        const iconMap = {
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'svg': 'image',
            'mp4': 'video', 'mov': 'video', 'avi': 'video',
            'pdf': 'file-pdf', 'doc': 'file-word', 'docx': 'file-word',
            'xls': 'file-excel', 'xlsx': 'file-excel',
            'ppt': 'file-powerpoint', 'pptx': 'file-powerpoint',
            'ai': 'palette', 'psd': 'palette', 'sketch': 'palette'
        };
        return iconMap[fileType.toLowerCase()] || 'file';
    }

    getFileIcon(fileType) {
        return this.getAssetIcon(fileType);
    }

    startDataRefreshInterval() {
        // Refresh intelligence data every 5 minutes
        setInterval(() => {
            this.refreshIntelligenceData();
        }, 5 * 60 * 1000);
    }

    // Export functions
    async exportReport() {
        try {
            const response = await fetch('/api/reports/weekly', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    include_intelligence: true,
                    include_cultural: true,
                    include_competitive: true
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `crooks-weekly-report-${new Date().toISOString().split('T')[0]}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                this.showNotification('success', 'Report Exported', 'Weekly report downloaded successfully');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Error exporting report:', error);
            this.showNotification('error', 'Export Failed', 'Failed to export report');
        }
    }

    async generateWeeklyReport() {
        this.showNotification('info', 'Generating Report', 'Creating weekly intelligence report...');
        await this.exportReport();
    }

    async generateCompetitiveReport() {
        try {
            const response = await fetch('/api/reports/competitive', { method: 'POST' });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `competitive-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                this.showNotification('success', 'Report Generated', 'Competitive analysis downloaded');
            }
        } catch (error) {
            this.showNotification('error', 'Generation Failed', 'Failed to generate competitive report');
        }
    }

    async generateCulturalReport() {
        try {
            const response = await fetch('/api/reports/cultural', { method: 'POST' });
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `cultural-radar-${new Date().toISOString().split('T')[0]}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                this.showNotification('success', 'Report Generated', 'Cultural radar report downloaded');
            }
        } catch (error) {
            this.showNotification('error', 'Generation Failed', 'Failed to generate cultural report');
        }
    }

    // Utility functions for UI interactions
    viewBrandDetails(brand) {
        const brandData = this.competitiveRankings[brand];
        if (brandData) {
            this.showModal(`${brand} - Competitive Analysis`, `
                <div class="brand-details">
                    <div class="detail-row">
                        <strong>Current Rank:</strong> #${brandData.rank}
                    </div>
                    <div class="detail-row">
                        <strong>Total Posts:</strong> ${brandData.metrics?.total_posts || 0}
                    </div>
                    <div class="detail-row">
                        <strong>Average Engagement:</strong> ${brandData.metrics?.avg_engagement || 0}
                    </div>
                    <div class="detail-row">
                        <strong>Performance Tier:</strong> ${brandData.performance_tier || 'Unknown'}
                    </div>
                </div>
            `, `
                <button class="btn btn-secondary" onclick="commandCenter.closeModal()">Close</button>
                <button class="btn btn-primary" onclick="commandCenter.exportBrandReport('${brand}')">Export Report</button>
            `);
        }
    }

    createNewProject() {
        this.showModal('Create New Project', `
            <form id="new-project-form">
                <div class="form-group">
                    <label>Project Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Project Type</label>
                    <select name="type" required>
                        <option value="product_launch">Product Launch</option>
                        <option value="seasonal_collection">Seasonal Collection</option>
                        <option value="artist_collaboration">Artist Collaboration</option>
                        <option value="heritage_revival">Heritage Revival</option>
                        <option value="cultural_moment">Cultural Moment Response</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>Deadline</label>
                    <input type="date" name="deadline">
                </div>
            </form>
        `, `
            <button class="btn btn-secondary" onclick="commandCenter.closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="commandCenter.submitNewProject()">Create Project</button>
        `);
    }

    async submitNewProject() {
        const form = document.getElementById('new-project-form');
        const formData = new FormData(form);
        const projectData = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(projectData)
            });
            
            if (response.ok) {
                this.closeModal();
                this.showNotification('success', 'Project Created', 'New project created successfully');
                this.loadProjectsData();
            } else {
                throw new Error('Failed to create project');
            }
        } catch (error) {
            this.showNotification('error', 'Creation Failed', 'Failed to create project');
        }
    }
}

// Global functions for onclick handlers
function refreshIntelligence() {
    commandCenter.refreshIntelligenceData();
}

function exportReport() {
    commandCenter.exportReport();
}

function refreshIntelligenceData() {
    commandCenter.refreshIntelligenceData();
}

function exportIntelligenceReport() {
    commandCenter.generateCompetitiveReport();
}

function createProject() {
    commandCenter.createNewProject();
}

function generateReport() {
    commandCenter.generateWeeklyReport();
}

function generateWeeklyReport() {
    commandCenter.generateWeeklyReport();
}

function generateCompetitiveReport() {
    commandCenter.generateCompetitiveReport();
}

function generateCulturalReport() {
    commandCenter.generateCulturalReport();
}

function generateTeamReport() {
    commandCenter.showNotification('info', 'Coming Soon', 'Team performance reports will be available soon');
}

function showTab(tabName) {
    commandCenter.showTab(tabName);
}

function closeModal() {
    commandCenter.closeModal();
}

// Initialize the application
let commandCenter;
document.addEventListener('DOMContentLoaded', function() {
    commandCenter = new CrooksCommandCenter();
});
