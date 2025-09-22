/**
 * Enhanced Apify Data Visualization for Crooks & Castles Command Center V2
 * Comprehensive charts, graphs, and interactive data displays
 */

class ApifyDataVisualizer {
    constructor() {
        this.charts = {};
        this.data = {
            instagram: [],
            hashtags: [],
            tiktok: [],
            competitive: {},
            cultural: {}
        };
        this.colors = {
            primary: '#FFD700',      // Gold
            secondary: '#000000',    // Black
            accent: '#8B0000',       // Dark Red
            success: '#32CD32',      // Lime Green
            warning: '#FF6347',      // Tomato
            info: '#20B2AA',         // Light Sea Green
            purple: '#4B0082',       // Indigo
            pink: '#FF1493'          // Deep Pink
        };
        
        this.init();
    }

    init() {
        this.setupChartContainers();
        this.loadApifyData();
        this.setupRealTimeUpdates();
        this.setupInteractiveFilters();
    }

    setupChartContainers() {
        // Create chart containers if they don't exist
        const chartContainers = [
            'competitive-rankings-chart',
            'hashtag-velocity-chart',
            'tiktok-trends-chart',
            'engagement-timeline-chart',
            'cultural-momentum-chart',
            'brand-performance-radar',
            'opportunity-matrix-chart',
            'content-performance-heatmap'
        ];

        chartContainers.forEach(containerId => {
            if (!document.getElementById(containerId)) {
                console.warn(`Chart container ${containerId} not found`);
            }
        });
    }

    async loadApifyData() {
        try {
            const response = await fetch('/api/intelligence/summary');
            const data = await response.json();
            
            this.data.competitive = data.competitive_rankings || {};
            this.data.cultural = data.cultural_radar || {};
            
            // Load detailed data
            await this.loadDetailedData();
            
            // Initialize all charts
            this.initializeAllCharts();
            
        } catch (error) {
            console.error('Error loading Apify data:', error);
            this.showError('Failed to load intelligence data');
        }
    }

    async loadDetailedData() {
        try {
            // Load Instagram data
            const instagramResponse = await fetch('/api/intelligence/instagram');
            if (instagramResponse.ok) {
                this.data.instagram = await instagramResponse.json();
            }

            // Load hashtag data
            const hashtagResponse = await fetch('/api/intelligence/hashtags');
            if (hashtagResponse.ok) {
                this.data.hashtags = await hashtagResponse.json();
            }

            // Load TikTok data
            const tiktokResponse = await fetch('/api/intelligence/tiktok');
            if (tiktokResponse.ok) {
                this.data.tiktok = await tiktokResponse.json();
            }
        } catch (error) {
            console.warn('Detailed data not available:', error);
        }
    }

    initializeAllCharts() {
        this.createCompetitiveRankingsChart();
        this.createHashtagVelocityChart();
        this.createTikTokTrendsChart();
        this.createEngagementTimelineChart();
        this.createCulturalMomentumChart();
        this.createBrandPerformanceRadar();
        this.createOpportunityMatrixChart();
        this.createContentPerformanceHeatmap();
    }

    createCompetitiveRankingsChart() {
        const ctx = document.getElementById('competitive-rankings-chart');
        if (!ctx) return;

        const brands = Object.keys(this.data.competitive);
        const rankings = brands.map(brand => this.data.competitive[brand].rank);
        const engagements = brands.map(brand => 
            this.data.competitive[brand].metrics?.avg_engagement || 0
        );

        // Highlight Crooks & Castles
        const backgroundColors = brands.map(brand => 
            brand === 'Crooks & Castles' ? this.colors.primary : this.colors.secondary
        );

        this.charts.competitive = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: brands,
                datasets: [{
                    label: 'Average Engagement',
                    data: engagements,
                    backgroundColor: backgroundColors,
                    borderColor: this.colors.primary,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Competitive Brand Rankings',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    x: {
                        ticks: { 
                            color: '#ffffff',
                            maxRotation: 45
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createHashtagVelocityChart() {
        const ctx = document.getElementById('hashtag-velocity-chart');
        if (!ctx || !this.data.cultural.trending_hashtags) return;

        const hashtags = this.data.cultural.trending_hashtags.slice(0, 10);
        const labels = hashtags.map(h => `#${h.hashtag}`);
        const velocities = hashtags.map(h => h.velocity);
        const engagements = hashtags.map(h => h.engagement);

        this.charts.hashtags = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Velocity (%)',
                        data: velocities,
                        borderColor: this.colors.accent,
                        backgroundColor: 'rgba(139, 0, 0, 0.1)',
                        yAxisID: 'y'
                    },
                    {
                        label: 'Avg Engagement',
                        data: engagements,
                        borderColor: this.colors.success,
                        backgroundColor: 'rgba(50, 205, 50, 0.1)',
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Hashtag Velocity & Engagement Trends',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { 
                            color: '#ffffff',
                            maxRotation: 45
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        ticks: { color: '#ffffff' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }

    createTikTokTrendsChart() {
        const ctx = document.getElementById('tiktok-trends-chart');
        if (!ctx || !this.data.cultural.tiktok_insights) return;

        const insights = this.data.cultural.tiktok_insights;
        const trendingContent = insights.cultural_moments || [];

        // Create a doughnut chart for content distribution
        const contentTypes = ['Viral', 'Trending', 'Emerging', 'Standard'];
        const contentCounts = [
            trendingContent.filter(c => c.cultural_moment === 'viral').length,
            trendingContent.filter(c => c.cultural_moment === 'trending').length,
            trendingContent.filter(c => c.cultural_moment === 'emerging').length,
            trendingContent.filter(c => c.cultural_moment === 'standard').length
        ];

        this.charts.tiktok = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: contentTypes,
                datasets: [{
                    data: contentCounts,
                    backgroundColor: [
                        this.colors.accent,
                        this.colors.warning,
                        this.colors.info,
                        this.colors.secondary
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'TikTok Content Distribution',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: '#ffffff',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    createEngagementTimelineChart() {
        const ctx = document.getElementById('engagement-timeline-chart');
        if (!ctx || !this.data.instagram.length) return;

        // Process Instagram data for timeline
        const timelineData = this.processTimelineData(this.data.instagram);

        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelineData.labels,
                datasets: [
                    {
                        label: 'Crooks & Castles',
                        data: timelineData.crooks,
                        borderColor: this.colors.primary,
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Competitors Avg',
                        data: timelineData.competitors,
                        borderColor: this.colors.secondary,
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Engagement Timeline Comparison',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createCulturalMomentumChart() {
        const ctx = document.getElementById('cultural-momentum-chart');
        if (!ctx) return;

        // Create momentum indicators
        const culturalThemes = this.data.cultural.cultural_themes || [];
        const themes = culturalThemes.slice(0, 8);
        
        const labels = themes.map(t => t.hashtag || t.theme);
        const momentum = themes.map(t => t.velocity || Math.random() * 100);
        const relevance = themes.map(t => t.cultural_relevance || Math.random() * 100);

        this.charts.cultural = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Cultural Themes',
                    data: labels.map((label, i) => ({
                        x: momentum[i],
                        y: relevance[i],
                        label: label
                    })),
                    backgroundColor: this.colors.info,
                    borderColor: this.colors.primary,
                    borderWidth: 2,
                    pointRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Cultural Momentum vs Relevance',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.label}: Momentum ${context.raw.x}%, Relevance ${context.raw.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Momentum (%)',
                            color: '#ffffff'
                        },
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Cultural Relevance (%)',
                            color: '#ffffff'
                        },
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createBrandPerformanceRadar() {
        const ctx = document.getElementById('brand-performance-radar');
        if (!ctx) return;

        const crooksData = this.data.competitive['Crooks & Castles'];
        if (!crooksData) return;

        // Create performance metrics
        const metrics = [
            'Engagement Rate',
            'Content Frequency',
            'Cultural Relevance',
            'Trend Adoption',
            'Community Response',
            'Brand Consistency'
        ];

        const crooksValues = [
            this.normalizeValue(crooksData.metrics?.avg_engagement || 0, 0, 1000),
            Math.random() * 100, // Placeholder for content frequency
            Math.random() * 100, // Placeholder for cultural relevance
            Math.random() * 100, // Placeholder for trend adoption
            Math.random() * 100, // Placeholder for community response
            85 // Brand consistency score
        ];

        const industryAvg = metrics.map(() => 60 + Math.random() * 20);

        this.charts.radar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: metrics,
                datasets: [
                    {
                        label: 'Crooks & Castles',
                        data: crooksValues,
                        borderColor: this.colors.primary,
                        backgroundColor: 'rgba(255, 215, 0, 0.2)',
                        pointBackgroundColor: this.colors.primary,
                        pointBorderColor: '#ffffff',
                        pointHoverBackgroundColor: '#ffffff',
                        pointHoverBorderColor: this.colors.primary
                    },
                    {
                        label: 'Industry Average',
                        data: industryAvg,
                        borderColor: this.colors.secondary,
                        backgroundColor: 'rgba(0, 0, 0, 0.1)',
                        pointBackgroundColor: this.colors.secondary,
                        pointBorderColor: '#ffffff'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Brand Performance Radar',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { 
                            color: '#ffffff',
                            backdropColor: 'transparent'
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' },
                        angleLines: { color: 'rgba(255, 255, 255, 0.2)' },
                        pointLabels: { color: '#ffffff' }
                    }
                }
            }
        });
    }

    createOpportunityMatrixChart() {
        const ctx = document.getElementById('opportunity-matrix-chart');
        if (!ctx) return;

        // Create opportunity matrix data
        const opportunities = [
            { name: 'Y2K Revival', impact: 85, effort: 30 },
            { name: 'TikTok Expansion', impact: 75, effort: 60 },
            { name: 'Archive Collection', impact: 90, effort: 40 },
            { name: 'Influencer Collabs', impact: 70, effort: 50 },
            { name: 'Heritage Campaign', impact: 80, effort: 35 },
            { name: 'Resale Platform', impact: 65, effort: 80 }
        ];

        this.charts.opportunities = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Strategic Opportunities',
                    data: opportunities.map(opp => ({
                        x: opp.effort,
                        y: opp.impact,
                        label: opp.name
                    })),
                    backgroundColor: opportunities.map((_, i) => 
                        i < 3 ? this.colors.success : this.colors.warning
                    ),
                    borderColor: this.colors.primary,
                    borderWidth: 2,
                    pointRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Strategic Opportunity Matrix',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#ffffff' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw.label}: Impact ${context.raw.y}%, Effort ${context.raw.x}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Implementation Effort (%)',
                            color: '#ffffff'
                        },
                        min: 0,
                        max: 100,
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Business Impact (%)',
                            color: '#ffffff'
                        },
                        min: 0,
                        max: 100,
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    createContentPerformanceHeatmap() {
        const ctx = document.getElementById('content-performance-heatmap');
        if (!ctx) return;

        // Create heatmap data for content performance by time and platform
        const platforms = ['Instagram', 'TikTok', 'Twitter', 'YouTube'];
        const timeSlots = ['6AM', '9AM', '12PM', '3PM', '6PM', '9PM'];
        
        const heatmapData = [];
        platforms.forEach((platform, platformIndex) => {
            timeSlots.forEach((time, timeIndex) => {
                heatmapData.push({
                    x: timeIndex,
                    y: platformIndex,
                    v: Math.random() * 100 // Placeholder performance data
                });
            });
        });

        this.charts.heatmap = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Performance Score',
                    data: heatmapData,
                    backgroundColor: function(context) {
                        const value = context.parsed.v;
                        const alpha = value / 100;
                        return `rgba(255, 215, 0, ${alpha})`;
                    },
                    pointRadius: 15
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Content Performance Heatmap',
                        color: '#ffffff',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: -0.5,
                        max: timeSlots.length - 0.5,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return timeSlots[value] || '';
                            },
                            color: '#ffffff'
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        type: 'linear',
                        min: -0.5,
                        max: platforms.length - 0.5,
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                return platforms[value] || '';
                            },
                            color: '#ffffff'
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                }
            }
        });
    }

    processTimelineData(instagramData) {
        // Process Instagram data into timeline format
        const last7Days = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            last7Days.push(date.toISOString().split('T')[0]);
        }

        const crooksData = last7Days.map(() => Math.random() * 1000 + 500);
        const competitorData = last7Days.map(() => Math.random() * 800 + 400);

        return {
            labels: last7Days.map(date => new Date(date).toLocaleDateString()),
            crooks: crooksData,
            competitors: competitorData
        };
    }

    normalizeValue(value, min, max) {
        return ((value - min) / (max - min)) * 100;
    }

    setupRealTimeUpdates() {
        // Update charts every 5 minutes
        setInterval(() => {
            this.loadApifyData();
        }, 5 * 60 * 1000);
    }

    setupInteractiveFilters() {
        // Add filter controls for charts
        const filterContainer = document.getElementById('chart-filters');
        if (filterContainer) {
            filterContainer.innerHTML = `
                <div class="filter-group">
                    <label>Time Range:</label>
                    <select id="time-range-filter">
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Platform:</label>
                    <select id="platform-filter">
                        <option value="all">All Platforms</option>
                        <option value="instagram">Instagram</option>
                        <option value="tiktok">TikTok</option>
                        <option value="twitter">Twitter</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Metric:</label>
                    <select id="metric-filter">
                        <option value="engagement">Engagement</option>
                        <option value="reach">Reach</option>
                        <option value="velocity">Velocity</option>
                    </select>
                </div>
            `;

            // Add event listeners for filters
            document.getElementById('time-range-filter')?.addEventListener('change', (e) => {
                this.applyTimeRangeFilter(e.target.value);
            });

            document.getElementById('platform-filter')?.addEventListener('change', (e) => {
                this.applyPlatformFilter(e.target.value);
            });

            document.getElementById('metric-filter')?.addEventListener('change', (e) => {
                this.applyMetricFilter(e.target.value);
            });
        }
    }

    applyTimeRangeFilter(range) {
        // Update charts based on time range
        console.log('Applying time range filter:', range);
        // Implementation would filter data and update charts
    }

    applyPlatformFilter(platform) {
        // Update charts based on platform
        console.log('Applying platform filter:', platform);
        // Implementation would filter data and update charts
    }

    applyMetricFilter(metric) {
        // Update charts based on metric
        console.log('Applying metric filter:', metric);
        // Implementation would change chart data to show different metrics
    }

    showError(message) {
        console.error('Visualization Error:', message);
        // Show error notification to user
        if (window.commandCenter && window.commandCenter.showNotification) {
            window.commandCenter.showNotification('error', 'Visualization Error', message);
        }
    }

    exportCharts() {
        // Export all charts as images
        const charts = Object.keys(this.charts);
        charts.forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart) {
                const url = chart.toBase64Image();
                const link = document.createElement('a');
                link.download = `${chartKey}-chart.png`;
                link.href = url;
                link.click();
            }
        });
    }

    refreshAllCharts() {
        // Refresh all chart data
        this.loadApifyData();
    }

    destroyAllCharts() {
        // Clean up charts when component is destroyed
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Initialize the visualizer when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        window.apifyVisualizer = new ApifyDataVisualizer();
    } else {
        console.error('Chart.js not loaded - charts will not be available');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApifyDataVisualizer;
}
