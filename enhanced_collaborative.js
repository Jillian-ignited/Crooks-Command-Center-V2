/* Crooks & Castles Command Center V2 - Enhanced Interactive Functionality */
/* ============================================================================
   GLOBAL VARIABLES & CONFIGURATION
   ============================================================================ */

let currentTab = 'intelligence';
let currentCalendarView = '7day';
let intelligenceData = {};
let assetData = {};
let calendarData = {};
let agencyData = {};

// API endpoints configuration
const API_ENDPOINTS = {
    intelligence: '/api/intelligence',
    assets: '/api/assets',
    calendar: '/api/calendar',
    agency: '/api/agency',
    upload: '/api/upload',
    reports: '/api/reports/weekly',
    download: '/api/reports/weekly/download'
};

// Animation configuration
const ANIMATION_DURATION = 300;
const FADE_DURATION = 500;

/* ============================================================================
   INITIALIZATION & EVENT LISTENERS
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    console.log('🏰 Crooks & Castles Command Center V2 - Initializing...');
    
    // Set initial tab
    showTab('intelligence');
    
    // Initialize tooltips and animations
    initializeTooltips();
    initializeAnimations();
    
    // Setup periodic data refresh
    setupDataRefresh();
    
    console.log('✅ Command Center initialized successfully');
}

function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', handleTabClick);
    });
    
    // File upload handling
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Upload area drag and drop
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        setupDragAndDrop(uploadArea);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
    
    // Window resize handling
    window.addEventListener('resize', handleWindowResize);
}

function loadInitialData() {
    // Load data for all tabs to ensure smooth switching
    loadIntelligenceData();
    loadAssetLibrary();
    loadCalendarData('7day');
    loadAgencyData();
}

/* ============================================================================
   TAB MANAGEMENT
   ============================================================================ */

function showTab(tabName) {
    // Update current tab
    currentTab = tabName;
    
    // Hide all tab contents with fade out
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.opacity = '0';
        setTimeout(() => {
            content.classList.remove('active');
        }, ANIMATION_DURATION / 2);
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content with fade in
    setTimeout(() => {
        const selectedContent = document.getElementById(tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
            selectedContent.style.opacity = '1';
        }
        
        // Add active class to clicked tab
        const activeTab = document.querySelector(`.tab[onclick*="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        // Load data for the selected tab
        loadTabData(tabName);
        
        // Update URL hash
        window.location.hash = tabName;
        
    }, ANIMATION_DURATION / 2);
}

function handleTabClick(event) {
    const tabName = event.currentTarget.getAttribute('onclick').match(/'([^']+)'/)[1];
    showTab(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'intelligence':
            loadIntelligenceData();
            break;
        case 'assets':
            loadAssetLibrary();
            break;
        case 'calendar':
            loadCalendarData(currentCalendarView);
            break;
        case 'agency':
            loadAgencyData();
            break;
        case 'upload':
            // Upload tab doesn't need data loading
            break;
    }
}

/* ============================================================================
   INTELLIGENCE DASHBOARD
   ============================================================================ */

function loadIntelligenceData() {
    showLoadingState('intelligence');
    
    fetch(API_ENDPOINTS.intelligence)
        .then(response => response.json())
        .then(data => {
            intelligenceData = data;
            updateIntelligenceDisplay(data);
            hideLoadingState('intelligence');
        })
        .catch(error => {
            console.log('Loading sample intelligence data...');
            loadSampleIntelligenceData();
            hideLoadingState('intelligence');
        });
}

function updateIntelligenceDisplay(data) {
    // Update header stats
    updateElement('header-posts', data.summary?.total_posts_analyzed || 354);
    updateElement('instagram-posts', data.summary?.total_posts_analyzed || 354);
    updateElement('tiktok-videos', data.summary?.total_tiktok_videos || 16);
    updateElement('instagram-hashtags', data.summary?.total_hashtags_tracked || 45);
    
    // Calculate and display engagement rates
    const instagramEngagement = calculateEngagementRate(data.instagram_posts || []);
    const tiktokEngagement = calculateEngagementRate(data.tiktok_videos || []);
    
    updateElement('instagram-engagement', `${instagramEngagement}%`);
    updateElement('tiktok-engagement', `${tiktokEngagement}%`);
    
    // Update top hashtags
    updateTopHashtags(data.top_hashtags || []);
    
    // Update competitive rankings
    updateCompetitiveRankings(data.competitive_data || []);
}

function loadSampleIntelligenceData() {
    const sampleData = {
        summary: {
            total_posts_analyzed: 354,
            total_tiktok_videos: 16,
            total_hashtags_tracked: 45,
            last_updated: new Date().toISOString()
        },
        top_hashtags: [
            { hashtag: '#heritagebrand', count: 89 },
            { hashtag: '#streetwear', count: 76 },
            { hashtag: '#authentic', count: 65 },
            { hashtag: '#culture', count: 54 },
            { hashtag: '#crooksandcastles', count: 43 }
        ],
        competitive_data: [
            { brand: 'Crooks & Castles', position: 47, category: 'Heritage Streetwear' },
            { brand: 'Supreme', position: 1, category: 'Streetwear Leader' },
            { brand: 'Off-White', position: 3, category: 'Luxury Streetwear' },
            { brand: 'Stussy', position: 12, category: 'Classic Streetwear' }
        ]
    };
    
    updateIntelligenceDisplay(sampleData);
}

function calculateEngagementRate(posts) {
    if (!posts || posts.length === 0) return '4.2';
    
    const totalEngagement = posts.reduce((sum, post) => {
        return sum + (post.likesCount || 0) + (post.commentsCount || 0);
    }, 0);
    
    const totalFollowers = posts.length * 10000; // Estimated followers
    return ((totalEngagement / totalFollowers) * 100).toFixed(1);
}

function updateTopHashtags(hashtags) {
    const container = document.getElementById('top-hashtags');
    if (!container) return;
    
    const hashtagsHtml = hashtags.slice(0, 8).map(tag => 
        `<span style="background: rgba(255, 107, 53, 0.2); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">${tag.hashtag}</span>`
    ).join('');
    
    container.innerHTML = `
        <h4 style="margin-bottom: 0.5rem; color: var(--crooks-accent);">Top Hashtags</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
            ${hashtagsHtml}
        </div>
    `;
}

function updateCompetitiveRankings(rankings) {
    const container = document.getElementById('competitive-rankings');
    if (!container) return;
    
    const rankingsHtml = rankings.slice(0, 4).map(ranking => `
        <div style="background: rgba(26, 26, 26, 0.5); padding: 1rem; border-radius: 8px;">
            <div style="font-weight: 600; color: ${ranking.brand === 'Crooks & Castles' ? 'var(--crooks-primary)' : '#ccc'}; margin-bottom: 0.5rem;">${ranking.brand}</div>
            <div style="font-size: 1.5rem; color: ${ranking.brand === 'Crooks & Castles' ? 'var(--crooks-accent)' : '#999'};">#${ranking.position}</div>
            <div style="font-size: 0.8rem; color: #ccc;">${ranking.category}</div>
        </div>
    `).join('');
    
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            ${rankingsHtml}
        </div>
    `;
}

/* ============================================================================
   ASSET LIBRARY MANAGEMENT
   ============================================================================ */

function loadAssetLibrary() {
    showLoadingState('assets');
    
    fetch(API_ENDPOINTS.assets)
        .then(response => response.json())
        .then(data => {
            assetData = data;
            updateAssetDisplay(data);
            updateElement('header-assets', data.total_count || 18);
            hideLoadingState('assets');
        })
        .catch(error => {
            console.log('Loading sample asset data...');
            loadSampleAssets();
            hideLoadingState('assets');
        });
}

function updateAssetDisplay(data) {
    const assetGrid = document.getElementById('asset-grid');
    if (!assetGrid) return;
    
    assetGrid.innerHTML = '';
    
    if (data.assets) {
        Object.entries(data.assets).forEach(([id, asset]) => {
            const assetItem = createAssetElement(id, asset);
            assetGrid.appendChild(assetItem);
        });
    }
    
    // Add animation to asset items
    animateAssetItems();
}

function createAssetElement(id, asset) {
    const assetItem = document.createElement('div');
    assetItem.className = 'asset-item';
    assetItem.style.opacity = '0';
    assetItem.style.transform = 'translateY(20px)';
    
    const iconClass = getAssetIcon(asset.type);
    const thumbnailSrc = asset.thumbnail_path || '';
    
    assetItem.innerHTML = `
        <div class="asset-thumbnail" style="background-image: url('${thumbnailSrc}'); background-size: cover; background-position: center;">
            ${!thumbnailSrc ? `<i class="fas fa-${iconClass}"></i>` : ''}
        </div>
        <div class="asset-name">${asset.filename}</div>
        <div class="asset-type">${asset.type.replace('_', ' ')}</div>
        <div class="asset-size" style="font-size: 0.7rem; color: #999; margin-bottom: 0.5rem;">${formatFileSize(asset.size || 0)}</div>
        <button class="download-btn" onclick="downloadAsset('${id}')">
            <i class="fas fa-download"></i> Download
        </button>
    `;
    
    return assetItem;
}

function loadSampleAssets() {
    const sampleAssets = {
        total_count: 18,
        categories: {
            social_content: 10,
            video_content: 2,
            intelligence_data: 3,
            documents: 3
        },
        assets: {
            '1': { filename: 'hispanic_heritage_launch.png', type: 'social_content', size: 1487981 },
            '2': { filename: 'cultural_fusion.png', type: 'social_content', size: 1843097 },
            '3': { filename: 'rebel_rooftop_story.png', type: 'social_content', size: 1985429 },
            '4': { filename: 'wordmark_story.png', type: 'social_content', size: 20067 },
            '5': { filename: 'model1_story.png', type: 'social_content', size: 1246706 },
            '6': { filename: 'model2_story.png', type: 'social_content', size: 1497912 },
            '7': { filename: 'medusa_story.png', type: 'social_content', size: 78263 },
            '8': { filename: 'castle_story.png', type: 'social_content', size: 17564 },
            '9': { filename: 'hiphop_anniversary.png', type: 'social_content', size: 1362765 },
            '10': { filename: 'brand_video.mp4', type: 'video_content', size: 6359882 },
            '11': { filename: 'campaign_video.mov', type: 'video_content', size: 4090068 },
            '12': { filename: 'instagram_data.jsonl', type: 'intelligence_data', size: 349184 },
            '13': { filename: 'tiktok_data.jsonl', type: 'intelligence_data', size: 13765 },
            '14': { filename: 'competitive_data.jsonl', type: 'intelligence_data', size: 22959804 },
            '15': { filename: 'brand_guidelines.pdf', type: 'documents', size: 2048000 },
            '16': { filename: 'campaign_brief.docx', type: 'documents', size: 1024000 },
            '17': { filename: 'style_guide.pdf', type: 'documents', size: 3072000 },
            '18': { filename: 'asset_inventory.xlsx', type: 'documents', size: 512000 }
        }
    };
    
    updateAssetDisplay(sampleAssets);
    updateElement('header-assets', sampleAssets.total_count);
}

function animateAssetItems() {
    const assetItems = document.querySelectorAll('.asset-item');
    assetItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function getAssetIcon(type) {
    const iconMap = {
        'social_content': 'image',
        'video_content': 'video',
        'intelligence_data': 'chart-bar',
        'documents': 'file-alt'
    };
    return iconMap[type] || 'file';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function downloadAsset(assetId) {
    // Show download animation
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
    button.disabled = true;
    
    // Simulate download or make actual API call
    setTimeout(() => {
        window.open(`/api/assets/${assetId}/download`, '_blank');
        button.innerHTML = originalText;
        button.disabled = false;
    }, 1000);
}

/* ============================================================================
   CALENDAR MANAGEMENT
   ============================================================================ */

function showCalendarView(view) {
    currentCalendarView = view;
    
    // Update calendar view tabs
    const calendarTabs = document.querySelector('#calendar .tabs');
    if (calendarTabs) {
        calendarTabs.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.target.classList.add('active');
    }
    
    // Load calendar data for the selected view
    loadCalendarData(view);
}

function loadCalendarData(view) {
    showLoadingState('calendar');
    
    fetch(API_ENDPOINTS.calendar)
        .then(response => response.json())
        .then(data => {
            calendarData = data;
            updateCalendarDisplay(data, view);
            updateElement('header-events', data.all_events?.length || 12);
            hideLoadingState('calendar');
        })
        .catch(error => {
            console.log('Loading sample calendar data...');
            loadSampleCalendar(view);
            hideLoadingState('calendar');
        });
}

function updateCalendarDisplay(data, view) {
    const calendarContent = document.getElementById('calendar-content');
    if (!calendarContent) return;
    
    calendarContent.innerHTML = '';
    
    let events = [];
    const viewMap = {
        '7day': '7_day_view',
        '30day': '30_day_view',
        '60day': '60_day_view',
        '90day': '90_day_view'
    };
    
    events = data[viewMap[view]] || [];
    
    events.forEach((event, index) => {
        const eventElement = createCalendarEventElement(event, index);
        calendarContent.appendChild(eventElement);
    });
    
    // Add animation to calendar events
    animateCalendarEvents();
}

function createCalendarEventElement(event, index) {
    const eventElement = document.createElement('div');
    eventElement.className = 'calendar-event';
    eventElement.style.opacity = '0';
    eventElement.style.transform = 'translateX(-20px)';
    
    const priorityColor = getPriorityColor(event.priority);
    const categoryIcon = getCategoryIcon(event.category);
    
    eventElement.innerHTML = `
        <div class="event-date">
            <i class="fas fa-calendar-day"></i> ${formatDate(event.date)}
        </div>
        <div class="event-title" style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${categoryIcon}" style="color: ${priorityColor};"></i>
            ${event.title}
        </div>
        <div class="event-description">${event.description}</div>
        <div class="event-details" style="margin-top: 1rem;">
            <div class="event-budget">💰 Budget: $${event.budget_allocation?.toLocaleString() || 0}</div>
            ${event.assets_required ? `<div style="margin-top: 0.5rem; font-size: 0.8rem; color: #ccc;">📁 Assets Required: ${event.assets_required.length}</div>` : ''}
            ${event.deliverables ? `<div style="margin-top: 0.5rem; font-size: 0.8rem; color: #ccc;">📋 Deliverables: ${event.deliverables.length}</div>` : ''}
        </div>
    `;
    
    return eventElement;
}

function loadSampleCalendar(view) {
    const sampleEvents = {
        '7_day_view': [
            {
                date: '2025-09-23',
                title: 'Hip-Hop Heritage Story Series Launch',
                description: 'Launch authentic hip-hop heritage content series with street photography and cultural elements',
                category: 'cultural',
                priority: 'high',
                budget_allocation: 500,
                assets_required: [
                    { type: 'hero_image', status: 'available' },
                    { type: 'story_template', status: 'available' }
                ],
                deliverables: ['Instagram post', 'Instagram story', 'TikTok video']
            },
            {
                date: '2025-09-25',
                title: 'Cultural Fusion Content Drop',
                description: 'Showcase cultural fusion in streetwear with diverse models and lifestyle context',
                category: 'cultural',
                priority: 'high',
                budget_allocation: 750,
                assets_required: [
                    { type: 'lifestyle_image', status: 'available' },
                    { type: 'carousel_images', status: 'available' }
                ],
                deliverables: ['Instagram carousel', 'Story series', 'TikTok trend']
            },
            {
                date: '2025-09-27',
                title: 'Weekly Intelligence Recap',
                description: 'Weekly competitive intelligence and trend analysis report',
                category: 'intelligence',
                priority: 'medium',
                budget_allocation: 300,
                deliverables: ['Weekly report', 'Dashboard update', 'Trend briefing']
            }
        ],
        '30_day_view': [
            {
                date: '2025-10-01',
                title: 'Hispanic Heritage Month Celebration',
                description: 'Authentic celebration of Hispanic heritage in streetwear with community focus',
                category: 'cultural',
                priority: 'high',
                budget_allocation: 2000,
                assets_required: [
                    { type: 'campaign_hero', status: 'available' },
                    { type: 'story_series', status: 'available' },
                    { type: 'community_video', status: 'available' }
                ],
                deliverables: ['Campaign launch', 'Educational content', 'Community spotlights']
            },
            {
                date: '2025-10-12',
                title: 'Hip-Hop Anniversary Tribute',
                description: 'Tribute to hip-hop anniversary with brand heritage and documentary style',
                category: 'cultural',
                priority: 'high',
                budget_allocation: 1500,
                deliverables: ['Anniversary post', 'Story timeline', 'Long-form video']
            }
        ],
        '60_day_view': [
            {
                date: '2025-11-07',
                title: 'Black Friday Campaign Launch',
                description: 'Strategic BFCM campaign with cultural authenticity and conversion optimization',
                category: 'commercial',
                priority: 'high',
                budget_allocation: 5000,
                deliverables: ['Campaign creative suite', 'Email templates', 'Social ads']
            },
            {
                date: '2025-11-12',
                title: 'Holiday Gift Guide Campaign',
                description: 'Curated gift guide for streetwear enthusiasts with editorial design',
                category: 'seasonal',
                priority: 'high',
                budget_allocation: 2500,
                deliverables: ['Digital gift guide', 'Social carousel', 'Email campaign']
            }
        ],
        '90_day_view': [
            {
                date: '2025-12-07',
                title: 'Q1 2026 Brand Evolution Campaign',
                description: 'Strategic brand evolution for new year positioning with manifesto content',
                category: 'brand',
                priority: 'high',
                budget_allocation: 8000,
                deliverables: ['Brand film', 'Manifesto content', 'PR package']
            },
            {
                date: '2025-12-17',
                title: 'Spring 2026 Collection Teasers',
                description: 'Strategic teasers for upcoming spring collection with mysterious reveals',
                category: 'product',
                priority: 'medium',
                budget_allocation: 1500,
                deliverables: ['Teaser posts', 'BTS content', 'VIP email']
            }
        ],
        'all_events': []
    };
    
    // Combine all events for total count
    sampleEvents.all_events = [
        ...sampleEvents['7_day_view'],
        ...sampleEvents['30_day_view'],
        ...sampleEvents['60_day_view'],
        ...sampleEvents['90_day_view']
    ];
    
    updateCalendarDisplay(sampleEvents, view);
    updateElement('header-events', sampleEvents.all_events.length);
}

function animateCalendarEvents() {
    const calendarEvents = document.querySelectorAll('.calendar-event');
    calendarEvents.forEach((event, index) => {
        setTimeout(() => {
            event.style.transition = 'all 0.5s ease';
            event.style.opacity = '1';
            event.style.transform = 'translateX(0)';
        }, index * 150);
    });
}

function getPriorityColor(priority) {
    const colors = {
        'high': 'var(--crooks-danger)',
        'medium': 'var(--crooks-warning)',
        'low': 'var(--crooks-success)'
    };
    return colors[priority] || 'var(--crooks-primary)';
}

function getCategoryIcon(category) {
    const icons = {
        'cultural': 'users',
        'commercial': 'shopping-cart',
        'seasonal': 'snowflake',
        'brand': 'crown',
        'product': 'box',
        'intelligence': 'chart-line'
    };
    return icons[category] || 'calendar';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/* ============================================================================
   AGENCY TRACKING
   ============================================================================ */

function loadAgencyData() {
    showLoadingState('agency');
    
    fetch(API_ENDPOINTS.agency)
        .then(response => response.json())
        .then(data => {
            agencyData = data;
            updateAgencyDisplay(data);
            hideLoadingState('agency');
        })
        .catch(error => {
            console.log('Loading sample agency data...');
            loadSampleAgencyData();
            hideLoadingState('agency');
        });
}

function updateAgencyDisplay(data) {
    // Agency display is mostly static in the HTML
    // This function can be expanded for dynamic agency data
    console.log('Agency data loaded:', data);
}

function loadSampleAgencyData() {
    const sampleData = {
        agencies: [
            {
                name: 'High Voltage Digital',
                phase: 1,
                deliverables: 4,
                budget: 4000,
                onTimeDelivery: 100,
                qualityScore: 95
            }
        ]
    };
    
    updateAgencyDisplay(sampleData);
}

/* ============================================================================
   FILE UPLOAD FUNCTIONALITY
   ============================================================================ */

function setupDragAndDrop(uploadArea) {
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.style.background = 'rgba(255, 107, 53, 0.2)';
    event.currentTarget.style.borderColor = 'var(--crooks-accent)';
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.style.background = 'rgba(255, 107, 53, 0.05)';
    event.currentTarget.style.borderColor = 'var(--crooks-primary)';
}

function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        uploadFiles(files);
    }
    handleDragLeave(event);
}

function handleFileUpload(input) {
    const files = input.files;
    if (files.length > 0) {
        uploadFiles(files);
    }
}

function uploadFiles(files) {
    Array.from(files).forEach(file => {
        if (file.name.endsWith('.jsonl') || file.name.endsWith('.json')) {
            uploadSingleFile(file);
        } else {
            showNotification('Please upload only JSONL or JSON files', 'warning');
        }
    });
}

function uploadSingleFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show upload progress
    showNotification(`Uploading ${file.name}...`, 'info');
    
    fetch(API_ENDPOINTS.upload, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showNotification(`${file.name} uploaded successfully!`, 'success');
        // Refresh intelligence data
        loadIntelligenceData();
        loadAssetLibrary();
    })
    .catch(error => {
        showNotification(`Upload failed: ${error.message}`, 'error');
    });
}

/* ============================================================================
   UTILITY FUNCTIONS
   ============================================================================ */

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function showLoadingState(section) {
    const content = document.getElementById(section);
    if (content) {
        content.style.opacity = '0.5';
        content.style.pointerEvents = 'none';
    }
}

function hideLoadingState(section) {
    const content = document.getElementById(section);
    if (content) {
        content.style.opacity = '1';
        content.style.pointerEvents = 'auto';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--crooks-${type === 'error' ? 'danger' : type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'primary'});
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: var(--crooks-shadow-lg);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

function handleKeyboardShortcuts(event) {
    // Ctrl/Cmd + number keys for tab switching
    if ((event.ctrlKey || event.metaKey) && event.key >= '1' && event.key <= '5') {
        event.preventDefault();
        const tabs = ['intelligence', 'assets', 'calendar', 'agency', 'upload'];
        const tabIndex = parseInt(event.key) - 1;
        if (tabs[tabIndex]) {
            showTab(tabs[tabIndex]);
        }
    }
}

function handleWindowResize() {
    // Handle responsive behavior
    const width = window.innerWidth;
    const headerStats = document.querySelector('.header-stats');
    
    if (width < 768 && headerStats) {
        headerStats.style.display = 'none';
    } else if (headerStats) {
        headerStats.style.display = 'flex';
    }
}

function initializeTooltips() {
    // Add tooltips to interactive elements
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: var(--crooks-dark);
        color: var(--crooks-light);
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        z-index: 10000;
        pointer-events: none;
        box-shadow: var(--crooks-shadow-md);
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
    
    event.target._tooltip = tooltip;
}

function hideTooltip(event) {
    if (event.target._tooltip) {
        document.body.removeChild(event.target._tooltip);
        delete event.target._tooltip;
    }
}

function initializeAnimations() {
    // Add intersection observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
            }
        });
    });
    
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
}

function setupDataRefresh() {
    // Refresh data every 5 minutes
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            loadTabData(currentTab);
        }
    }, 300000); // 5 minutes
}

/* ============================================================================
   EXPORT FUNCTIONS (for global access)
   ============================================================================ */

// Make functions globally available
window.showTab = showTab;
window.showCalendarView = showCalendarView;
window.downloadAsset = downloadAsset;
window.handleFileUpload = handleFileUpload;
