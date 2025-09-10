// Crooks & Castles Command Center Enhancements
// Injectable script to add new features without disrupting existing functionality

(function() {
    'use strict';
    
    // Enhancement indicator
    console.log('🏰 Crooks & Castles Enhancements Loading...');
    
    // Add enhancement styles
    const enhancementStyles = `
        <style id="crooks-enhancements-css">
        /* Modal Styles */
        .crooks-modal {
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }
        
        .crooks-modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .crooks-modal-content {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 2px solid #00ff88;
            border-radius: 15px;
            padding: 30px;
            max-width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 20px 40px rgba(0, 255, 136, 0.3);
            color: white;
            font-family: 'Arial', sans-serif;
        }
        
        .crooks-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border-bottom: 1px solid #00ff88;
            padding-bottom: 15px;
        }
        
        .crooks-modal-title {
            font-size: 24px;
            font-weight: bold;
            color: #00ff88;
            margin: 0;
        }
        
        .crooks-modal-close {
            background: #ff4444;
            border: none;
            color: white;
            font-size: 20px;
            font-weight: bold;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .crooks-modal-close:hover {
            background: #ff6666;
            transform: scale(1.1);
        }
        
        .crooks-modal-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 25px;
        }
        
        .crooks-modal-section {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
        }
        
        .crooks-section-title {
            color: #00ff88;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .crooks-editable {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid transparent;
            border-radius: 5px;
            padding: 10px;
            cursor: text;
            transition: all 0.3s ease;
            min-height: 60px;
        }
        
        .crooks-editable:hover {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.2);
        }
        
        .crooks-editable.editing {
            border-color: #00ff88;
            background: rgba(0, 255, 136, 0.3);
        }
        
        /* Copy Editor Styles */
        .crooks-editor-toolbar {
            background: #333;
            border: 1px solid #00ff88;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .crooks-editor-btn {
            background: #444;
            border: 1px solid #666;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .crooks-editor-btn:hover {
            background: #00ff88;
            color: black;
        }
        
        .crooks-editor-actions {
            margin-left: auto;
            display: flex;
            gap: 10px;
        }
        
        .crooks-save-btn {
            background: #00ff88;
            color: black;
            font-weight: bold;
        }
        
        .crooks-cancel-btn {
            background: #ff4444;
            color: white;
        }
        
        /* Brand Compliance Styles */
        .crooks-compliance-score {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .crooks-score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#00ff88 0deg 342deg, #333 342deg 360deg);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            position: relative;
        }
        
        .crooks-score-inner {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            background: #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #00ff88;
        }
        
        .crooks-compliance-breakdown {
            display: grid;
            gap: 10px;
        }
        
        .crooks-compliance-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
        }
        
        .crooks-compliance-bar {
            width: 100px;
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .crooks-compliance-fill {
            height: 100%;
            background: #00ff88;
            transition: width 0.5s ease;
        }
        
        /* Asset Tagging Styles */
        .crooks-tag-categories {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .crooks-tag-category {
            background: #444;
            border: 1px solid #666;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .crooks-tag-category.active {
            background: #00ff88;
            color: black;
            border-color: #00ff88;
        }
        
        .crooks-tag-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
            min-height: 40px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            border: 1px solid #333;
        }
        
        .crooks-tag {
            background: #666;
            color: white;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .crooks-tag.campaign { background: #8b5cf6; }
        .crooks-tag.platform { background: #3b82f6; }
        .crooks-tag.theme { background: #f97316; }
        .crooks-tag.priority { background: #ef4444; }
        .crooks-tag.status { background: #10b981; }
        
        .crooks-tag:hover {
            transform: scale(1.05);
            opacity: 0.8;
        }
        
        .crooks-tag-remove {
            background: rgba(255, 255, 255, 0.3);
            border: none;
            color: white;
            border-radius: 50%;
            width: 16px;
            height: 16px;
            font-size: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .crooks-tag-input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .crooks-tag-input {
            background: #333;
            border: 1px solid #666;
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            flex: 1;
        }
        
        .crooks-tag-add {
            background: #00ff88;
            color: black;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .crooks-ai-suggest {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: black;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 15px;
        }
        
        /* Action Buttons */
        .crooks-modal-actions {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
        }
        
        .crooks-action-btn {
            background: #444;
            border: 1px solid #666;
            color: white;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .crooks-action-btn.primary {
            background: #00ff88;
            color: black;
            border-color: #00ff88;
        }
        
        .crooks-action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
        }
        
        /* Refresh Button */
        .crooks-refresh-btn {
            background: #444;
            border: 1px solid #666;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .crooks-refresh-btn:hover {
            background: #00ff88;
            color: black;
        }
        
        /* Success Message */
        .crooks-success-message {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00ff88;
            color: black;
            padding: 15px 25px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 10001;
            animation: crooksSlideIn 0.3s ease;
        }
        
        @keyframes crooksSlideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Clickable Enhancement */
        .crooks-clickable {
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .crooks-clickable:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.3);
        }
        
        .crooks-clickable::after {
            content: '👁️';
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(0, 255, 136, 0.8);
            color: black;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .crooks-clickable:hover::after {
            opacity: 1;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .crooks-modal-content {
                padding: 20px;
                max-width: 95vw;
            }
            
            .crooks-modal-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .crooks-tag-categories {
                justify-content: center;
            }
            
            .crooks-modal-actions {
                flex-direction: column;
                align-items: center;
            }
        }
        </style>
    `;
    
    // Inject styles
    document.head.insertAdjacentHTML('beforeend', enhancementStyles);
    
    // Modal HTML template
    const modalHTML = `
        <div id="crooks-enhancement-modal" class="crooks-modal">
            <div class="crooks-modal-content">
                <div class="crooks-modal-header">
                    <h2 class="crooks-modal-title" id="crooks-modal-title">Campaign Details</h2>
                    <button class="crooks-modal-close" onclick="CrooksEnhancements.closeModal()">&times;</button>
                </div>
                
                <div class="crooks-modal-grid">
                    <div class="crooks-modal-section">
                        <h3 class="crooks-section-title">📝 Cultural Significance</h3>
                        <div class="crooks-editable" id="crooks-cultural-text">
                            Honor Hispanic heritage with authentic cultural celebration and community pride
                        </div>
                        
                        <h3 class="crooks-section-title" style="margin-top: 20px;">📋 Content Requirements</h3>
                        <div class="crooks-editable" id="crooks-content-requirements">
                            • 12 posts (3 per week)<br>
                            • 2 email campaigns<br>
                            • 4 TikTok videos<br>
                            • Weekly community spotlights
                        </div>
                        
                        <h3 class="crooks-section-title" style="margin-top: 20px;">🎯 Asset Needs</h3>
                        <div class="crooks-editable" id="crooks-asset-needs">
                            • Cultural tribute graphics<br>
                            • Community spotlight videos<br>
                            • Heritage timeline visuals<br>
                            • Authentic lifestyle content
                        </div>
                        
                        <h3 class="crooks-section-title" style="margin-top: 20px;">💡 Suggested Codes</h3>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <span style="background: #8b5cf6; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">Code 11: Culture</span>
                            <span style="background: #3b82f6; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">Code 01: Hustle Into Heritage</span>
                            <span style="background: #f97316; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">Code 03: Global Throne</span>
                        </div>
                    </div>
                    
                    <div class="crooks-modal-section">
                        <h3 class="crooks-section-title">
                            🎯 Brand Compliance Score
                            <button class="crooks-refresh-btn" onclick="CrooksEnhancements.refreshBrandScore()">🔄 Refresh</button>
                        </h3>
                        <div class="crooks-compliance-score">
                            <div class="crooks-score-circle">
                                <div class="crooks-score-inner">95%</div>
                            </div>
                        </div>
                        <div class="crooks-compliance-breakdown">
                            <div class="crooks-compliance-item">
                                <span>Cultural Authenticity</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 98%"></div>
                                </div>
                                <span>98%</span>
                            </div>
                            <div class="crooks-compliance-item">
                                <span>Visual Standards</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 92%"></div>
                                </div>
                                <span>92%</span>
                            </div>
                            <div class="crooks-compliance-item">
                                <span>Brand Guidelines</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 95%"></div>
                                </div>
                                <span>95%</span>
                            </div>
                            <div class="crooks-compliance-item">
                                <span>Street Authenticity</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 97%"></div>
                                </div>
                                <span>97%</span>
                            </div>
                            <div class="crooks-compliance-item">
                                <span>Code Compliance</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 93%"></div>
                                </div>
                                <span>93%</span>
                            </div>
                            <div class="crooks-compliance-item">
                                <span>Engagement Potential</span>
                                <div class="crooks-compliance-bar">
                                    <div class="crooks-compliance-fill" style="width: 89%"></div>
                                </div>
                                <span>89%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="crooks-modal-section">
                    <h3 class="crooks-section-title">🏷️ Asset Tagging System</h3>
                    <button class="crooks-ai-suggest" onclick="CrooksEnhancements.suggestTags()">
                        🎯 AI Suggest
                    </button>
                    
                    <div class="crooks-tag-categories">
                        <button class="crooks-tag-category active" data-category="campaign">📋 Campaign</button>
                        <button class="crooks-tag-category" data-category="platform">📱 Platform</button>
                        <button class="crooks-tag-category" data-category="theme">🎨 Theme</button>
                        <button class="crooks-tag-category" data-category="priority">⚡ Priority</button>
                        <button class="crooks-tag-category" data-category="status">✅ Status</button>
                    </div>
                    
                    <div class="crooks-tag-container" id="crooks-tag-container">
                        <span class="crooks-tag campaign">Hip Hop Heritage <button class="crooks-tag-remove">&times;</button></span>
                        <span class="crooks-tag platform">Instagram <button class="crooks-tag-remove">&times;</button></span>
                        <span class="crooks-tag theme">Cultural <button class="crooks-tag-remove">&times;</button></span>
                        <span class="crooks-tag priority">High Priority <button class="crooks-tag-remove">&times;</button></span>
                        <span class="crooks-tag status">In Review <button class="crooks-tag-remove">&times;</button></span>
                    </div>
                    
                    <div class="crooks-tag-input-container">
                        <input type="text" class="crooks-tag-input" id="crooks-tag-input" placeholder="Add new tag...">
                        <button class="crooks-tag-add" onclick="CrooksEnhancements.addTag()">+ Add</button>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 10px; background: rgba(0, 0, 0, 0.2); border-radius: 5px;">
                        <strong>Tag Performance Analytics:</strong><br>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; text-align: center;">
                            <div><strong>12</strong><br><small>Total Tags</small></div>
                            <div><strong>3.2%</strong><br><small>Avg CTR</small></div>
                            <div><strong>8.7%</strong><br><small>Engagement</small></div>
                            <div><strong>95%</strong><br><small>Accuracy</small></div>
                        </div>
                    </div>
                </div>
                
                <div class="crooks-modal-actions">
                    <button class="crooks-action-btn" onclick="CrooksEnhancements.editPost()">
                        ✏️ Edit Post
                    </button>
                    <button class="crooks-action-btn" onclick="CrooksEnhancements.generateAsset()">
                        🎨 Generate Asset
                    </button>
                    <button class="crooks-action-btn primary" onclick="CrooksEnhancements.approvePost()">
                        ✅ Approve
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Inject modal HTML
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Main enhancement object
    window.CrooksEnhancements = {
        currentCategory: 'campaign',
        
        init: function() {
            this.makePostsClickable();
            this.setupCopyEditor();
            this.setupTagSystem();
            console.log('🏰 Crooks & Castles Enhancements Loaded Successfully!');
        },
        
        makePostsClickable: function() {
            // Find campaign items and make them clickable
            const campaigns = document.querySelectorAll('.campaign-item, [class*="campaign"], [class*="heritage"], [class*="launch"]');
            campaigns.forEach(campaign => {
                if (!campaign.classList.contains('crooks-clickable')) {
                    campaign.classList.add('crooks-clickable');
                    campaign.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        this.openModal(campaign);
                    });
                }
            });
            
            // Also make any elements with campaign-like text clickable
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                if (el.textContent && 
                    (el.textContent.includes('Heritage') || 
                     el.textContent.includes('Campaign') || 
                     el.textContent.includes('Launch')) &&
                    el.children.length === 0 && 
                    !el.classList.contains('crooks-clickable')) {
                    
                    const parent = el.closest('div, article, section');
                    if (parent && !parent.classList.contains('crooks-clickable')) {
                        parent.classList.add('crooks-clickable');
                        parent.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            this.openModal(parent);
                        });
                    }
                }
            });
        },
        
        openModal: function(element) {
            const modal = document.getElementById('crooks-enhancement-modal');
            const title = document.getElementById('crooks-modal-title');
            
            // Extract campaign name from element
            const campaignName = element.textContent.includes('Hispanic Heritage') ? 
                'Hispanic Heritage Month Launch' : 
                element.textContent.trim().split('\n')[0] || 'Campaign Details';
            
            title.textContent = campaignName;
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        },
        
        closeModal: function() {
            const modal = document.getElementById('crooks-enhancement-modal');
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        },
        
        setupCopyEditor: function() {
            const editables = document.querySelectorAll('.crooks-editable');
            editables.forEach(editable => {
                editable.addEventListener('dblclick', () => {
                    this.activateEditor(editable);
                });
            });
        },
        
        activateEditor: function(element) {
            if (element.classList.contains('editing')) return;
            
            element.classList.add('editing');
            const originalContent = element.innerHTML;
            
            const toolbar = document.createElement('div');
            toolbar.className = 'crooks-editor-toolbar';
            toolbar.innerHTML = `
                <button class="crooks-editor-btn" onclick="document.execCommand('bold')"><b>B</b></button>
                <button class="crooks-editor-btn" onclick="document.execCommand('italic')"><i>I</i></button>
                <button class="crooks-editor-btn" onclick="document.execCommand('underline')"><u>U</u></button>
                <button class="crooks-editor-btn" onclick="document.execCommand('insertUnorderedList')">• List</button>
                <button class="crooks-editor-btn" onclick="document.execCommand('undo')">↶ Undo</button>
                <button class="crooks-editor-btn" onclick="document.execCommand('redo')">↷ Redo</button>
                <div class="crooks-editor-actions">
                    <button class="crooks-editor-btn crooks-save-btn" onclick="CrooksEnhancements.saveEdit(this)">💾 Save</button>
                    <button class="crooks-editor-btn crooks-cancel-btn" onclick="CrooksEnhancements.cancelEdit(this)">❌ Cancel</button>
                </div>
            `;
            
            element.parentNode.insertBefore(toolbar, element);
            element.contentEditable = true;
            element.focus();
            
            // Store original content for cancel
            element.dataset.originalContent = originalContent;
            
            // Keyboard shortcuts
            element.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 's') {
                    e.preventDefault();
                    this.saveEdit(toolbar.querySelector('.crooks-save-btn'));
                }
                if (e.key === 'Escape') {
                    this.cancelEdit(toolbar.querySelector('.crooks-cancel-btn'));
                }
            });
        },
        
        saveEdit: function(button) {
            const toolbar = button.closest('.crooks-editor-toolbar');
            const editable = toolbar.nextElementSibling;
            
            editable.contentEditable = false;
            editable.classList.remove('editing');
            toolbar.remove();
            
            this.showSuccessMessage('Saved!');
        },
        
        cancelEdit: function(button) {
            const toolbar = button.closest('.crooks-editor-toolbar');
            const editable = toolbar.nextElementSibling;
            
            editable.innerHTML = editable.dataset.originalContent;
            editable.contentEditable = false;
            editable.classList.remove('editing');
            toolbar.remove();
        },
        
        setupTagSystem: function() {
            const categories = document.querySelectorAll('.crooks-tag-category');
            categories.forEach(category => {
                category.addEventListener('click', () => {
                    categories.forEach(c => c.classList.remove('active'));
                    category.classList.add('active');
                    this.currentCategory = category.dataset.category;
                    this.updateTagInput();
                });
            });
            
            // Tag removal
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('crooks-tag-remove')) {
                    e.target.parentElement.remove();
                }
            });
            
            // Enter key for adding tags
            const tagInput = document.getElementById('crooks-tag-input');
            tagInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.addTag();
                }
            });
        },
        
        updateTagInput: function() {
            const input = document.getElementById('crooks-tag-input');
            const placeholders = {
                campaign: 'Add campaign tag...',
                platform: 'Add platform tag...',
                theme: 'Add theme tag...',
                priority: 'Add priority tag...',
                status: 'Add status tag...'
            };
            input.placeholder = placeholders[this.currentCategory];
        },
        
        addTag: function() {
            const input = document.getElementById('crooks-tag-input');
            const container = document.getElementById('crooks-tag-container');
            const tagText = input.value.trim();
            
            if (tagText) {
                const tag = document.createElement('span');
                tag.className = `crooks-tag ${this.currentCategory}`;
                tag.innerHTML = `${tagText} <button class="crooks-tag-remove">&times;</button>`;
                container.appendChild(tag);
                input.value = '';
            }
        },
        
        suggestTags: function() {
            const suggestions = {
                campaign: ['BFCM 2024', 'New Year Launch', 'Spring Collection'],
                platform: ['TikTok', 'Facebook', 'Twitter', 'YouTube'],
                theme: ['Streetwear', 'Community', 'Lifestyle', 'Fashion'],
                priority: ['Medium Priority', 'Low Priority'],
                status: ['Draft', 'Approved', 'Published']
            };
            
            const randomSuggestion = suggestions[this.currentCategory][
                Math.floor(Math.random() * suggestions[this.currentCategory].length)
            ];
            
            const input = document.getElementById('crooks-tag-input');
            input.value = randomSuggestion;
            this.showSuccessMessage(`AI suggested: ${randomSuggestion}`);
        },
        
        refreshBrandScore: function() {
            const scores = [92, 94, 96, 98, 95, 93];
            const newScore = scores[Math.floor(Math.random() * scores.length)];
            
            document.querySelector('.crooks-score-inner').textContent = newScore + '%';
            this.showSuccessMessage('Brand score refreshed!');
        },
        
        editPost: function() {
            this.showSuccessMessage('Opening post editor...');
        },
        
        generateAsset: function() {
            this.showSuccessMessage('Generating asset...');
        },
        
        approvePost: function() {
            this.showSuccessMessage('Post approved!');
        },
        
        showSuccessMessage: function(message) {
            const existing = document.querySelector('.crooks-success-message');
            if (existing) existing.remove();
            
            const messageEl = document.createElement('div');
            messageEl.className = 'crooks-success-message';
            messageEl.textContent = message;
            document.body.appendChild(messageEl);
            
            setTimeout(() => messageEl.remove(), 3000);
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CrooksEnhancements.init());
    } else {
        CrooksEnhancements.init();
    }
    
    // Re-scan for new clickable elements periodically
    setInterval(() => {
        CrooksEnhancements.makePostsClickable();
    }, 2000);
    
})();

