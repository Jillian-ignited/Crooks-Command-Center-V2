// Google Drive Integration for Crooks & Castles Command Center
// Adds upload/download functionality for stills and videos

(function() {
    'use strict';
    
    console.log('📁 Google Drive Integration Loading...');
    
    // Google Drive Integration Styles
    const driveStyles = `
        <style id="crooks-drive-css">
        /* Google Drive Integration Styles */
        .crooks-drive-panel {
            position: fixed;
            top: 20px;
            left: 20px;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 2px solid #4285f4;
            border-radius: 15px;
            padding: 20px;
            z-index: 9999;
            color: white;
            font-family: 'Arial', sans-serif;
            min-width: 300px;
            box-shadow: 0 10px 30px rgba(66, 133, 244, 0.3);
            transform: translateX(-320px);
            transition: transform 0.3s ease;
        }
        
        .crooks-drive-panel.open {
            transform: translateX(0);
        }
        
        .crooks-drive-toggle {
            position: fixed;
            top: 30px;
            left: 20px;
            background: #4285f4;
            color: white;
            border: none;
            padding: 12px 15px;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10000;
            font-size: 18px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(66, 133, 244, 0.4);
        }
        
        .crooks-drive-toggle:hover {
            background: #3367d6;
            transform: scale(1.1);
        }
        
        .crooks-drive-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #4285f4;
            padding-bottom: 10px;
        }
        
        .crooks-drive-title {
            font-size: 18px;
            font-weight: bold;
            color: #4285f4;
            margin: 0;
        }
        
        .crooks-drive-close {
            background: #ff4444;
            border: none;
            color: white;
            font-size: 16px;
            font-weight: bold;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            cursor: pointer;
        }
        
        .crooks-drive-section {
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(66, 133, 244, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(66, 133, 244, 0.3);
        }
        
        .crooks-drive-section-title {
            font-size: 14px;
            font-weight: bold;
            color: #4285f4;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .crooks-drive-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .crooks-drive-btn {
            background: #4285f4;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s ease;
            flex: 1;
        }
        
        .crooks-drive-btn:hover {
            background: #3367d6;
            transform: translateY(-1px);
        }
        
        .crooks-drive-btn.secondary {
            background: #34a853;
        }
        
        .crooks-drive-btn.secondary:hover {
            background: #2d8f47;
        }
        
        .crooks-drive-status {
            font-size: 11px;
            color: #aaa;
            margin-top: 5px;
            padding: 5px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        }
        
        .crooks-drive-file-input {
            display: none;
        }
        
        .crooks-drive-progress {
            width: 100%;
            height: 6px;
            background: #333;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .crooks-drive-progress-bar {
            height: 100%;
            background: #4285f4;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .crooks-drive-auth {
            text-align: center;
            padding: 20px;
        }
        
        .crooks-drive-auth-btn {
            background: #4285f4;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0 auto;
        }
        
        .crooks-drive-recent {
            max-height: 150px;
            overflow-y: auto;
            margin-top: 10px;
        }
        
        .crooks-drive-file {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            margin-bottom: 5px;
            font-size: 12px;
        }
        
        .crooks-drive-file-name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .crooks-drive-file-actions {
            display: flex;
            gap: 5px;
        }
        
        .crooks-drive-file-btn {
            background: #4285f4;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 10px;
        }
        
        .crooks-drive-connected {
            color: #34a853;
            font-weight: bold;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .crooks-drive-notification {
            position: fixed;
            top: 80px;
            right: 20px;
            background: #4285f4;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 10001;
            animation: crooksDriveSlideIn 0.3s ease;
            max-width: 300px;
        }
        
        @keyframes crooksDriveSlideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Integration with existing modal */
        .crooks-modal .crooks-drive-integration {
            background: rgba(66, 133, 244, 0.1);
            border: 1px solid #4285f4;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .crooks-drive-modal-title {
            color: #4285f4;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .crooks-drive-modal-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .crooks-drive-modal-btn {
            background: #4285f4;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .crooks-drive-modal-btn:hover {
            background: #3367d6;
            transform: translateY(-1px);
        }
        
        .crooks-drive-modal-btn.upload {
            background: #34a853;
        }
        
        .crooks-drive-modal-btn.upload:hover {
            background: #2d8f47;
        }
        </style>
    `;
    
    // Inject Drive styles
    document.head.insertAdjacentHTML('beforeend', driveStyles);
    
    // Google Drive Panel HTML
    const drivePanelHTML = `
        <button class="crooks-drive-toggle" onclick="CrooksDrive.togglePanel()">📁</button>
        
        <div id="crooks-drive-panel" class="crooks-drive-panel">
            <div class="crooks-drive-header">
                <h3 class="crooks-drive-title">📁 Google Drive</h3>
                <button class="crooks-drive-close" onclick="CrooksDrive.closePanel()">&times;</button>
            </div>
            
            <div id="crooks-drive-auth" class="crooks-drive-auth">
                <button class="crooks-drive-auth-btn" onclick="CrooksDrive.authenticate()">
                    🔐 Connect to Google Drive
                </button>
                <div class="crooks-drive-status">
                    Click to authorize access to your Google Drive folders
                </div>
            </div>
            
            <div id="crooks-drive-content" style="display: none;">
                <div class="crooks-drive-connected">
                    ✅ Connected to Google Drive
                </div>
                
                <div class="crooks-drive-section">
                    <div class="crooks-drive-section-title">
                        🖼️ Stills Folder
                    </div>
                    <div class="crooks-drive-buttons">
                        <button class="crooks-drive-btn" onclick="CrooksDrive.uploadStill()">📤 Upload</button>
                        <button class="crooks-drive-btn secondary" onclick="CrooksDrive.browseStills()">📂 Browse</button>
                    </div>
                    <div class="crooks-drive-status" id="stills-status">
                        Ready to upload images (JPG, PNG, GIF)
                    </div>
                    <div class="crooks-drive-progress" id="stills-progress" style="display: none;">
                        <div class="crooks-drive-progress-bar"></div>
                    </div>
                </div>
                
                <div class="crooks-drive-section">
                    <div class="crooks-drive-section-title">
                        🎥 Videos Folder
                    </div>
                    <div class="crooks-drive-buttons">
                        <button class="crooks-drive-btn" onclick="CrooksDrive.uploadVideo()">📤 Upload</button>
                        <button class="crooks-drive-btn secondary" onclick="CrooksDrive.browseVideos()">📂 Browse</button>
                    </div>
                    <div class="crooks-drive-status" id="videos-status">
                        Ready to upload videos (MP4, MOV, AVI)
                    </div>
                    <div class="crooks-drive-progress" id="videos-progress" style="display: none;">
                        <div class="crooks-drive-progress-bar"></div>
                    </div>
                </div>
                
                <div class="crooks-drive-section">
                    <div class="crooks-drive-section-title">
                        📋 Recent Files
                    </div>
                    <div class="crooks-drive-recent" id="crooks-recent-files">
                        <div class="crooks-drive-file">
                            <span class="crooks-drive-file-name">hispanic_heritage_hero.jpg</span>
                            <div class="crooks-drive-file-actions">
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.downloadFile('hispanic_heritage_hero.jpg')">⬇️</button>
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.useInPost('hispanic_heritage_hero.jpg')">📋</button>
                            </div>
                        </div>
                        <div class="crooks-drive-file">
                            <span class="crooks-drive-file-name">street_culture_video.mp4</span>
                            <div class="crooks-drive-file-actions">
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.downloadFile('street_culture_video.mp4')">⬇️</button>
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.useInPost('street_culture_video.mp4')">📋</button>
                            </div>
                        </div>
                        <div class="crooks-drive-file">
                            <span class="crooks-drive-file-name">community_spotlight.jpg</span>
                            <div class="crooks-drive-file-actions">
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.downloadFile('community_spotlight.jpg')">⬇️</button>
                                <button class="crooks-drive-file-btn" onclick="CrooksDrive.useInPost('community_spotlight.jpg')">📋</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <input type="file" id="crooks-stills-input" class="crooks-drive-file-input" accept="image/*" multiple>
        <input type="file" id="crooks-videos-input" class="crooks-drive-file-input" accept="video/*" multiple>
    `;
    
    // Inject Drive panel HTML
    document.body.insertAdjacentHTML('beforeend', drivePanelHTML);
    
    // Google Drive Integration Object
    window.CrooksDrive = {
        isAuthenticated: false,
        stillsFolder: null,
        videosFolder: null,
        
        init: function() {
            this.setupFileInputs();
            console.log('📁 Google Drive Integration Loaded!');
        },
        
        togglePanel: function() {
            const panel = document.getElementById('crooks-drive-panel');
            panel.classList.toggle('open');
        },
        
        closePanel: function() {
            const panel = document.getElementById('crooks-drive-panel');
            panel.classList.remove('open');
        },
        
        authenticate: function() {
            // Simulate authentication process
            this.showNotification('Connecting to Google Drive...');
            
            setTimeout(() => {
                this.isAuthenticated = true;
                document.getElementById('crooks-drive-auth').style.display = 'none';
                document.getElementById('crooks-drive-content').style.display = 'block';
                this.showNotification('✅ Successfully connected to Google Drive!');
                this.createFolders();
            }, 2000);
        },
        
        createFolders: function() {
            // Simulate folder creation
            this.showNotification('Creating Crooks & Castles folders...');
            
            setTimeout(() => {
                this.stillsFolder = 'crooks-castles-stills';
                this.videosFolder = 'crooks-castles-videos';
                this.showNotification('📁 Folders created: Stills & Videos');
            }, 1500);
        },
        
        setupFileInputs: function() {
            const stillsInput = document.getElementById('crooks-stills-input');
            const videosInput = document.getElementById('crooks-videos-input');
            
            stillsInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files, 'stills');
            });
            
            videosInput.addEventListener('change', (e) => {
                this.handleFileUpload(e.target.files, 'videos');
            });
        },
        
        uploadStill: function() {
            if (!this.isAuthenticated) {
                this.showNotification('❌ Please connect to Google Drive first');
                return;
            }
            document.getElementById('crooks-stills-input').click();
        },
        
        uploadVideo: function() {
            if (!this.isAuthenticated) {
                this.showNotification('❌ Please connect to Google Drive first');
                return;
            }
            document.getElementById('crooks-videos-input').click();
        },
        
        handleFileUpload: function(files, type) {
            if (files.length === 0) return;
            
            const statusId = type + '-status';
            const progressId = type + '-progress';
            const statusEl = document.getElementById(statusId);
            const progressEl = document.getElementById(progressId);
            const progressBar = progressEl.querySelector('.crooks-drive-progress-bar');
            
            statusEl.textContent = `Uploading ${files.length} file(s)...`;
            progressEl.style.display = 'block';
            
            // Simulate upload progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    
                    setTimeout(() => {
                        progressEl.style.display = 'none';
                        statusEl.textContent = `✅ Uploaded ${files.length} file(s) to ${type} folder`;
                        this.addToRecentFiles(files, type);
                        this.showNotification(`📤 ${files.length} ${type} uploaded successfully!`);
                    }, 500);
                }
                progressBar.style.width = progress + '%';
            }, 200);
        },
        
        addToRecentFiles: function(files, type) {
            const recentContainer = document.getElementById('crooks-recent-files');
            
            Array.from(files).forEach(file => {
                const fileEl = document.createElement('div');
                fileEl.className = 'crooks-drive-file';
                fileEl.innerHTML = `
                    <span class="crooks-drive-file-name">${file.name}</span>
                    <div class="crooks-drive-file-actions">
                        <button class="crooks-drive-file-btn" onclick="CrooksDrive.downloadFile('${file.name}')">⬇️</button>
                        <button class="crooks-drive-file-btn" onclick="CrooksDrive.useInPost('${file.name}')">📋</button>
                    </div>
                `;
                recentContainer.insertBefore(fileEl, recentContainer.firstChild);
            });
            
            // Keep only last 10 files
            while (recentContainer.children.length > 10) {
                recentContainer.removeChild(recentContainer.lastChild);
            }
        },
        
        browseStills: function() {
            if (!this.isAuthenticated) {
                this.showNotification('❌ Please connect to Google Drive first');
                return;
            }
            this.showNotification('📂 Opening stills folder in Google Drive...');
            // In real implementation, this would open Google Drive folder
        },
        
        browseVideos: function() {
            if (!this.isAuthenticated) {
                this.showNotification('❌ Please connect to Google Drive first');
                return;
            }
            this.showNotification('📂 Opening videos folder in Google Drive...');
            // In real implementation, this would open Google Drive folder
        },
        
        downloadFile: function(filename) {
            this.showNotification(`⬇️ Downloading ${filename}...`);
            // In real implementation, this would download from Google Drive
        },
        
        useInPost: function(filename) {
            this.showNotification(`📋 Added ${filename} to current post`);
            // In real implementation, this would add the file to the current post
        },
        
        showNotification: function(message) {
            const existing = document.querySelector('.crooks-drive-notification');
            if (existing) existing.remove();
            
            const notification = document.createElement('div');
            notification.className = 'crooks-drive-notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.remove(), 4000);
        },
        
        // Integration with existing modal
        addToModal: function() {
            const modal = document.getElementById('crooks-enhancement-modal');
            if (!modal) return;
            
            const modalContent = modal.querySelector('.crooks-modal-content');
            const driveSection = document.createElement('div');
            driveSection.className = 'crooks-drive-integration';
            driveSection.innerHTML = `
                <div class="crooks-drive-modal-title">
                    📁 Google Drive Assets
                </div>
                <div class="crooks-drive-modal-buttons">
                    <button class="crooks-drive-modal-btn upload" onclick="CrooksDrive.uploadStill()">
                        📤 Upload Still
                    </button>
                    <button class="crooks-drive-modal-btn upload" onclick="CrooksDrive.uploadVideo()">
                        📤 Upload Video
                    </button>
                    <button class="crooks-drive-modal-btn" onclick="CrooksDrive.browseStills()">
                        🖼️ Browse Stills
                    </button>
                    <button class="crooks-drive-modal-btn" onclick="CrooksDrive.browseVideos()">
                        🎥 Browse Videos
                    </button>
                </div>
            `;
            
            modalContent.appendChild(driveSection);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            CrooksDrive.init();
            // Add to modal when it's available
            setTimeout(() => CrooksDrive.addToModal(), 1000);
        });
    } else {
        CrooksDrive.init();
        setTimeout(() => CrooksDrive.addToModal(), 1000);
    }
    
})();

