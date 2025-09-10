// KyndVibes Command Center - Working JavaScript

// Global variables
let currentCalendarPeriod = 'next_30_days';
let uploadInProgress = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎉 KyndVibes Command Center Initializing...');
    
    // Initialize all components
    initializeEventListeners();
    loadInitialData();
    setupFileUpload();
    startHealthMonitoring();
    
    console.log('✨ Command Center Ready - High Frequency Activated!');
});

// Initialize event listeners
function initializeEventListeners() {
    // Calendar period selector
    const periodSelector = document.getElementById('calendar-period');
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            currentCalendarPeriod = this.value;
            loadCalendar();
        });
    }
    
    // File input change
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Upload area drag and drop
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput?.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }
}

// Load initial data
function loadInitialData() {
    loadCalendar();
    loadAssets();
    loadDeliverables();
    checkHealth();
}

// Calendar Functions
async function loadCalendar() {
    const calendarContent = document.getElementById('calendar-content');
    if (!calendarContent) return;
    
    try {
        showLoading(calendarContent, 'Loading calendar events...');
        
        const response = await fetch(`/api/calendar?period=${currentCalendarPeriod}`);
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayCalendarEvents(data.events || []);
            showToast('Calendar loaded successfully', 'success');
        } else {
            throw new Error(data.error || 'Failed to load calendar');
        }
    } catch (error) {
        console.error('Calendar error:', error);
        showError(calendarContent, 'Failed to load calendar events');
        showToast('Failed to load calendar', 'error');
    }
}

function displayCalendarEvents(events) {
    const calendarContent = document.getElementById('calendar-content');
    if (!calendarContent) return;
    
    if (events.length === 0) {
        calendarContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-calendar-plus"></i>
                <h4>No events scheduled</h4>
                <p>Your calendar is clear for this period</p>
            </div>
        `;
        return;
    }
    
    const eventsHTML = events.map(event => `
        <div class="event-item">
            <div class="event-title">${escapeHtml(event.title)}</div>
            <div class="event-description">${escapeHtml(event.description || '')}</div>
            <div class="event-meta">
                <span class="event-date">${formatDate(event.start_date)}</span>
                <span class="event-priority priority-${event.priority || 'medium'}">${event.priority || 'medium'}</span>
            </div>
        </div>
    `).join('');
    
    calendarContent.innerHTML = eventsHTML;
}

// Assets Functions
async function loadAssets() {
    const assetsContent = document.getElementById('assets-content');
    if (!assetsContent) return;
    
    try {
        showLoading(assetsContent, 'Loading brand assets...');
        
        const response = await fetch('/api/assets');
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayAssets(data.assets || []);
            showToast('Assets loaded successfully', 'success');
        } else {
            throw new Error(data.error || 'Failed to load assets');
        }
    } catch (error) {
        console.error('Assets error:', error);
        showError(assetsContent, 'Failed to load brand assets');
        showToast('Failed to load assets', 'error');
    }
}

function displayAssets(assets) {
    const assetsContent = document.getElementById('assets-content');
    if (!assetsContent) return;
    
    if (assets.length === 0) {
        assetsContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-images"></i>
                <h4>No assets found</h4>
                <p>Upload your first brand asset to get started</p>
            </div>
        `;
        return;
    }
    
    const assetsHTML = assets.map(asset => `
        <div class="asset-item" onclick="viewAsset('${asset.url}', '${asset.name}')">
            <div class="asset-icon">
                <i class="fas ${getAssetIcon(asset.type)}"></i>
            </div>
            <div class="asset-info">
                <div class="asset-name">${escapeHtml(asset.name)}</div>
                <div class="asset-meta">${asset.type} • ${asset.file_size} • ${formatDate(asset.created_date)}</div>
            </div>
        </div>
    `).join('');
    
    assetsContent.innerHTML = assetsHTML;
}

function getAssetIcon(type) {
    const icons = {
        'image': 'fa-image',
        'document': 'fa-file-pdf',
        'video': 'fa-video',
        'brand_guide': 'fa-palette',
        'logo': 'fa-star',
        'brand_element': 'fa-magic'
    };
    return icons[type] || 'fa-file';
}

function viewAsset(url, name) {
    if (url && url !== '#') {
        window.open(url, '_blank');
        showToast(`Opening: ${name}`, 'info');
    } else {
        showToast(`${name} - Preview coming soon`, 'info');
    }
}

// Deliverables Functions
async function loadDeliverables() {
    const deliverablesContent = document.getElementById('deliverables-content');
    if (!deliverablesContent) return;
    
    try {
        showLoading(deliverablesContent, 'Loading deliverables...');
        
        const response = await fetch('/api/deliverables');
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayDeliverables(data.deliverables || []);
            showToast('Deliverables loaded successfully', 'success');
        } else {
            throw new Error(data.error || 'Failed to load deliverables');
        }
    } catch (error) {
        console.error('Deliverables error:', error);
        showError(deliverablesContent, 'Failed to load deliverables');
        showToast('Failed to load deliverables', 'error');
    }
}

function displayDeliverables(deliverables) {
    const deliverablesContent = document.getElementById('deliverables-content');
    if (!deliverablesContent) return;
    
    if (deliverables.length === 0) {
        deliverablesContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-tasks"></i>
                <h4>No deliverables</h4>
                <p>All caught up! No pending deliverables</p>
            </div>
        `;
        return;
    }
    
    const deliverablesHTML = deliverables.map(deliverable => `
        <div class="deliverable-item">
            <div class="deliverable-title">${escapeHtml(deliverable.title)}</div>
            <div class="deliverable-description">${escapeHtml(deliverable.description || '')}</div>
            <div class="deliverable-meta">
                <span class="deliverable-due">Due: ${formatDate(deliverable.due_date)}</span>
                <span class="deliverable-status status-${deliverable.status.replace('_', '-')}">${deliverable.status.replace('_', ' ')}</span>
            </div>
        </div>
    `).join('');
    
    deliverablesContent.innerHTML = deliverablesHTML;
}

// File Upload Functions
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    if (!uploadArea || !fileInput) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    const uploadArea = document.getElementById('upload-area');
    uploadArea?.classList.add('dragover');
}

function handleDragLeave(e) {
    const uploadArea = document.getElementById('upload-area');
    uploadArea?.classList.remove('dragover');
}

function handleDrop(e) {
    const uploadArea = document.getElementById('upload-area');
    uploadArea?.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

async function handleFiles(files) {
    if (uploadInProgress) {
        showToast('Upload already in progress', 'warning');
        return;
    }
    
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'video/mp4', 'video/quicktime'];
    
    for (let file of files) {
        if (file.size > maxSize) {
            showToast(`File ${file.name} is too large (max 16MB)`, 'error');
            continue;
        }
        
        if (!allowedTypes.includes(file.type)) {
            showToast(`File type ${file.type} not supported`, 'error');
            continue;
        }
        
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    uploadInProgress = true;
    
    const progressContainer = document.getElementById('upload-progress');
    const progressFill = progressContainer?.querySelector('.progress-fill');
    const progressText = progressContainer?.querySelector('.progress-text');
    
    try {
        // Show progress
        progressContainer?.classList.remove('hidden');
        if (progressText) progressText.textContent = `Uploading ${file.name}...`;
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('campaign_tags', '');
        formData.append('asset_type', 'general');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showToast(`Successfully uploaded ${file.name}`, 'success');
            loadAssets(); // Refresh assets list
        } else {
            throw new Error(result.error || 'Upload failed');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showToast(`Failed to upload ${file.name}: ${error.message}`, 'error');
    } finally {
        uploadInProgress = false;
        progressContainer?.classList.add('hidden');
        if (progressFill) progressFill.style.width = '0%';
    }
}

// Health Check Functions
async function checkHealth() {
    const apiStatus = document.getElementById('api-status');
    const lastUpdated = document.getElementById('last-updated');
    
    try {
        const response = await fetch('/healthz');
        const data = await response.json();
        
        if (response.ok && data.status === 'healthy') {
            if (apiStatus) apiStatus.textContent = 'Healthy ✅';
            if (lastUpdated) lastUpdated.textContent = formatTime(new Date());
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        console.error('Health check error:', error);
        if (apiStatus) apiStatus.textContent = 'Unhealthy ❌';
        if (lastUpdated) lastUpdated.textContent = formatTime(new Date());
    }
}

function startHealthMonitoring() {
    // Check health every 5 minutes
    setInterval(checkHealth, 5 * 60 * 1000);
}

// Quick Action Functions
async function refreshAssets() {
    loadAssets();
    showToast('Refreshing assets...', 'info');
}

async function refreshDeliverables() {
    loadDeliverables();
    showToast('Refreshing deliverables...', 'info');
}

async function exportData() {
    try {
        showToast('Exporting data...', 'info');
        const response = await fetch('/api/export');
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Create downloadable JSON file
            const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `kyndvibes-export-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showToast('Data exported successfully!', 'success');
        } else {
            throw new Error(data.error || 'Export failed');
        }
    } catch (error) {
        console.error('Export error:', error);
        showToast('Export failed: ' + error.message, 'error');
    }
}

async function viewBrandGuide() {
    try {
        showToast('Opening KyndVibes Brand Guide...', 'info');
        
        // Create comprehensive brand guide modal
        const brandGuideContent = `
🌈 **KYND VIBES: HIGH FREQUENCY APPAREL**
Complete Brand Guide for Content + Asset Creation

**🎯 BRAND ESSENCE**
• **Tagline:** Amazing, Not Surprising
• **Core Promise:** Apparel infused with gratitude, energy, and protection — designed to lift frequency and connect communities
• **Archetype:** The Connector × Rebel. Inspires belonging while breaking the mold
• **Tone:** Uplifting, honest, magnetic, slightly irreverent (never preachy), rooted in shared moments

**⚡ BRAND CODES (Non-Negotiables)**
• **Gratitude** - Hidden notes, inner labels, surprise-and-delight
• **Energy** - Bright color pops, movement in design & media
• **Protection** - Talisman symbols, community codes, limited access layers
• **Love** - Affirmations, collectivity, "The Universe Provides"
• **Signal** - Bold phrases, embroidery, digital frequency through UGC

**🎨 VISUAL IDENTITY**
**Colors (SU26 Core Palette):**
• Lavender (#D5BDE4) • Powder Blue (#ACC9E0) • Butter Yellow (#F6E587)
• Mint Green (#BFD7B2) • Bright Pink (#F99ACB) • Washed Black (#464647)
• Oatmeal Heather (#D8CBB3) • Bright White (#FFFFFF)

**Typography:**
• Primary: Sans-serif modern (Inter) for clarity
• Secondary: Soft serif for campaign headlines (emotive, feminine edge)

**Logos & Graphics:**
• Kynd Vibes wordmark = clean, minimal
• Signature embroidery phrases = puffed / full-color 3D
• Secondary icons = talismans, cosmic symbols, subtle line art

**👕 PRODUCT DNA**
**Signature Silhouettes:**
Radiate Tee • Bloom Tee • Cozy Crew • Vibe Hoodie • Ease Short • Flow Pant • Energy Jogger

**Hidden Details:**
• Embroidered mantras inside sleeves/waistbands ("amazing not surprising")
• Gratitude notes printed in labels
• Energy transmission through fabric feel (soft, sustainable, lived-in hand feel)

**📱 CONTENT GUIDELINES**
**Pillars:**
• **Fit & Frequency** — Show product in motion, everyday energy
• **Signals in the Wild** — Members wearing phrases (UGC, campus, festivals)
• **Inner Beauty** — Spotlight hidden notes & embroidery details
• **Collective Stories** — Ambassadors sharing gratitude, rituals, surprise drops
• **Cultural Calendar** — Align with rush week, finals, concerts, game days

**Aesthetic:**
• Natural light, no heavy filters
• Environments: dorm rooms, quads, rooftops, concerts, coffee shops
• Visual vibe: polished candids — looks like UGC but elevated

**📊 SOCIAL MEDIA TOOLKIT**
• **Hashtags:** #KyndVibes #FrequencyCollective #TuneIntoFrequency
• **Posting Rituals:** Gratitude chains, frequency fit checks, collective takeover days
• **Formats:** TikTok/IG Reels = micro-moments, Static IG = affirmations + detail shots

**✅ DO'S & DON'TS**
**✅ DO:** Emphasize energy, gratitude, collectivity • Show diverse, real students • Highlight inner beauty
**❌ DON'T:** Over-style or make it feel like a photo shoot • Use heavy filters • Corporate tone

**📈 NORTH STAR METRICS**
• UGC participation (# posts tagged per week)
• Collective growth (# campuses activated)
• Engagement rate on "signal" content (shares/saves > likes)
• Surprise & Delight ROI (tracking surprise drops → sales lift)
        `;
        
        // Create sophisticated brand guide modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 800px; max-height: 90vh;">
                <div class="modal-header">
                    <h3><i class="fas fa-book"></i> KyndVibes Brand Guide</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="padding: 24px; white-space: pre-line; font-family: 'Inter', sans-serif; line-height: 1.6; color: #333; overflow-y: auto; max-height: 60vh;">
                    ${brandGuideContent}
                </div>
                <div class="form-actions" style="border-top: 1px solid #f0f0f0; margin-top: 24px; padding: 24px; display: flex; gap: 12px; justify-content: space-between;">
                    <div style="display: flex; gap: 12px;">
                        <button class="btn btn-primary" onclick="downloadBrandGuide()">
                            <i class="fas fa-download"></i> Download Guide
                        </button>
                        <button class="btn btn-secondary" onclick="window.open('/complete_palette/kyndvibes_brand_standard_palette.jpg', '_blank')">
                            <i class="fas fa-palette"></i> View Color Palette
                        </button>
                    </div>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                        Close Guide
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        showToast('Brand Guide opened! ✨', 'success');
        
    } catch (error) {
        console.error('Brand guide error:', error);
        showToast('Brand guide temporarily unavailable', 'warning');
    }
}

function downloadBrandGuide() {
    const brandGuideData = {
        "brand_name": "KyndVibes",
        "tagline": "Amazing, Not Surprising",
        "positioning": "High Frequency Apparel",
        "brand_essence": {
            "core_promise": "Apparel infused with gratitude, energy, and protection — designed to lift frequency and connect communities",
            "archetype": "The Connector × Rebel. Inspires belonging while breaking the mold",
            "tone_of_voice": "Uplifting, honest, magnetic, slightly irreverent (never preachy), rooted in shared moments"
        },
        "brand_codes": {
            "gratitude": "Hidden notes, inner labels, surprise-and-delight",
            "energy": "Bright color pops, movement in design & media", 
            "protection": "Talisman symbols, community codes, limited access layers",
            "love": "Affirmations, collectivity, 'The Universe Provides'",
            "signal": "Bold phrases, embroidery, digital frequency through UGC"
        },
        "visual_identity": {
            "su26_core_palette": {
                "lavender": "#D5BDE4",
                "powder_blue": "#ACC9E0", 
                "butter_yellow": "#F6E587",
                "mint_green": "#BFD7B2",
                "bright_pink": "#F99ACB",
                "washed_black": "#464647",
                "oatmeal_heather": "#D8CBB3",
                "bright_white": "#FFFFFF"
            },
            "typography": {
                "primary": "Sans-serif modern (Inter) for clarity",
                "secondary": "Soft serif for campaign headlines (emotive, feminine edge)"
            },
            "logos_graphics": {
                "wordmark": "Kynd Vibes wordmark = clean, minimal",
                "embroidery": "Signature embroidery phrases = puffed / full-color 3D",
                "icons": "Secondary icons = talismans, cosmic symbols, subtle line art"
            }
        },
        "product_dna": {
            "signature_silhouettes": ["Radiate Tee", "Bloom Tee", "Cozy Crew", "Vibe Hoodie", "Ease Short", "Flow Pant", "Energy Jogger"],
            "hidden_details": [
                "Embroidered mantras inside sleeves/waistbands ('amazing not surprising')",
                "Gratitude notes printed in labels",
                "Energy transmission through fabric feel (soft, sustainable, lived-in hand feel)"
            ]
        },
        "content_guidelines": {
            "pillars": [
                "Fit & Frequency — Show product in motion, everyday energy",
                "Signals in the Wild — Members wearing phrases (UGC, campus, festivals)",
                "Inner Beauty — Spotlight hidden notes & embroidery details",
                "Collective Stories — Ambassadors sharing gratitude, rituals, surprise drops",
                "Cultural Calendar — Align with rush week, finals, concerts, game days"
            ],
            "aesthetic": {
                "lighting": "Natural light, no heavy filters",
                "environments": "dorm rooms, quads, rooftops, concerts, coffee shops",
                "visual_vibe": "polished candids — looks like UGC but elevated"
            }
        },
        "social_media_toolkit": {
            "hashtags": ["#KyndVibes", "#FrequencyCollective", "#TuneIntoFrequency"],
            "posting_rituals": ["Gratitude chains", "frequency fit checks", "collective takeover days"],
            "formats": {
                "tiktok_ig_reels": "micro-moments (try-ons, campus hacks, 'signal spotted')",
                "static_ig": "affirmations + detail shots",
                "ugc_reposts": "anchor community"
            }
        },
        "dos_and_donts": {
            "do": [
                "Emphasize energy, gratitude, collectivity",
                "Show diverse, real students", 
                "Highlight inner beauty (hidden notes, embroidery, details)"
            ],
            "dont": [
                "Over-style or make it feel like a photo shoot",
                "Use heavy filters, staged backdrops, or corporate tone"
            ]
        },
        "north_star_metrics": [
            "UGC participation (# posts tagged per week)",
            "Collective growth (# campuses activated)",
            "Engagement rate on 'signal' content (shares/saves > likes)",
            "Surprise & Delight ROI (tracking surprise drops → sales lift)"
        ]
    };
    
    // Create downloadable file
    const blob = new Blob([JSON.stringify(brandGuideData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'KyndVibes-Complete-Brand-Guide.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Brand Guide downloaded successfully!', 'success');
}

// Add to global functions
window.downloadBrandGuide = downloadBrandGuide;

async function openFrequencyCollective() {
    try {
        showToast('Opening Frequency Collective portal...', 'info');
        
        // Create the sophisticated Frequency Collective portal
        const collectiveInfo = `
🌟 THE FREQUENCY COLLECTIVE 🌟
Frequency Keepers • Energy Transmitters • Cultural Curators

✨ NOT AN APPLICATION — AN INVITATION ✨

The Frequency Collective isn't something you apply for.
You're discovered. You're tuned in. The universe provides.

🎯 WHO WE SCOUT:
• Micro-creators (500-5k followers) with authentic energy
• Student leaders, DJs, athletes, club organizers
• Campus influencers who naturally embody gratitude codes
• Students who post uplifting, stylish, community-driven content

🎁 THE DISCOVERY EXPERIENCE:
Surprise Frequency Packs appear without warning:
• Limited colorway tee/hoodie (Collective-only embroidery)
• Manifestation card with hidden gratitude phrases
• Holographic "Frequency Collective" student ID
• Surprise talisman (crystal, pin, or mystique element)
• QR code linking to private member hub

🌊 ONGOING FREQUENCY DROPS:
• Seasonal exclusive gear in unreleased campus colorways
• Secret "Signal" missions via text/DM
• Priority invites to Kynd activations & pop-ups
• Campus takeover opportunities on brand socials

🎪 FREQUENCY CHALLENGES:
• Post fits with code phrase captions
• Gratitude chains tagging 3 people you're thankful for
• Campus signals documenting random acts of kindness
• Hidden treasure hunts with cryptic clues

💫 OUTER CIRCLE ENGAGEMENT:
Can't wait to be discovered? Start transmitting frequency:
• Post with #TuneIntoFrequency
• Embody the codes: gratitude, energy, protection, love
• Top UGC monthly wins surprise merch & campus shoutouts

🔮 THE MYSTIQUE:
"You've been tuned into The Frequency Collective.
The universe provides."

#FrequencyCollective #AmazingNotSurprising #TheUniverseProvides
        `;
        
        // Create sophisticated portal modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 700px;">
                <div class="modal-header">
                    <h3><i class="fas fa-satellite-dish"></i> The Frequency Collective</h3>
                    <button class="modal-close" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="padding: 24px; white-space: pre-line; font-family: 'Inter', sans-serif; line-height: 1.6; color: #333;">
                    ${collectiveInfo}
                </div>
                <div class="form-actions" style="border-top: 1px solid #f0f0f0; margin-top: 24px; padding: 24px; display: flex; gap: 12px; justify-content: space-between;">
                    <div style="display: flex; gap: 12px;">
                        <button class="btn btn-primary" onclick="window.open('https://instagram.com/kyndvibes', '_blank')">
                            <i class="fab fa-instagram"></i> Start Transmitting
                        </button>
                        <button class="btn btn-secondary" onclick="openScoutingTools()">
                            <i class="fas fa-search"></i> Scouting Tools
                        </button>
                    </div>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                        Close Portal
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        showToast('Frequency Collective portal opened! ✨', 'success');
        
    } catch (error) {
        console.error('Frequency Collective error:', error);
        showToast('Frequency Collective temporarily unavailable', 'warning');
    }
}

// Add scouting tools function
function openScoutingTools() {
    const scoutingModal = document.createElement('div');
    scoutingModal.className = 'modal';
    scoutingModal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-search"></i> Frequency Scouting Tools</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div style="padding: 24px;">
                <h4 style="color: #008B8B; margin-bottom: 16px;">Scout Potential Frequency Keepers</h4>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Campus/University:</label>
                    <input type="text" id="scout-campus" placeholder="e.g., University of California" 
                           style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px;">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Instagram Handle:</label>
                    <input type="text" id="scout-instagram" placeholder="@username" 
                           style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px;">
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Frequency Notes:</label>
                    <textarea id="scout-notes" placeholder="Why they embody the frequency... energy, style, community influence, etc." 
                              style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; min-height: 80px;"></textarea>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 600;">Discovery Method:</label>
                    <select id="scout-method" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px;">
                        <option value="surprise_pack">Surprise Frequency Pack</option>
                        <option value="dm_invitation">DM Invitation</option>
                        <option value="campus_activation">Campus Activation</option>
                        <option value="referral">Member Referral</option>
                    </select>
                </div>
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="addToFrequencyScouts()">
                    <i class="fas fa-plus"></i> Add to Scout List
                </button>
                <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    // Remove existing modals and add new one
    document.querySelectorAll('.modal').forEach(m => m.remove());
    document.body.appendChild(scoutingModal);
}

function addToFrequencyScouts() {
    const campus = document.getElementById('scout-campus').value;
    const instagram = document.getElementById('scout-instagram').value;
    const notes = document.getElementById('scout-notes').value;
    const method = document.getElementById('scout-method').value;
    
    if (!campus || !instagram) {
        showToast('Please fill in campus and Instagram handle', 'warning');
        return;
    }
    
    // In a real implementation, this would save to your database
    showToast(`${instagram} added to Frequency Scout list for ${campus}! 🌟`, 'success');
    
    // Close modal
    document.querySelector('.modal').remove();
}

// Deliverable Management Functions
function showAddDeliverableForm() {
    const modal = document.getElementById('add-deliverable-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Reset form
        document.getElementById('add-deliverable-form').reset();
        // Set default due date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        document.getElementById('deliverable-due-date').value = tomorrow.toISOString().split('T')[0];
    }
}

function hideAddDeliverableForm() {
    const modal = document.getElementById('add-deliverable-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function submitDeliverable(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const deliverableData = {
        title: formData.get('title'),
        description: formData.get('description'),
        due_date: formData.get('due_date'),
        priority: formData.get('priority'),
        assignee: formData.get('assignee') || 'Team',
        status: 'pending',
        created_date: new Date().toISOString().split('T')[0]
    };
    
    try {
        showToast('Creating deliverable...', 'info');
        
        const response = await fetch('/api/deliverables', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(deliverableData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showToast(`Deliverable "${deliverableData.title}" created successfully!`, 'success');
            
            // Hide modal
            hideAddDeliverableForm();
            
            // Refresh deliverables and calendar
            await loadDeliverables();
            await loadCalendarEvents();
            
        } else {
            throw new Error('Failed to create deliverable');
        }
        
    } catch (error) {
        console.error('Error creating deliverable:', error);
        showToast('Failed to create deliverable. Please try again.', 'error');
    }
}

async function refreshDeliverables() {
    showToast('Refreshing deliverables...', 'info');
    await loadDeliverables();
    showToast('Deliverables refreshed!', 'success');
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add deliverable form submission
    const deliverableForm = document.getElementById('add-deliverable-form');
    if (deliverableForm) {
        deliverableForm.addEventListener('submit', submitDeliverable);
    }
    
    // Close modal when clicking outside
    const modal = document.getElementById('add-deliverable-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideAddDeliverableForm();
            }
        });
    }
});

// Add to global functions
window.showAddDeliverableForm = showAddDeliverableForm;
window.hideAddDeliverableForm = hideAddDeliverableForm;
window.submitDeliverable = submitDeliverable;
window.refreshDeliverables = refreshDeliverables;

// UI Helper Functions
function showLoading(container, message = 'Loading...') {
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>${message}</p>
        </div>
    `;
}

function showError(container, message = 'An error occurred') {
    if (!container) return;
    
    container.innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <h4>Error</h4>
            <p>${message}</p>
        </div>
    `;
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.cssText = `
        background: white;
        border-left: 4px solid ${getToastColor(type)};
        padding: 12px 16px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    `;
    
    toast.innerHTML = `
        <i class="fas ${getToastIcon(type)}" style="color: ${getToastColor(type)};"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function getToastIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || 'fa-info-circle';
}

function getToastColor(type) {
    const colors = {
        'success': '#00CED1',
        'error': '#FF1493',
        'warning': '#FFD700',
        'info': '#008B8B'
    };
    return colors[type] || '#008B8B';
}

// Utility Functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(dateString) {
    if (!dateString) return 'No date';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return 'Invalid date';
    }
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Deliverable Creation Functions
function showAddDeliverableForm() {
    const modal = document.getElementById('add-deliverable-modal');
    if (modal) {
        modal.classList.remove('hidden');
        
        // Set default due date to 7 days from now
        const dueDateInput = document.getElementById('deliverable-due-date');
        if (dueDateInput) {
            const defaultDate = new Date();
            defaultDate.setDate(defaultDate.getDate() + 7);
            dueDateInput.value = defaultDate.toISOString().split('T')[0];
        }
        
        // Focus on title field
        const titleInput = document.getElementById('deliverable-title');
        if (titleInput) {
            setTimeout(() => titleInput.focus(), 100);
        }
    }
}

function hideAddDeliverableForm() {
    const modal = document.getElementById('add-deliverable-modal');
    if (modal) {
        modal.classList.add('hidden');
        
        // Reset form
        const form = document.getElementById('add-deliverable-form');
        if (form) {
            form.reset();
        }
    }
}

async function submitDeliverable(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const deliverableData = {
        title: formData.get('title'),
        description: formData.get('description'),
        due_date: formData.get('due_date'),
        priority: formData.get('priority'),
        assignee: formData.get('assignee') || 'Team'
    };
    
    try {
        showToast('Creating deliverable...', 'info');
        
        const response = await fetch('/api/deliverables', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deliverableData)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showToast(`Deliverable "${deliverableData.title}" created successfully!`, 'success');
            hideAddDeliverableForm();
            
            // Refresh both deliverables and calendar
            loadDeliverables();
            loadCalendar();
        } else {
            throw new Error(result.error || 'Failed to create deliverable');
        }
        
    } catch (error) {
        console.error('Create deliverable error:', error);
        showToast(`Failed to create deliverable: ${error.message}`, 'error');
    }
}

// Global functions for onclick handlers
window.loadCalendar = loadCalendar;
window.refreshAssets = refreshAssets;
window.refreshDeliverables = refreshDeliverables;
window.checkHealth = checkHealth;
window.exportData = exportData;
window.viewBrandGuide = viewBrandGuide;
window.openFrequencyCollective = openFrequencyCollective;
window.viewAsset = viewAsset;
window.showAddDeliverableForm = showAddDeliverableForm;
window.hideAddDeliverableForm = hideAddDeliverableForm;
window.submitDeliverable = submitDeliverable;

console.log('🎨 KyndVibes Command Center JavaScript Loaded - Amazing, Not Surprising! ✨');

