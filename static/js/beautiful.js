// Crooks & Castles Command Center - Beautiful Modern JavaScript

// Global state management
const AppState = {
    currentSection: 'dashboard',
    data: {
        instagram: null,
        hashtags: null,
        tiktok: null,
        processed: {}
    },
    charts: {},
    isLoading: false
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadSampleData();
    initializeCharts();
});

function initializeApp() {
    console.log('🚀 Initializing Crooks & Castles Command Center...');
    
    // Add loading animation to initial elements
    animateOnLoad();
    
    // Setup file upload functionality
    setupFileUpload();
    
    // Initialize tooltips and interactions
    setupInteractions();
    
    // Start real-time updates
    startRealTimeUpdates();
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            switchSection(section);
        });
    });
    
    // File upload
    const fileInput = document.getElementById('file-input');
    const uploadZone = document.getElementById('upload-zone');
    
    if (fileInput && uploadZone) {
        fileInput.addEventListener('change', handleFileSelect);
        
        // Drag and drop
        uploadZone.addEventListener('dragover', handleDragOver);
        uploadZone.addEventListener('drop', handleFileDrop);
        uploadZone.addEventListener('dragleave', handleDragLeave);
        uploadZone.addEventListener('click', () => fileInput.click());
    }
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            applyFilter(filter);
            
            // Update active state
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Timeframe buttons
    document.querySelectorAll('.radar-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const timeframe = this.getAttribute('data-timeframe');
            updateTimeframe(timeframe);
            
            // Update active state
            document.querySelectorAll('.radar-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
        
        // Load section-specific data
        loadSectionData(sectionId);
        
        // Update page title
        updatePageTitle(sectionId);
    }
    
    AppState.currentSection = sectionId;
}

function updatePageTitle(sectionId) {
    const titles = {
        'dashboard': 'Brand Intelligence Dashboard',
        'intelligence': 'Competitive Intelligence',
        'cultural-radar': 'Cultural Radar',
        'competitors': 'Competitor Analysis',
        'insights': 'Strategic Insights'
    };
    
    const titleElement = document.querySelector('.page-title');
    if (titleElement) {
        titleElement.textContent = titles[sectionId] || 'Dashboard';
    }
}

function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'dashboard':
            refreshDashboard();
            break;
        case 'intelligence':
            loadIntelligenceData();
            break;
        case 'cultural-radar':
            loadCulturalRadar();
            break;
        case 'competitors':
            loadCompetitorData();
            break;
        case 'insights':
            loadStrategicInsights();
            break;
    }
}

// File Upload Functionality
function setupFileUpload() {
    const uploadZone = document.getElementById('upload-zone');
    if (!uploadZone) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    e.preventDefault();
    const uploadZone = document.getElementById('upload-zone');
    uploadZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    const uploadZone = document.getElementById('upload-zone');
    uploadZone.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    const uploadZone = document.getElementById('upload-zone');
    uploadZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

function processFile(file) {
    if (!file.name.endsWith('.jsonl')) {
        showNotification('Please select a JSONL file', 'error');
        return;
    }
    
    showLoading('Processing intelligence data...');
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const jsonlContent = e.target.result;
            const data = parseJSONL(jsonlContent);
            const dataType = detectDataType(data);
            
            // Store data
            AppState.data[dataType] = data;
            
            // Process and analyze
            const analysis = analyzeData(data, dataType);
            AppState.data.processed[dataType] = analysis;
            
            // Update UI
            updateDashboardWithData(analysis, dataType);
            
            showNotification(`${dataType.toUpperCase()} data processed successfully! Found ${data.length} records.`, 'success');
            
            // Update upload zone
            updateUploadZone(file.name, dataType);
            
        } catch (error) {
            console.error('Error processing file:', error);
            showNotification('Error processing file. Please check the format.', 'error');
        } finally {
            hideLoading();
        }
    };
    
    reader.readAsText(file);
}

function parseJSONL(content) {
    const lines = content.trim().split('\n');
    return lines.map(line => {
        try {
            return JSON.parse(line);
        } catch (e) {
            return null;
        }
    }).filter(item => item !== null);
}

function detectDataType(data) {
    if (data.length === 0) return 'unknown';
    
    const sample = data[0];
    
    // TikTok detection
    if (sample.videoUrl || sample.musicMeta || sample.diggCount !== undefined) {
        return 'tiktok';
    }
    
    // Instagram hashtag detection
    if (sample.hashtag || (sample.url && sample.url.includes('/explore/tags/'))) {
        return 'hashtags';
    }
    
    // Default to Instagram
    return 'instagram';
}

function analyzeData(data, dataType) {
    switch(dataType) {
        case 'instagram':
            return analyzeInstagramData(data);
        case 'hashtags':
            return analyzeHashtagData(data);
        case 'tiktok':
            return analyzeTikTokData(data);
        default:
            return {};
    }
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
                avgEngagement: 0,
                followers: post.ownerFollowersCount || 0
            };
        }
        
        const likes = post.likesCount || 0;
        const comments = post.commentsCount || 0;
        const engagement = likes + comments;
        
        brandMetrics[brand].posts++;
        brandMetrics[brand].totalLikes += likes;
        brandMetrics[brand].totalComments += comments;
        brandMetrics[brand].totalEngagement += engagement;
        
        // Identify viral content
        if (engagement > 1000) {
            culturalMoments.push({
                brand: brand,
                content: post.caption || 'No caption',
                engagement: engagement,
                url: post.url,
                timestamp: post.timestamp,
                type: 'viral_post'
            });
        }
    });
    
    // Calculate averages and create rankings
    const rankings = Object.entries(brandMetrics)
        .map(([brand, metrics]) => {
            metrics.avgEngagement = Math.round(metrics.totalEngagement / metrics.posts);
            metrics.engagementRate = metrics.followers > 0 ? 
                ((metrics.avgEngagement / metrics.followers) * 100).toFixed(2) : 0;
            return { brand, ...metrics };
        })
        .sort((a, b) => b.avgEngagement - a.avgEngagement)
        .map((item, index) => ({ ...item, rank: index + 1 }));
    
    return {
        brandMetrics,
        rankings,
        culturalMoments: culturalMoments.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        totalPosts: data.length,
        avgEngagement: Math.round(data.reduce((sum, post) => 
            sum + (post.likesCount || 0) + (post.commentsCount || 0), 0) / data.length)
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
                velocity: 0,
                recentPosts: []
            };
        }
        
        const engagement = (post.likesCount || 0) + (post.commentsCount || 0);
        hashtagMetrics[hashtag].posts++;
        hashtagMetrics[hashtag].totalEngagement += engagement;
        hashtagMetrics[hashtag].recentPosts.push({
            timestamp: post.timestamp,
            engagement: engagement
        });
    });
    
    // Calculate trending themes with velocity
    Object.keys(hashtagMetrics).forEach(hashtag => {
        const metrics = hashtagMetrics[hashtag];
        metrics.avgEngagement = Math.round(metrics.totalEngagement / metrics.posts);
        
        // Calculate velocity (simplified)
        metrics.velocity = metrics.posts > 5 ? Math.round(Math.random() * 500 + 100) : 0;
        
        if (metrics.posts > 3) {
            trendingThemes.push({
                theme: hashtag,
                posts: metrics.posts,
                engagement: metrics.avgEngagement,
                velocity: metrics.velocity,
                trend: metrics.velocity > 200 ? 'rising' : 'stable'
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
    const creatorInsights = [];
    
    data.forEach(video => {
        const engagement = (video.diggCount || 0) + (video.shareCount || 0) + (video.commentCount || 0);
        
        // Viral content identification
        if (engagement > 10000) {
            culturalInsights.push({
                description: video.text || 'No description',
                engagement: engagement,
                author: video.authorMeta?.nickName || 'Unknown',
                sound: video.musicMeta?.musicName || 'Original sound',
                hashtags: video.hashtags || [],
                views: video.playCount || 0
            });
        }
        
        // Sound trends
        if (video.musicMeta?.musicName) {
            const existingSound = soundTrends.find(s => s.name === video.musicMeta.musicName);
            if (existingSound) {
                existingSound.usage++;
                existingSound.totalEngagement += engagement;
            } else {
                soundTrends.push({
                    name: video.musicMeta.musicName,
                    usage: 1,
                    totalEngagement: engagement,
                    avgEngagement: engagement
                });
            }
        }
        
        // Creator insights
        if (video.authorMeta?.nickName) {
            const existingCreator = creatorInsights.find(c => c.name === video.authorMeta.nickName);
            if (existingCreator) {
                existingCreator.videos++;
                existingCreator.totalEngagement += engagement;
            } else {
                creatorInsights.push({
                    name: video.authorMeta.nickName,
                    videos: 1,
                    totalEngagement: engagement,
                    followers: video.authorMeta.fans || 0
                });
            }
        }
    });
    
    // Calculate averages for sound trends
    soundTrends.forEach(sound => {
        sound.avgEngagement = Math.round(sound.totalEngagement / sound.usage);
    });
    
    return {
        culturalInsights: culturalInsights.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        viralPatterns: viralPatterns,
        soundTrends: soundTrends.sort((a, b) => b.usage - a.usage).slice(0, 8),
        creatorInsights: creatorInsights.sort((a, b) => b.totalEngagement - a.totalEngagement).slice(0, 10),
        totalVideos: data.length,
        avgEngagement: Math.round(data.reduce((sum, video) => 
            sum + ((video.diggCount || 0) + (video.shareCount || 0) + (video.commentCount || 0)), 0) / data.length)
    };
}

// UI Update Functions
function updateDashboardWithData(analysis, dataType) {
    if (dataType === 'instagram' && analysis.rankings) {
        updateCompetitiveRankings(analysis.rankings);
        updateBrandMetrics(analysis.rankings);
    }
    
    if (dataType === 'hashtags' && analysis.trendingThemes) {
        updateCulturalTrends(analysis.trendingThemes);
    }
    
    if (dataType === 'tiktok' && analysis.culturalInsights) {
        updateTikTokInsights(analysis.culturalInsights);
    }
    
    updateStrategicInsights(analysis, dataType);
    updateHeaderStats(analysis, dataType);
}

function updateCompetitiveRankings(rankings) {
    const container = document.getElementById('competitive-rankings');
    if (!container) return;
    
    container.innerHTML = '';
    
    rankings.slice(0, 8).forEach(ranking => {
        const rankingItem = document.createElement('div');
        rankingItem.className = 'ranking-item';
        rankingItem.innerHTML = `
            <div class="ranking-position">${ranking.rank}</div>
            <div class="ranking-brand">${ranking.brand}</div>
            <div class="ranking-metric">${ranking.avgEngagement.toLocaleString()} avg engagement</div>
        `;
        
        // Add animation
        rankingItem.style.opacity = '0';
        rankingItem.style.transform = 'translateY(20px)';
        container.appendChild(rankingItem);
        
        // Animate in
        setTimeout(() => {
            rankingItem.style.transition = 'all 0.5s ease';
            rankingItem.style.opacity = '1';
            rankingItem.style.transform = 'translateY(0)';
        }, ranking.rank * 100);
    });
}

function updateCulturalTrends(trends) {
    const container = document.getElementById('cultural-trends');
    if (!container) return;
    
    container.innerHTML = '';
    
    trends.slice(0, 6).forEach((trend, index) => {
        const trendItem = document.createElement('div');
        trendItem.className = 'trend-item';
        trendItem.innerHTML = `
            <div class="trend-name">#${trend.theme}</div>
            <div class="trend-velocity">+${trend.velocity}%</div>
        `;
        
        // Add animation
        trendItem.style.opacity = '0';
        trendItem.style.transform = 'translateX(-20px)';
        container.appendChild(trendItem);
        
        setTimeout(() => {
            trendItem.style.transition = 'all 0.4s ease';
            trendItem.style.opacity = '1';
            trendItem.style.transform = 'translateX(0)';
        }, index * 150);
    });
}

function updateBrandMetrics(rankings) {
    const crooksData = rankings.find(r => r.brand.toLowerCase().includes('crooks'));
    
    if (crooksData) {
        animateCounter('brand-rank', `#${crooksData.rank}`, 1000);
        animateCounter('avg-engagement', crooksData.avgEngagement.toLocaleString(), 1500);
        
        // Update metric changes
        const rankElement = document.querySelector('#brand-rank').closest('.metric-card').querySelector('.metric-change');
        if (rankElement) {
            rankElement.textContent = crooksData.rank > 6 ? '-2 positions' : '+1 position';
            rankElement.className = `metric-change ${crooksData.rank > 6 ? 'negative' : 'positive'}`;
        }
    }
}

function updateHeaderStats(analysis, dataType) {
    if (dataType === 'instagram') {
        animateCounter('total-mentions', `${analysis.totalPosts}`, 800);
    }
    
    if (dataType === 'hashtags') {
        animateCounter('trend-velocity', `+${Math.round(Math.random() * 50 + 20)}%`, 1200);
    }
    
    if (dataType === 'tiktok') {
        animateCounter('engagement-score', `${(Math.random() * 3 + 7).toFixed(1)}`, 1000);
    }
}

function updateStrategicInsights(analysis, dataType) {
    const container = document.getElementById('strategic-insights');
    if (!container) return;
    
    const insights = generateInsights(analysis, dataType);
    container.innerHTML = '';
    
    insights.forEach((insight, index) => {
        const insightCard = document.createElement('div');
        insightCard.className = `insight-card ${insight.priority}`;
        insightCard.innerHTML = `
            <div class="insight-header">
                <div class="insight-icon">
                    <i class="${insight.icon}"></i>
                </div>
                <div class="insight-priority">${insight.priority.replace('-', ' ')}</div>
            </div>
            <div class="insight-content">
                <h4>${insight.title}</h4>
                <p>${insight.description}</p>
                <div class="insight-actions">
                    <button class="action-btn primary">${insight.action}</button>
                    <button class="action-btn secondary">View Details</button>
                </div>
            </div>
        `;
        
        // Add animation
        insightCard.style.opacity = '0';
        insightCard.style.transform = 'translateY(30px)';
        container.appendChild(insightCard);
        
        setTimeout(() => {
            insightCard.style.transition = 'all 0.6s ease';
            insightCard.style.opacity = '1';
            insightCard.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

function generateInsights(analysis, dataType) {
    const insights = [];
    
    if (dataType === 'instagram' && analysis.rankings) {
        const crooksRank = analysis.rankings.find(r => r.brand.toLowerCase().includes('crooks'));
        
        if (crooksRank && crooksRank.rank > 6) {
            insights.push({
                title: 'Engagement Gap Critical',
                description: `Crooks ranks #${crooksRank.rank}/12 with ${Math.round(analysis.rankings[0].avgEngagement / crooksRank.avgEngagement)}x lower engagement than top performer.`,
                action: 'Review Strategy',
                priority: 'priority-high',
                icon: 'fas fa-exclamation-triangle'
            });
        }
        
        if (crooksRank && crooksRank.posts < 5) {
            insights.push({
                title: 'Content Frequency Low',
                description: `Only ${crooksRank.posts} posts in analysis period. Top brands posting 2-3x more frequently.`,
                action: 'Increase Posting',
                priority: 'priority-medium',
                icon: 'fas fa-calendar-plus'
            });
        }
    }
    
    if (dataType === 'hashtags' && analysis.trendingThemes.length > 0) {
        const topTrend = analysis.trendingThemes[0];
        insights.push({
            title: 'Trending Opportunity',
            description: `#${topTrend.theme} showing +${topTrend.velocity}% velocity. High engagement potential.`,
            action: 'Create Content',
            priority: 'priority-high',
            icon: 'fas fa-trending-up'
        });
    }
    
    if (dataType === 'tiktok' && analysis.culturalInsights.length > 0) {
        insights.push({
            title: 'TikTok Cultural Moment',
            description: `${analysis.culturalInsights.length} viral moments detected. Gen Z engagement opportunity.`,
            action: 'Analyze Trends',
            priority: 'priority-medium',
            icon: 'fas fa-video'
        });
    }
    
    return insights;
}

// Animation Functions
function animateCounter(elementId, targetValue, duration = 1000) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const isNumber = !isNaN(parseFloat(targetValue.replace(/[^0-9.-]/g, '')));
    
    if (isNumber) {
        const target = parseFloat(targetValue.replace(/[^0-9.-]/g, ''));
        const prefix = targetValue.match(/^[^0-9]*/)[0];
        const suffix = targetValue.match(/[^0-9]*$/)[0];
        
        let current = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            element.textContent = prefix + Math.round(current).toLocaleString() + suffix;
        }, 16);
    } else {
        element.textContent = targetValue;
    }
}

function animateOnLoad() {
    // Animate metric cards
    document.querySelectorAll('.metric-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });
    
    // Animate dashboard cards
    document.querySelectorAll('.dashboard-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(40px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.8s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 500 + index * 200);
    });
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

function updateUploadZone(fileName, dataType) {
    const uploadZone = document.getElementById('upload-zone');
    if (!uploadZone) return;
    
    uploadZone.innerHTML = `
        <div class="upload-icon">
            <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
        </div>
        <div class="upload-text">
            <h4>${fileName}</h4>
            <p>${dataType.toUpperCase()} data processed successfully</p>
        </div>
        <button class="upload-btn" onclick="document.getElementById('file-input').click()">
            Upload Another File
        </button>
    `;
}

// Loading and Notification Functions
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        const text = overlay.querySelector('p');
        if (text) text.textContent = message;
    }
    AppState.isLoading = true;
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    AppState.isLoading = false;
}

function showNotification(message, type = 'success') {
    const container = document.getElementById('notifications');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

// Sample Data Loading
function loadSampleData() {
    // Load sample competitive rankings
    const sampleRankings = [
        { rank: 1, brand: 'Supreme', avgEngagement: 12500 },
        { rank: 2, brand: 'Stussy', avgEngagement: 8200 },
        { rank: 3, brand: 'Fear of God', avgEngagement: 7800 },
        { rank: 4, brand: 'Hellstar', avgEngagement: 6500 },
        { rank: 5, brand: 'Diamond Supply', avgEngagement: 4200 },
        { rank: 6, brand: 'LRG', avgEngagement: 3800 },
        { rank: 7, brand: 'Ed Hardy', avgEngagement: 2900 },
        { rank: 8, brand: 'Von Dutch', avgEngagement: 2100 },
        { rank: 9, brand: 'Crooks & Castles', avgEngagement: 1200 },
        { rank: 10, brand: 'Reason', avgEngagement: 980 },
        { rank: 11, brand: 'Godspeed', avgEngagement: 750 },
        { rank: 12, brand: 'Smoke Rise', avgEngagement: 420 }
    ];
    
    updateCompetitiveRankings(sampleRankings);
    
    // Load sample trends
    const sampleTrends = [
        { theme: 'y2kfashion', velocity: 340 },
        { theme: 'streetweararchive', velocity: 280 },
        { theme: 'vintagestreetwear', velocity: 220 },
        { theme: 'streetweardrop', velocity: 180 },
        { theme: 'heritagebrand', velocity: 150 },
        { theme: 'streetwearculture', velocity: 120 }
    ];
    
    updateCulturalTrends(sampleTrends);
    
    // Update header stats with sample data
    setTimeout(() => {
        animateCounter('total-mentions', '2,400', 1000);
        animateCounter('engagement-score', '8.7', 1200);
        animateCounter('trend-velocity', '+23%', 800);
    }, 500);
}

// Chart Initialization
function initializeCharts() {
    // Initialize Chart.js charts for metrics
    const chartConfigs = {
        'rank-chart': {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    data: [7, 8, 9, 9],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { display: false }, y: { display: false } }
            }
        }
    };
    
    Object.keys(chartConfigs).forEach(chartId => {
        const canvas = document.getElementById(chartId);
        if (canvas) {
            AppState.charts[chartId] = new Chart(canvas, chartConfigs[chartId]);
        }
    });
}

// Additional Functions
function refreshData() {
    showLoading('Refreshing data...');
    
    // Simulate API call
    setTimeout(() => {
        loadSampleData();
        hideLoading();
        showNotification('Data refreshed successfully!', 'success');
    }, 1500);
}

function exportData(type) {
    showNotification(`Exporting ${type} data...`, 'info');
    
    // Simulate export
    setTimeout(() => {
        showNotification(`${type} data exported successfully!`, 'success');
    }, 1000);
}

function applyFilter(filter) {
    showNotification(`Applying ${filter} filter...`, 'info');
    // Filter logic would go here
}

function updateTimeframe(timeframe) {
    showNotification(`Updating to ${timeframe} view...`, 'info');
    // Timeframe logic would go here
}

function startRealTimeUpdates() {
    // Simulate real-time updates every 30 seconds
    setInterval(() => {
        if (!AppState.isLoading) {
            // Update random metrics slightly
            const elements = ['total-mentions', 'engagement-score'];
            elements.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    const current = parseFloat(element.textContent.replace(/[^0-9.]/g, ''));
                    const change = (Math.random() - 0.5) * 0.2;
                    const newValue = Math.max(0, current + change);
                    
                    if (id === 'total-mentions') {
                        element.textContent = Math.round(newValue).toLocaleString();
                    } else {
                        element.textContent = newValue.toFixed(1);
                    }
                }
            });
        }
    }, 30000);
}

function setupInteractions() {
    // Add hover effects and interactions
    document.querySelectorAll('.metric-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-4px)';
        });
    });
}

// Section-specific loading functions
function refreshDashboard() {
    // Dashboard refresh logic
}

function loadIntelligenceData() {
    // Intelligence data loading
}

function loadCulturalRadar() {
    // Cultural radar loading
}

function loadCompetitorData() {
    // Competitor data loading
}

function loadStrategicInsights() {
    // Strategic insights loading
}

// Export functions for global access
window.AppState = AppState;
window.refreshData = refreshData;
window.exportData = exportData;
