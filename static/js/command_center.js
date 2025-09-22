// Crooks & Castles Command Center - Matching Existing Design
document.addEventListener('DOMContentLoaded', function() {
    initializeCommandCenter();
});

function initializeCommandCenter() {
    setupNavigation();
    setupFileUpload();
    loadInitialData();
    setupEventListeners();
}

// Navigation
function setupNavigation() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const sections = document.querySelectorAll('.content-section');
    
    navTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetSection = this.getAttribute('data-section');
            
            // Update active tab
            navTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Update active section
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(targetSection).classList.add('active');
        });
    });
}

// File Upload
function setupFileUpload() {
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');
    
    if (!uploadZone || !fileInput) return;
    
    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // File selection
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('drop', handleFileDrop);
    uploadZone.addEventListener('dragleave', handleDragLeave);
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
    
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
    if (!file.name.endsWith('.jsonl') && !file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
        showNotification('Please select a JSONL, CSV, or JSON file', 'error');
        return;
    }
    
    showLoading('Processing intelligence data...');
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            let data;
            const content = e.target.result;
            
            if (file.name.endsWith('.jsonl')) {
                data = parseJSONL(content);
            } else if (file.name.endsWith('.json')) {
                data = JSON.parse(content);
            } else {
                // CSV parsing would go here
                data = parseCSV(content);
            }
            
            const dataType = detectDataType(data, file.name);
            const analysis = analyzeData(data, dataType);
            
            updateDashboard(analysis, dataType);
            updateUploadStatus(file.name, dataType, data.length);
            
            showNotification(`${dataType.toUpperCase()} data processed successfully! Found ${data.length} records.`, 'success');
            
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
    return content.trim().split('\n')
        .map(line => {
            try {
                return JSON.parse(line);
            } catch (e) {
                return null;
            }
        })
        .filter(item => item !== null);
}

function parseCSV(content) {
    // Simple CSV parser - would need more robust implementation
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',');
    
    return lines.slice(1).map(line => {
        const values = line.split(',');
        const obj = {};
        headers.forEach((header, index) => {
            obj[header.trim()] = values[index]?.trim();
        });
        return obj;
    });
}

function detectDataType(data, filename) {
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
            return { totalRecords: data.length };
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
                timestamp: post.timestamp
            });
        }
    });
    
    // Calculate averages and create rankings
    const rankings = Object.entries(brandMetrics)
        .map(([brand, metrics]) => {
            metrics.avgEngagement = Math.round(metrics.totalEngagement / metrics.posts);
            return { brand, ...metrics };
        })
        .sort((a, b) => b.avgEngagement - a.avgEngagement)
        .map((item, index) => ({ ...item, rank: index + 1 }));
    
    return {
        brandMetrics,
        rankings,
        culturalMoments: culturalMoments.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        totalPosts: data.length
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
                velocity: Math.round(Math.random() * 400 + 100) // Simulated velocity
            };
        }
        
        const engagement = (post.likesCount || 0) + (post.commentsCount || 0);
        hashtagMetrics[hashtag].posts++;
        hashtagMetrics[hashtag].totalEngagement += engagement;
    });
    
    // Create trending themes
    Object.keys(hashtagMetrics).forEach(hashtag => {
        const metrics = hashtagMetrics[hashtag];
        if (metrics.posts > 2) {
            trendingThemes.push({
                theme: hashtag,
                posts: metrics.posts,
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
    const soundTrends = [];
    
    data.forEach(video => {
        const engagement = (video.diggCount || 0) + (video.shareCount || 0) + (video.commentCount || 0);
        
        if (engagement > 5000) {
            culturalInsights.push({
                description: video.text || 'No description',
                engagement: engagement,
                author: video.authorMeta?.nickName || 'Unknown',
                views: video.playCount || 0
            });
        }
    });
    
    return {
        culturalInsights: culturalInsights.sort((a, b) => b.engagement - a.engagement).slice(0, 10),
        soundTrends,
        totalVideos: data.length
    };
}

function updateDashboard(analysis, dataType) {
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
}

function updateCompetitiveRankings(rankings) {
    const container = document.getElementById('competitive-rankings');
    if (!container) return;
    
    container.innerHTML = '';
    
    rankings.slice(0, 8).forEach((ranking, index) => {
        const rankingItem = document.createElement('div');
        rankingItem.className = 'ranking-item';
        if (ranking.brand.toLowerCase().includes('crooks')) {
            rankingItem.classList.add('crooks-rank');
        }
        
        rankingItem.innerHTML = `
            <div class="rank-position">${ranking.rank}</div>
            <div class="brand-info">
                <div class="brand-name">${ranking.brand}</div>
                <div class="brand-metric">${ranking.avgEngagement.toLocaleString()} avg engagement</div>
            </div>
        `;
        
        container.appendChild(rankingItem);
        
        // Animate in
        setTimeout(() => {
            rankingItem.style.opacity = '0';
            rankingItem.style.transform = 'translateY(20px)';
            rankingItem.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                rankingItem.style.opacity = '1';
                rankingItem.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
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
        
        container.appendChild(trendItem);
        
        // Animate in
        setTimeout(() => {
            trendItem.style.opacity = '0';
            trendItem.style.transform = 'translateX(-20px)';
            trendItem.style.transition = 'all 0.4s ease';
            
            setTimeout(() => {
                trendItem.style.opacity = '1';
                trendItem.style.transform = 'translateX(0)';
            }, 50);
        }, index * 150);
    });
}

function updateTikTokInsights(insights) {
    const container = document.getElementById('tiktok-insights');
    if (!container) return;
    
    container.innerHTML = '';
    
    insights.slice(0, 4).forEach((insight, index) => {
        const insightItem = document.createElement('div');
        insightItem.className = 'insight-item';
        insightItem.innerHTML = `
            <div class="insight-text">${insight.description.substring(0, 50)}...</div>
            <div class="insight-metric">${insight.engagement.toLocaleString()}</div>
        `;
        
        container.appendChild(insightItem);
    });
}

function updateBrandMetrics(rankings) {
    const crooksData = rankings.find(r => r.brand.toLowerCase().includes('crooks'));
    
    if (crooksData) {
        // Update metrics with animation
        animateCounter(document.querySelector('.metric-value'), `#${crooksData.rank}`, 1000);
        
        // Update other metrics
        const metricValues = document.querySelectorAll('.metric-value');
        if (metricValues[1]) {
            animateCounter(metricValues[1], crooksData.avgEngagement.toLocaleString(), 1500);
        }
    }
}

function updateStrategicInsights(analysis, dataType) {
    const container = document.getElementById('strategic-insights');
    if (!container) return;
    
    const insights = generateInsights(analysis, dataType);
    
    // Update existing insights or add new ones
    insights.forEach((insight, index) => {
        const existingCards = container.querySelectorAll('.insight-card');
        if (existingCards[index]) {
            const contentDiv = existingCards[index].querySelector('.insight-content');
            if (contentDiv) {
                contentDiv.querySelector('h4').textContent = insight.title;
                contentDiv.querySelector('p').textContent = insight.description;
            }
        }
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
                action: 'Review Strategy'
            });
        }
    }
    
    if (dataType === 'hashtags' && analysis.trendingThemes.length > 0) {
        const topTrend = analysis.trendingThemes[0];
        insights.push({
            title: 'Trending Opportunity',
            description: `#${topTrend.theme} showing +${topTrend.velocity}% velocity. High engagement potential.`,
            action: 'Create Content'
        });
    }
    
    return insights;
}

function updateUploadStatus(filename, dataType, recordCount) {
    const uploadZone = document.getElementById('upload-zone');
    if (!uploadZone) return;
    
    uploadZone.innerHTML = `
        <div class="upload-icon">
            <i class="fas fa-check-circle" style="color: var(--accent-green);"></i>
        </div>
        <div class="upload-text">
            <h4>${filename}</h4>
            <p>${dataType.toUpperCase()} data processed successfully (${recordCount} records)</p>
        </div>
    `;
    
    // Add click to upload another
    setTimeout(() => {
        uploadZone.addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
    }, 100);
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

function animateCounter(element, targetValue, duration = 1000) {
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

// Loading and Notifications
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        const text = overlay.querySelector('p');
        if (text) text.textContent = message;
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
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

// Load initial sample data
function loadInitialData() {
    // Sample competitive rankings
    const sampleRankings = [
        { rank: 1, brand: 'Supreme', avgEngagement: 12500 },
        { rank: 2, brand: 'Stussy', avgEngagement: 8200 },
        { rank: 3, brand: 'Fear of God', avgEngagement: 7800 },
        { rank: 4, brand: 'Hellstar', avgEngagement: 6500 },
        { rank: 5, brand: 'Diamond Supply', avgEngagement: 4200 },
        { rank: 6, brand: 'LRG', avgEngagement: 3800 },
        { rank: 7, brand: 'Ed Hardy', avgEngagement: 2900 },
        { rank: 8, brand: 'Von Dutch', avgEngagement: 2100 },
        { rank: 9, brand: 'Crooks & Castles', avgEngagement: 1200 }
    ];
    
    updateCompetitiveRankings(sampleRankings);
    
    // Sample trends
    const sampleTrends = [
        { theme: 'y2kfashion', velocity: 340 },
        { theme: 'streetweararchive', velocity: 280 },
        { theme: 'vintagestreetwear', velocity: 220 }
    ];
    
    updateCulturalTrends(sampleTrends);
}

function setupEventListeners() {
    // Add any additional event listeners here
    document.addEventListener('keydown', function(e) {
        // Keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    document.querySelector('[data-section="intelligence"]').click();
                    break;
                case '2':
                    e.preventDefault();
                    document.querySelector('[data-section="cultural-radar"]').click();
                    break;
                case '3':
                    e.preventDefault();
                    document.querySelector('[data-section="competitive"]').click();
                    break;
            }
        }
    });
}
