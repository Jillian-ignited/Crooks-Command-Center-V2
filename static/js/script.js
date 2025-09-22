// Crooks & Castles Command Center V2 JavaScript

// Global variables
let currentData = {
    instagram: null,
    hashtags: null,
    tiktok: null,
    processed: null
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    // Set initial timestamp
    updateLastUpdated();
    
    // Show dashboard by default
    showSection('dashboard');
    
    // Initialize upload functionality
    setupFileUpload();
}

function setupEventListeners() {
    // Navigation buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            showSection(section);
            
            // Update active state
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Upload area click
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('intelligence-file');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleFileDrop);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    
    // Upload button
    document.getElementById('upload-btn').addEventListener('click', processIntelligenceData);
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Load section-specific data
    switch(sectionId) {
        case 'dashboard':
            refreshDashboard();
            break;
        case 'competitive-intelligence':
            refreshCompetitiveData();
            break;
        case 'cultural-radar':
            refreshCulturalRadar();
            break;
        case 'calendar':
            loadCalendarEvents();
            break;
        case 'assets':
            loadBrandAssets();
            break;
    }
}

// File Upload Functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('intelligence-file');
    
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
    e.preventDefault();
    document.getElementById('upload-area').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    document.getElementById('upload-area').classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    document.getElementById('upload-area').classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.name.endsWith('.jsonl')) {
        showStatusMessage('Please select a JSONL file', 'error');
        return;
    }
    
    // Update UI
    const uploadContent = document.querySelector('.upload-content p');
    uploadContent.innerHTML = `<i class="fas fa-file-alt"></i> ${file.name} selected`;
    
    // Enable upload button
    document.getElementById('upload-btn').disabled = false;
    
    // Store file for processing
    window.selectedFile = file;
}

function processIntelligenceData() {
    if (!window.selectedFile) {
        showStatusMessage('Please select a file first', 'error');
        return;
    }
    
    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    uploadBtn.disabled = true;
    
    // Read and process the JSONL file
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const jsonlContent = e.target.result;
            const processedData = parseJSONL(jsonlContent);
            
            // Determine data type and process accordingly
            const dataType = detectDataType(processedData);
            currentData[dataType] = processedData;
            
            // Process the data
            analyzeIntelligenceData(processedData, dataType);
            
            showStatusMessage(`${dataType.toUpperCase()} data processed successfully!`, 'success');
            
        } catch (error) {
            console.error('Error processing file:', error);
            showStatusMessage('Error processing file. Please check the format.', 'error');
        } finally {
            uploadBtn.innerHTML = '<i class="fas fa-upload"></i> Process Intelligence Data';
            uploadBtn.disabled = false;
        }
    };
    
    reader.readAsText(window.selectedFile);
}

function parseJSONL(content) {
    const lines = content.trim().split('\n');
    return lines.map(line => {
        try {
            return JSON.parse(line);
        } catch (e) {
            console.warn('Skipping invalid JSON line:', line);
            return null;
        }
    }).filter(item => item !== null);
}

function detectDataType(data) {
    if (data.length === 0) return 'unknown';
    
    const sample = data[0];
    
    // Check for TikTok data
    if (sample.videoUrl || sample.musicMeta || sample.hashtags) {
        return 'tiktok';
    }
    
    // Check for Instagram hashtag data
    if (sample.hashtag || (sample.url && sample.url.includes('/explore/tags/'))) {
        return 'hashtags';
    }
    
    // Default to Instagram brand data
    return 'instagram';
}

function analyzeIntelligenceData(data, dataType) {
    let analysis = {};
    
    switch(dataType) {
        case 'instagram':
            analysis = analyzeInstagramData(data);
            break;
        case 'hashtags':
            analysis = analyzeHashtagData(data);
            break;
        case 'tiktok':
            analysis = analyzeTikTokData(data);
            break;
    }
    
    // Update UI with analysis
    updateDashboardMetrics(analysis, dataType);
    updateCompetitiveIntelligence(analysis, dataType);
    updateCulturalRadar(analysis, dataType);
    
    // Store processed analysis
    currentData.processed = {
        ...currentData.processed,
        [dataType]: analysis
    };
}

function analyzeInstagramData(data) {
    const brandMetrics = {};
    const culturalMoments = [];
    
    data.forEach(post => {
        const brand = extractBrandFromPost(post);
        if (!brandMetrics[brand]) {
            brandMetrics[brand] = {
                posts: 0,
                totalLikes: 0,
                totalComments: 0,
                totalEngagement: 0,
                avgEngagement: 0
            };
        }
        
        const likes = post.likesCount || 0;
        const comments = post.commentsCount || 0;
        const engagement = likes + comments;
        
        brandMetrics[brand].posts++;
        brandMetrics[brand].totalLikes += likes;
        brandMetrics[brand].totalComments += comments;
        brandMetrics[brand].totalEngagement += engagement;
        
        // Identify viral content (high engagement)
        if (engagement > 1000) {
            culturalMoments.push({
                brand: brand,
                content: post.caption || 'No caption',
                engagement: engagement,
                url: post.url,
                timestamp: post.timestamp
            });
        }
    });
    
    // Calculate averages and rankings
    Object.keys(brandMetrics).forEach(brand => {
        const metrics = brandMetrics[brand];
        metrics.avgEngagement = Math.round(metrics.totalEngagement / metrics.posts);
    });
    
    const rankings = Object.entries(brandMetrics)
        .sort((a, b) => b[1].avgEngagement - a[1].avgEngagement)
        .map(([brand, metrics], index) => ({
            rank: index + 1,
            brand: brand,
            ...metrics
        }));
    
    return {
        brandMetrics,
        rankings,
        culturalMoments: culturalMoments.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        totalPosts: data.length,
        avgEngagement: Math.round(data.reduce((sum, post) => sum + (post.likesCount || 0) + (post.commentsCount || 0), 0) / data.length)
    };
}

function analyzeHashtagData(data) {
    const hashtagMetrics = {};
    const trendingThemes = [];
    
    data.forEach(post => {
        const hashtag = post.hashtag || extractHashtagFromUrl(post.url);
        if (!hashtagMetrics[hashtag]) {
            hashtagMetrics[hashtag] = {
                posts: 0,
                totalEngagement: 0,
                avgEngagement: 0,
                velocity: 0
            };
        }
        
        const engagement = (post.likesCount || 0) + (post.commentsCount || 0);
        hashtagMetrics[hashtag].posts++;
        hashtagMetrics[hashtag].totalEngagement += engagement;
    });
    
    // Calculate trending themes
    Object.keys(hashtagMetrics).forEach(hashtag => {
        const metrics = hashtagMetrics[hashtag];
        metrics.avgEngagement = Math.round(metrics.totalEngagement / metrics.posts);
        
        // Simple velocity calculation (posts per day estimate)
        metrics.velocity = metrics.posts; // Simplified for demo
        
        if (metrics.posts > 5) {
            trendingThemes.push({
                theme: hashtag,
                posts: metrics.posts,
                engagement: metrics.avgEngagement,
                velocity: metrics.velocity
            });
        }
    });
    
    return {
        hashtagMetrics,
        trendingThemes: trendingThemes.sort((a, b) => b.velocity - a.velocity).slice(0, 10),
        totalHashtagPosts: data.length
    };
}

function analyzeTikTokData(data) {
    const culturalInsights = [];
    const viralPatterns = [];
    const soundTrends = [];
    
    data.forEach(video => {
        const engagement = (video.diggCount || 0) + (video.shareCount || 0) + (video.commentCount || 0);
        
        // Identify viral content
        if (engagement > 10000) {
            culturalInsights.push({
                description: video.text || 'No description',
                engagement: engagement,
                author: video.authorMeta?.nickName || 'Unknown',
                sound: video.musicMeta?.musicName || 'Original sound',
                hashtags: video.hashtags || []
            });
        }
        
        // Track sound trends
        if (video.musicMeta?.musicName) {
            const existingSound = soundTrends.find(s => s.name === video.musicMeta.musicName);
            if (existingSound) {
                existingSound.usage++;
                existingSound.totalEngagement += engagement;
            } else {
                soundTrends.push({
                    name: video.musicMeta.musicName,
                    usage: 1,
                    totalEngagement: engagement
                });
            }
        }
    });
    
    return {
        culturalInsights: culturalInsights.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        viralPatterns: viralPatterns,
        soundTrends: soundTrends.sort((a, b) => b.usage - a.usage).slice(0, 5),
        totalVideos: data.length,
        avgEngagement: Math.round(data.reduce((sum, video) => sum + ((video.diggCount || 0) + (video.shareCount || 0) + (video.commentCount || 0)), 0) / data.length)
    };
}

// UI Update Functions
function updateDashboardMetrics(analysis, dataType) {
    if (dataType === 'instagram' && analysis.rankings) {
        const crooksRank = analysis.rankings.find(r => r.brand.toLowerCase().includes('crooks'));
        if (crooksRank) {
            document.getElementById('competitive-rank').textContent = `#${crooksRank.rank}/12`;
            document.getElementById('avg-engagement').textContent = crooksRank.avgEngagement.toLocaleString();
            document.getElementById('posts-count').textContent = crooksRank.posts;
            document.getElementById('engagement-rate').textContent = `${((crooksRank.avgEngagement / 1000) * 100).toFixed(1)}%`;
        }
    }
    
    if (analysis.culturalMoments || analysis.culturalInsights) {
        const moments = analysis.culturalMoments || analysis.culturalInsights || [];
        document.getElementById('cultural-moments-count').textContent = moments.length;
    }
    
    if (analysis.trendingThemes) {
        document.getElementById('trending-themes').textContent = analysis.trendingThemes.length;
    }
    
    if (dataType === 'tiktok') {
        document.getElementById('tiktok-insights').textContent = `${analysis.totalVideos} videos analyzed`;
    }
}

function updateCompetitiveIntelligence(analysis, dataType) {
    if (dataType === 'instagram' && analysis.rankings) {
        updateBrandRankings(analysis.rankings);
        updateCulturalMoments(analysis.culturalMoments);
        updateMetricsTable(analysis.rankings);
    }
}

function updateBrandRankings(rankings) {
    const container = document.getElementById('brand-rankings');
    container.innerHTML = '';
    
    rankings.forEach(ranking => {
        const rankingItem = document.createElement('div');
        rankingItem.className = 'ranking-item';
        rankingItem.innerHTML = `
            <div class="ranking-position">${ranking.rank}</div>
            <div>
                <div class="ranking-brand">${ranking.brand}</div>
                <div class="ranking-metric">${ranking.avgEngagement.toLocaleString()} avg engagement</div>
            </div>
            <div class="ranking-metric">${ranking.posts} posts</div>
        `;
        container.appendChild(rankingItem);
    });
}

function updateCulturalMoments(moments) {
    const container = document.getElementById('cultural-moments');
    container.innerHTML = '';
    
    moments.forEach(moment => {
        const momentItem = document.createElement('div');
        momentItem.className = 'cultural-moment';
        momentItem.innerHTML = `
            <div class="moment-title">${moment.brand} Viral Content</div>
            <div class="moment-description">${moment.content.substring(0, 100)}...</div>
            <div class="moment-metrics">
                <span><i class="fas fa-heart"></i> ${moment.engagement.toLocaleString()}</span>
                <span><i class="fas fa-clock"></i> ${new Date(moment.timestamp).toLocaleDateString()}</span>
            </div>
        `;
        container.appendChild(momentItem);
    });
}

function updateMetricsTable(rankings) {
    const tableBody = document.getElementById('metrics-table-body');
    tableBody.innerHTML = '';
    
    rankings.forEach(ranking => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ranking.rank}</td>
            <td>${ranking.brand}</td>
            <td>${ranking.posts}</td>
            <td>${ranking.avgEngagement.toLocaleString()}</td>
            <td>${ranking.totalLikes.toLocaleString()}</td>
            <td>${(ranking.posts / 7).toFixed(1)}/week</td>
            <td>${((ranking.avgEngagement / 1000) * 100).toFixed(1)}%</td>
        `;
        tableBody.appendChild(row);
    });
    
    document.getElementById('metrics-detail').style.display = 'block';
}

function updateCulturalRadar(analysis, dataType) {
    if (analysis.trendingThemes) {
        updateTrendingThemes(analysis.trendingThemes);
    }
    
    if (analysis.culturalInsights) {
        updateViralPatterns(analysis.culturalInsights);
    }
    
    if (analysis.rankings) {
        updateBrandMomentum(analysis.rankings);
    }
    
    updateStrategicInsights(analysis, dataType);
}

function updateTrendingThemes(themes) {
    const container = document.getElementById('trending-themes-list');
    container.innerHTML = '';
    
    themes.forEach(theme => {
        const themeItem = document.createElement('div');
        themeItem.className = 'trend-item';
        themeItem.innerHTML = `
            <div class="item-title">#${theme.theme}</div>
            <div class="item-description">${theme.posts} posts, ${theme.engagement.toLocaleString()} avg engagement</div>
            <div class="item-metric">Velocity: +${theme.velocity}% this week</div>
        `;
        container.appendChild(themeItem);
    });
}

function updateViralPatterns(insights) {
    const container = document.getElementById('viral-patterns-list');
    container.innerHTML = '';
    
    insights.forEach(insight => {
        const patternItem = document.createElement('div');
        patternItem.className = 'pattern-item';
        patternItem.innerHTML = `
            <div class="item-title">Viral Content by ${insight.author || insight.brand}</div>
            <div class="item-description">${insight.description.substring(0, 80)}...</div>
            <div class="item-metric">${insight.engagement.toLocaleString()} total engagement</div>
        `;
        container.appendChild(patternItem);
    });
}

function updateBrandMomentum(rankings) {
    const container = document.getElementById('brand-momentum-list');
    container.innerHTML = '';
    
    rankings.slice(0, 5).forEach(brand => {
        const momentumItem = document.createElement('div');
        momentumItem.className = 'momentum-item';
        const trend = brand.rank <= 3 ? '↗️ Rising' : brand.rank >= 8 ? '↘️ Declining' : '→ Stable';
        momentumItem.innerHTML = `
            <div class="item-title">${brand.brand}</div>
            <div class="item-description">Rank #${brand.rank} - ${brand.avgEngagement.toLocaleString()} avg engagement</div>
            <div class="item-metric">${trend}</div>
        `;
        container.appendChild(momentumItem);
    });
}

function updateStrategicInsights(analysis, dataType) {
    const container = document.getElementById('strategic-insights-list');
    container.innerHTML = '';
    
    const insights = generateStrategicInsights(analysis, dataType);
    
    insights.forEach(insight => {
        const insightItem = document.createElement('div');
        insightItem.className = 'insight-item';
        insightItem.innerHTML = `
            <div class="item-title">${insight.title}</div>
            <div class="item-description">${insight.description}</div>
            <div class="item-metric">${insight.action}</div>
        `;
        container.appendChild(insightItem);
    });
}

function generateStrategicInsights(analysis, dataType) {
    const insights = [];
    
    if (dataType === 'instagram' && analysis.rankings) {
        const crooksRank = analysis.rankings.find(r => r.brand.toLowerCase().includes('crooks'));
        if (crooksRank && crooksRank.rank > 5) {
            insights.push({
                title: 'Engagement Gap Alert',
                description: `Crooks ranks #${crooksRank.rank}/12 in engagement. Top performer has ${Math.round(analysis.rankings[0].avgEngagement / crooksRank.avgEngagement)}x higher engagement.`,
                action: 'Immediate content strategy review needed'
            });
        }
        
        if (crooksRank && crooksRank.posts < 3) {
            insights.push({
                title: 'Content Frequency Issue',
                description: `Only ${crooksRank.posts} posts in analysis period. Top brands posting 2-3x more frequently.`,
                action: 'Increase posting frequency to 1-2 posts daily'
            });
        }
    }
    
    if (analysis.trendingThemes && analysis.trendingThemes.length > 0) {
        const topTheme = analysis.trendingThemes[0];
        insights.push({
            title: 'Trending Opportunity',
            description: `#${topTheme.theme} showing high velocity with ${topTheme.posts} posts and strong engagement.`,
            action: 'Create content around this trending theme'
        });
    }
    
    return insights;
}

// Utility Functions
function extractBrandFromPost(post) {
    if (post.ownerUsername) {
        return post.ownerUsername;
    }
    
    if (post.url) {
        const match = post.url.match(/instagram\.com\/([^\/]+)/);
        return match ? match[1] : 'Unknown';
    }
    
    return 'Unknown';
}

function extractHashtagFromUrl(url) {
    if (url && url.includes('/explore/tags/')) {
        const match = url.match(/\/explore\/tags\/([^\/]+)/);
        return match ? match[1] : 'unknown';
    }
    return 'unknown';
}

function updateLastUpdated() {
    const now = new Date();
    document.getElementById('last-updated').textContent = now.toLocaleString();
}

function showStatusMessage(message, type = 'info') {
    const container = document.getElementById('status-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.textContent = message;
    
    container.appendChild(messageDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 5000);
}

// Refresh Functions
function refreshDashboard() {
    updateLastUpdated();
    // Refresh dashboard metrics if data is available
    if (currentData.processed) {
        Object.keys(currentData.processed).forEach(dataType => {
            updateDashboardMetrics(currentData.processed[dataType], dataType);
        });
    }
}

function refreshCompetitiveData() {
    // Refresh competitive intelligence data
    if (currentData.processed && currentData.processed.instagram) {
        updateCompetitiveIntelligence(currentData.processed.instagram, 'instagram');
    }
}

function refreshCulturalRadar() {
    // Refresh cultural radar data
    if (currentData.processed) {
        Object.keys(currentData.processed).forEach(dataType => {
            updateCulturalRadar(currentData.processed[dataType], dataType);
        });
    }
}

function loadInitialData() {
    // Load any existing data from the server
    fetch('/api/dashboard-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update dashboard with existing data
                updateDashboardMetrics(data.metrics, 'dashboard');
            }
        })
        .catch(error => {
            console.log('No existing data found, starting fresh');
        });
}

// Calendar and Assets functions (placeholder)
function loadCalendarEvents() {
    const container = document.getElementById('events-list');
    container.innerHTML = '<div class="loading-state"><i class="fas fa-calendar"></i><p>Calendar integration coming soon</p></div>';
}

function loadBrandAssets() {
    const container = document.getElementById('assets-grid');
    container.innerHTML = '<div class="loading-state"><i class="fas fa-folder"></i><p>Asset management coming soon</p></div>';
}

function createEvent() {
    showStatusMessage('Calendar integration coming soon', 'info');
}

function uploadAsset() {
    showStatusMessage('Asset upload coming soon', 'info');
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}
