/**
 * Intelligence Integration Layer for Crooks Command Center V2
 * 
 * This module creates a unified intelligence layer that connects data
 * across all modules of the application, ensuring insights and recommendations
 * are pervasive throughout the entire system.
 * 
 * Features:
 * - Cross-module data sharing
 * - Unified recommendation engine
 * - Intelligent signal detection
 * - Consistent insights across all views
 */

// Intelligence Integration Layer
const IntelligenceLayer = (function() {
  // Private data store for intelligence data
  let _dataStore = {
    intelligence: {
      competitors: [],
      trends: [],
      insights: [],
      recommendations: []
    },
    shopify: {
      sales: {},
      products: [],
      customers: {}
    },
    social: {
      sentiment: {},
      engagement: {},
      trends: []
    },
    content: {
      performance: [],
      ideas: []
    },
    executive: {
      kpis: {},
      signals: [],
      recommendations: []
    },
    agency: {
      projects: [],
      deliverables: []
    }
  };

  // Cache for derived insights
  let _insightsCache = {};
  
  // Flag to track if data has been initialized
  let _initialized = false;
  
  // Event system for cross-module communication
  const _events = {};
  
  /**
   * Initialize the intelligence layer by loading data from all modules
   * @returns {Promise} Promise that resolves when all data is loaded
   */
  async function initialize() {
    if (_initialized) return Promise.resolve();
    
    try {
      // Load data from all modules in parallel
      const [
        intelligenceData,
        shopifyData,
        executiveData,
        agencyData,
        contentData,
        socialData
      ] = await Promise.all([
        fetchIntelligenceData(),
        fetchShopifyData(),
        fetchExecutiveData(),
        fetchAgencyData(),
        fetchContentData(),
        fetchSocialData()
      ]);
      
      // Store the data
      _dataStore.intelligence = intelligenceData;
      _dataStore.shopify = shopifyData;
      _dataStore.executive = executiveData;
      _dataStore.agency = agencyData;
      _dataStore.content = contentData;
      _dataStore.social = socialData;
      
      // Generate cross-module insights
      generateCrossModuleInsights();
      
      _initialized = true;
      triggerEvent('initialized', { success: true });
      
      return Promise.resolve();
    } catch (error) {
      console.error('Failed to initialize Intelligence Layer:', error);
      triggerEvent('error', { message: 'Failed to initialize Intelligence Layer', error });
      return Promise.reject(error);
    }
  }
  
  /**
   * Fetch intelligence data from the API
   * @returns {Promise} Promise that resolves with intelligence data
   */
  async function fetchIntelligenceData() {
    try {
      const [dashboard, report, summary, competitors] = await Promise.all([
        fetch('/api/intelligence/dashboard').then(res => res.json()),
        fetch('/api/intelligence/report').then(res => res.json()),
        fetch('/api/intelligence/summary?brands=all').then(res => res.json()),
        fetch('/api/intelligence/competitors').then(res => res.json())
      ]);
      
      return {
        dashboard: dashboard,
        report: report,
        summary: summary,
        competitors: competitors.competitors || [],
        trends: extractTrends(report, summary),
        insights: extractInsights(report, summary, competitors),
        recommendations: extractRecommendations(report)
      };
    } catch (error) {
      console.error('Failed to fetch intelligence data:', error);
      return {
        competitors: [],
        trends: [],
        insights: [],
        recommendations: []
      };
    }
  }
  
  /**
   * Fetch Shopify data from the API
   * @returns {Promise} Promise that resolves with Shopify data
   */
  async function fetchShopifyData() {
    try {
      const [analytics, products, orders, customers] = await Promise.all([
        fetch('/api/shopify/analytics').then(res => res.json()),
        fetch('/api/shopify/products').then(res => res.json()),
        fetch('/api/shopify/orders').then(res => res.json()),
        fetch('/api/shopify/customers').then(res => res.json())
      ]);
      
      return {
        analytics: analytics,
        products: products.products || [],
        orders: orders.orders || [],
        customers: customers.customers || [],
        sales: analytics.analytics?.summary || {}
      };
    } catch (error) {
      console.error('Failed to fetch Shopify data:', error);
      return {
        sales: {},
        products: [],
        orders: [],
        customers: []
      };
    }
  }
  
  /**
   * Fetch executive data from the API
   * @returns {Promise} Promise that resolves with executive data
   */
  async function fetchExecutiveData() {
    try {
      const overview = await fetch('/api/executive/overview').then(res => res.json());
      
      return {
        overview: overview,
        kpis: overview.kpis || {},
        signals: overview.signals || [],
        recommendations: overview.recommendations || []
      };
    } catch (error) {
      console.error('Failed to fetch executive data:', error);
      return {
        kpis: {},
        signals: [],
        recommendations: []
      };
    }
  }
  
  /**
   * Fetch agency data from the API
   * @returns {Promise} Promise that resolves with agency data
   */
  async function fetchAgencyData() {
    try {
      const [dashboard, projects, deliverables] = await Promise.all([
        fetch('/api/agency/dashboard').then(res => res.json()),
        fetch('/api/agency/projects').then(res => res.json()),
        fetch('/api/agency/deliverables').then(res => res.json())
      ]);
      
      return {
        dashboard: dashboard,
        projects: projects.projects || dashboard.current_projects || [],
        deliverables: deliverables.deliverables || dashboard.upcoming_deadlines || [],
        metrics: dashboard.metrics || {}
      };
    } catch (error) {
      console.error('Failed to fetch agency data:', error);
      return {
        projects: [],
        deliverables: [],
        metrics: {}
      };
    }
  }
  
  /**
   * Fetch content data from the API
   * @returns {Promise} Promise that resolves with content data
   */
  async function fetchContentData() {
    try {
      const [dashboard, ideas] = await Promise.all([
        fetch('/api/content/dashboard').then(res => res.json()),
        fetch('/api/content/ideas/generate').then(res => res.json())
      ]);
      
      return {
        dashboard: dashboard,
        performance: dashboard.performance || [],
        ideas: ideas.ideas || [],
        calendar: dashboard.calendar || []
      };
    } catch (error) {
      console.error('Failed to fetch content data:', error);
      return {
        performance: [],
        ideas: [],
        calendar: []
      };
    }
  }
  
  /**
   * Fetch social data from various endpoints
   * @returns {Promise} Promise that resolves with social data
   */
  async function fetchSocialData() {
    try {
      // This would typically come from a social media API
      // For now, we'll extract it from intelligence data
      const summary = await fetch('/api/intelligence/summary?brands=all').then(res => res.json());
      
      return {
        sentiment: extractSentiment(summary),
        engagement: extractEngagement(summary),
        trends: extractSocialTrends(summary)
      };
    } catch (error) {
      console.error('Failed to fetch social data:', error);
      return {
        sentiment: {},
        engagement: {},
        trends: []
      };
    }
  }
  
  /**
   * Extract trends from intelligence data
   * @param {Object} report - Intelligence report data
   * @param {Object} summary - Intelligence summary data
   * @returns {Array} Array of trend objects
   */
  function extractTrends(report, summary) {
    const trends = [];
    
    try {
      // Extract trends from report
      if (report && report.trends) {
        trends.push(...report.trends);
      }
      
      // Extract trends from summary
      if (summary && summary.trends) {
        trends.push(...summary.trends);
      }
      
      // If no explicit trends, derive some from the data
      if (trends.length === 0) {
        if (summary && summary.competitors) {
          // Find fastest growing competitor
          const competitors = summary.competitors.filter(c => c.growth_rate);
          competitors.sort((a, b) => b.growth_rate - a.growth_rate);
          
          if (competitors.length > 0) {
            trends.push({
              name: `${competitors[0].name} Growing Fast`,
              description: `${competitors[0].name} shows ${competitors[0].growth_rate}% growth, fastest among competitors.`,
              impact: 'high',
              category: 'competitor'
            });
          }
        }
      }
      
      return trends;
    } catch (error) {
      console.error('Error extracting trends:', error);
      return [];
    }
  }
  
  /**
   * Extract insights from intelligence data
   * @param {Object} report - Intelligence report data
   * @param {Object} summary - Intelligence summary data
   * @param {Object} competitors - Competitors data
   * @returns {Array} Array of insight objects
   */
  function extractInsights(report, summary, competitors) {
    const insights = [];
    
    try {
      // Extract insights from report
      if (report && report.insights) {
        insights.push(...report.insights);
      }
      
      // Extract insights from summary
      if (summary && summary.insights) {
        insights.push(...summary.insights);
      }
      
      // If no explicit insights, derive some from the data
      if (insights.length === 0 && competitors && competitors.competitors) {
        // Find market share insights
        const totalShare = competitors.competitors.reduce((sum, comp) => sum + (comp.market_share || 0), 0);
        const ourShare = competitors.competitors.find(c => c.is_us)?.market_share || 0;
        
        if (ourShare > 0 && totalShare > 0) {
          const sharePercent = (ourShare / totalShare * 100).toFixed(1);
          insights.push({
            title: 'Market Share Analysis',
            description: `Current market share is ${sharePercent}% among tracked competitors.`,
            category: 'market',
            impact: sharePercent > 15 ? 'positive' : 'neutral'
          });
        }
      }
      
      return insights;
    } catch (error) {
      console.error('Error extracting insights:', error);
      return [];
    }
  }
  
  /**
   * Extract recommendations from intelligence data
   * @param {Object} report - Intelligence report data
   * @returns {Array} Array of recommendation objects
   */
  function extractRecommendations(report) {
    const recommendations = [];
    
    try {
      // Extract recommendations from report
      if (report && report.recommendations) {
        recommendations.push(...report.recommendations);
      }
      
      return recommendations;
    } catch (error) {
      console.error('Error extracting recommendations:', error);
      return [];
    }
  }
  
  /**
   * Extract sentiment data from intelligence summary
   * @param {Object} summary - Intelligence summary data
   * @returns {Object} Sentiment data
   */
  function extractSentiment(summary) {
    try {
      if (summary && summary.sentiment) {
        return summary.sentiment;
      }
      
      // Derive sentiment from competitors if available
      if (summary && summary.competitors) {
        const sentimentData = {
          overall: 0,
          positive: 0,
          negative: 0,
          neutral: 0
        };
        
        let totalMentions = 0;
        
        summary.competitors.forEach(competitor => {
          if (competitor.sentiment) {
            sentimentData.positive += competitor.sentiment.positive || 0;
            sentimentData.negative += competitor.sentiment.negative || 0;
            sentimentData.neutral += competitor.sentiment.neutral || 0;
            totalMentions += competitor.mentions || 0;
          }
        });
        
        if (totalMentions > 0) {
          sentimentData.overall = (sentimentData.positive - sentimentData.negative) / totalMentions;
        }
        
        return sentimentData;
      }
      
      return {
        overall: 0,
        positive: 0,
        negative: 0,
        neutral: 0
      };
    } catch (error) {
      console.error('Error extracting sentiment:', error);
      return {
        overall: 0,
        positive: 0,
        negative: 0,
        neutral: 0
      };
    }
  }
  
  /**
   * Extract engagement data from intelligence summary
   * @param {Object} summary - Intelligence summary data
   * @returns {Object} Engagement data
   */
  function extractEngagement(summary) {
    try {
      if (summary && summary.engagement) {
        return summary.engagement;
      }
      
      // Derive engagement from competitors if available
      if (summary && summary.competitors) {
        const engagementData = {
          total: 0,
          likes: 0,
          comments: 0,
          shares: 0,
          rate: 0
        };
        
        summary.competitors.forEach(competitor => {
          if (competitor.engagement) {
            engagementData.likes += competitor.engagement.likes || 0;
            engagementData.comments += competitor.engagement.comments || 0;
            engagementData.shares += competitor.engagement.shares || 0;
          }
        });
        
        engagementData.total = engagementData.likes + engagementData.comments + engagementData.shares;
        
        return engagementData;
      }
      
      return {
        total: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        rate: 0
      };
    } catch (error) {
      console.error('Error extracting engagement:', error);
      return {
        total: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        rate: 0
      };
    }
  }
  
  /**
   * Extract social trends from intelligence summary
   * @param {Object} summary - Intelligence summary data
   * @returns {Array} Array of social trend objects
   */
  function extractSocialTrends(summary) {
    try {
      if (summary && summary.social_trends) {
        return summary.social_trends;
      }
      
      return [];
    } catch (error) {
      console.error('Error extracting social trends:', error);
      return [];
    }
  }
  
  /**
   * Generate cross-module insights by analyzing data from all modules
   */
  function generateCrossModuleInsights() {
    try {
      const insights = [];
      
      // Connect shopify sales with content performance
      if (_dataStore.shopify.sales && _dataStore.content.performance) {
        const salesTrend = _dataStore.shopify.sales.revenue_growth;
        const topContent = _dataStore.content.performance[0];
        
        if (salesTrend && topContent) {
          insights.push({
            title: 'Content-Sales Correlation',
            description: `Top performing content "${topContent.title}" correlates with ${salesTrend > 0 ? 'positive' : 'negative'} sales trend of ${salesTrend}%.`,
            modules: ['content', 'shopify'],
            impact: salesTrend > 0 ? 'positive' : 'negative'
          });
        }
      }
      
      // Connect intelligence competitors with agency projects
      if (_dataStore.intelligence.competitors && _dataStore.agency.projects) {
        const topCompetitor = _dataStore.intelligence.competitors[0];
        const relevantProjects = _dataStore.agency.projects.filter(p => 
          p.name.toLowerCase().includes('campaign') || 
          p.name.toLowerCase().includes('marketing')
        );
        
        if (topCompetitor && relevantProjects.length > 0) {
          insights.push({
            title: 'Competitive Campaign Alignment',
            description: `${relevantProjects.length} active campaigns should address ${topCompetitor.name}'s market position.`,
            modules: ['intelligence', 'agency'],
            impact: 'strategic'
          });
        }
      }
      
      // Connect social sentiment with executive signals
      if (_dataStore.social.sentiment && _dataStore.executive.signals) {
        const sentiment = _dataStore.social.sentiment.overall;
        
        if (sentiment !== undefined) {
          const sentimentSignal = {
            title: 'Social Sentiment Signal',
            description: `Overall social sentiment is ${sentiment > 0.2 ? 'positive' : sentiment < -0.2 ? 'negative' : 'neutral'} at ${(sentiment * 100).toFixed(1)}%.`,
            type: sentiment > 0.2 ? 'positive' : sentiment < -0.2 ? 'warning' : 'info',
            source: 'social'
          };
          
          _dataStore.executive.signals.push(sentimentSignal);
          
          insights.push({
            title: 'Sentiment-Executive Connection',
            description: `Social sentiment signal added to executive dashboard.`,
            modules: ['social', 'executive'],
            impact: 'operational'
          });
        }
      }
      
      // Store the cross-module insights
      _insightsCache.crossModule = insights;
      
      // Update recommendations based on cross-module insights
      updateRecommendationsFromInsights(insights);
    } catch (error) {
      console.error('Error generating cross-module insights:', error);
    }
  }
  
  /**
   * Update recommendations in all modules based on cross-module insights
   * @param {Array} insights - Cross-module insights
   */
  function updateRecommendationsFromInsights(insights) {
    try {
      insights.forEach(insight => {
        if (!insight.modules || !insight.modules.length) return;
        
        // Create a recommendation based on the insight
        const recommendation = {
          title: insight.title,
          description: insight.description,
          priority: insight.impact === 'positive' ? 'medium' : insight.impact === 'negative' ? 'high' : 'low',
          source: 'intelligence_layer',
          modules: insight.modules
        };
        
        // Add the recommendation to relevant modules
        insight.modules.forEach(module => {
          if (_dataStore[module] && Array.isArray(_dataStore[module].recommendations)) {
            _dataStore[module].recommendations.push(recommendation);
          }
        });
      });
    } catch (error) {
      console.error('Error updating recommendations from insights:', error);
    }
  }
  
  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  function on(event, callback) {
    if (!_events[event]) {
      _events[event] = [];
    }
    
    _events[event].push(callback);
    
    return function unsubscribe() {
      _events[event] = _events[event].filter(cb => cb !== callback);
    };
  }
  
  /**
   * Trigger an event
   * @param {string} event - Event name
   * @param {Object} data - Event data
   */
  function triggerEvent(event, data) {
    if (_events[event]) {
      _events[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }
  
  /**
   * Get intelligence data for a specific module
   * @param {string} module - Module name
   * @returns {Object} Module data with intelligence enhancements
   */
  function getModuleData(module) {
    if (!_initialized) {
      console.warn('Intelligence Layer not initialized. Call initialize() first.');
      return null;
    }
    
    if (!_dataStore[module]) {
      console.warn(`Module "${module}" not found in Intelligence Layer.`);
      return null;
    }
    
    return {
      ..._dataStore[module],
      insights: getInsightsForModule(module),
      recommendations: getRecommendationsForModule(module),
      signals: getSignalsForModule(module)
    };
  }
  
  /**
   * Get insights relevant to a specific module
   * @param {string} module - Module name
   * @returns {Array} Array of insight objects
   */
  function getInsightsForModule(module) {
    const insights = [];
    
    // Add module-specific insights
    if (_dataStore[module] && _dataStore[module].insights) {
      insights.push(..._dataStore[module].insights);
    }
    
    // Add cross-module insights relevant to this module
    if (_insightsCache.crossModule) {
      const relevantInsights = _insightsCache.crossModule.filter(insight => 
        insight.modules && insight.modules.includes(module)
      );
      
      insights.push(...relevantInsights);
    }
    
    return insights;
  }
  
  /**
   * Get recommendations relevant to a specific module
   * @param {string} module - Module name
   * @returns {Array} Array of recommendation objects
   */
  function getRecommendationsForModule(module) {
    const recommendations = [];
    
    // Add module-specific recommendations
    if (_dataStore[module] && _dataStore[module].recommendations) {
      recommendations.push(..._dataStore[module].recommendations);
    }
    
    // Add intelligence recommendations if they're relevant to this module
    if (module !== 'intelligence' && _dataStore.intelligence && _dataStore.intelligence.recommendations) {
      const relevantRecommendations = _dataStore.intelligence.recommendations.filter(rec => 
        !rec.modules || rec.modules.includes(module)
      );
      
      recommendations.push(...relevantRecommendations);
    }
    
    return recommendations;
  }
  
  /**
   * Get signals relevant to a specific module
   * @param {string} module - Module name
   * @returns {Array} Array of signal objects
   */
  function getSignalsForModule(module) {
    const signals = [];
    
    // Add module-specific signals
    if (_dataStore[module] && _dataStore[module].signals) {
      signals.push(..._dataStore[module].signals);
    }
    
    // Add executive signals if they're relevant to this module
    if (module !== 'executive' && _dataStore.executive && _dataStore.executive.signals) {
      const relevantSignals = _dataStore.executive.signals.filter(signal => 
        !signal.modules || signal.modules.includes(module)
      );
      
      signals.push(...relevantSignals);
    }
    
    return signals;
  }
  
  /**
   * Get all intelligence data
   * @returns {Object} Complete intelligence data store
   */
  function getAllData() {
    if (!_initialized) {
      console.warn('Intelligence Layer not initialized. Call initialize() first.');
      return null;
    }
    
    return _dataStore;
  }
  
  /**
   * Get cross-module insights
   * @returns {Array} Array of cross-module insight objects
   */
  function getCrossModuleInsights() {
    return _insightsCache.crossModule || [];
  }
  
  /**
   * Refresh data for a specific module
   * @param {string} module - Module name
   * @returns {Promise} Promise that resolves when the module data is refreshed
   */
  async function refreshModule(module) {
    if (!_dataStore[module]) {
      console.warn(`Module "${module}" not found in Intelligence Layer.`);
      return Promise.reject(new Error(`Module "${module}" not found`));
    }
    
    try {
      let moduleData;
      
      switch (module) {
        case 'intelligence':
          moduleData = await fetchIntelligenceData();
          break;
        case 'shopify':
          moduleData = await fetchShopifyData();
          break;
        case 'executive':
          moduleData = await fetchExecutiveData();
          break;
        case 'agency':
          moduleData = await fetchAgencyData();
          break;
        case 'content':
          moduleData = await fetchContentData();
          break;
        case 'social':
          moduleData = await fetchSocialData();
          break;
        default:
          return Promise.reject(new Error(`Unknown module: ${module}`));
      }
      
      _dataStore[module] = moduleData;
      
      // Regenerate cross-module insights
      generateCrossModuleInsights();
      
      triggerEvent('moduleRefreshed', { module });
      
      return Promise.resolve(moduleData);
    } catch (error) {
      console.error(`Failed to refresh module ${module}:`, error);
      triggerEvent('error', { message: `Failed to refresh module ${module}`, error });
      return Promise.reject(error);
    }
  }
  
  /**
   * Refresh all data
   * @returns {Promise} Promise that resolves when all data is refreshed
   */
  async function refreshAll() {
    try {
      await initialize();
      triggerEvent('refreshed', { success: true });
      return Promise.resolve();
    } catch (error) {
      console.error('Failed to refresh Intelligence Layer:', error);
      triggerEvent('error', { message: 'Failed to refresh Intelligence Layer', error });
      return Promise.reject(error);
    }
  }
  
  // Public API
  return {
    initialize,
    getModuleData,
    getAllData,
    getCrossModuleInsights,
    refreshModule,
    refreshAll,
    on
  };
})();

// Cross-Module Recommendation Engine
const RecommendationEngine = (function() {
  // Private recommendation store
  let _recommendations = [];
  
  // Priority levels
  const PRIORITY = {
    HIGH: 3,
    MEDIUM: 2,
    LOW: 1
  };
  
  /**
   * Initialize the recommendation engine
   * @param {Object} intelligenceData - Data from the Intelligence Layer
   * @returns {Array} Generated recommendations
   */
  function initialize(intelligenceData) {
    _recommendations = [];
    
    if (!intelligenceData) return _recommendations;
    
    try {
      // Generate recommendations from intelligence data
      generateFromIntelligence(intelligenceData.intelligence);
      
      // Generate recommendations from shopify data
      generateFromShopify(intelligenceData.shopify);
      
      // Generate recommendations from social data
      generateFromSocial(intelligenceData.social);
      
      // Generate recommendations from content data
      generateFromContent(intelligenceData.content);
      
      // Generate recommendations from agency data
      generateFromAgency(intelligenceData.agency);
      
      // Generate cross-module recommendations
      generateCrossModuleRecommendations(intelligenceData);
      
      // Sort recommendations by priority
      _recommendations.sort((a, b) => {
        const priorityA = PRIORITY[a.priority.toUpperCase()] || 0;
        const priorityB = PRIORITY[b.priority.toUpperCase()] || 0;
        return priorityB - priorityA;
      });
      
      return _recommendations;
    } catch (error) {
      console.error('Error initializing recommendation engine:', error);
      return [];
    }
  }
  
  /**
   * Generate recommendations from intelligence data
   * @param {Object} intelligence - Intelligence data
   */
  function generateFromIntelligence(intelligence) {
    if (!intelligence) return;
    
    try {
      // Add existing recommendations
      if (intelligence.recommendations && intelligence.recommendations.length > 0) {
        _recommendations.push(...intelligence.recommendations.map(rec => ({
          ...rec,
          source: rec.source || 'intelligence',
          modules: rec.modules || ['intelligence']
        })));
      }
      
      // Generate recommendations from competitors
      if (intelligence.competitors && intelligence.competitors.length > 0) {
        const topCompetitor = intelligence.competitors[0];
        
        if (topCompetitor) {
          _recommendations.push({
            title: 'Competitive Strategy',
            description: `Develop targeted strategy to address ${topCompetitor.name}'s market position.`,
            priority: 'high',
            source: 'intelligence',
            modules: ['intelligence', 'executive']
          });
        }
      }
      
      // Generate recommendations from trends
      if (intelligence.trends && intelligence.trends.length > 0) {
        intelligence.trends.forEach(trend => {
          if (trend.impact === 'high') {
            _recommendations.push({
              title: `Trend Response: ${trend.name}`,
              description: `Develop response strategy for high-impact trend: ${trend.description}`,
              priority: 'high',
              source: 'intelligence',
              modules: ['intelligence', 'executive', 'content']
            });
          }
        });
      }
    } catch (error) {
      console.error('Error generating intelligence recommendations:', error);
    }
  }
  
  /**
   * Generate recommendations from shopify data
   * @param {Object} shopify - Shopify data
   */
  function generateFromShopify(shopify) {
    if (!shopify) return;
    
    try {
      // Generate recommendations from sales data
      if (shopify.sales) {
        const salesTrend = shopify.sales.revenue_growth;
        
        if (salesTrend !== undefined) {
          if (salesTrend < 0) {
            _recommendations.push({
              title: 'Sales Decline Alert',
              description: `Address ${Math.abs(salesTrend).toFixed(1)}% revenue decline with targeted marketing campaign.`,
              priority: 'high',
              source: 'shopify',
              modules: ['shopify', 'executive', 'content']
            });
          } else if (salesTrend > 15) {
            _recommendations.push({
              title: 'Capitalize on Growth',
              description: `Leverage ${salesTrend.toFixed(1)}% revenue growth with expanded inventory and marketing.`,
              priority: 'medium',
              source: 'shopify',
              modules: ['shopify', 'executive']
            });
          }
        }
      }
      
      // Generate recommendations from product data
      if (shopify.products && shopify.products.length > 0) {
        // Find products with low inventory
        const lowInventory = shopify.products.filter(p => p.inventory_quantity < 10);
        
        if (lowInventory.length > 0) {
          _recommendations.push({
            title: 'Inventory Alert',
            description: `${lowInventory.length} products have low inventory levels (<10 units).`,
            priority: 'medium',
            source: 'shopify',
            modules: ['shopify', 'executive']
          });
        }
      }
    } catch (error) {
      console.error('Error generating shopify recommendations:', error);
    }
  }
  
  /**
   * Generate recommendations from social data
   * @param {Object} social - Social data
   */
  function generateFromSocial(social) {
    if (!social) return;
    
    try {
      // Generate recommendations from sentiment data
      if (social.sentiment) {
        const sentiment = social.sentiment.overall;
        
        if (sentiment !== undefined) {
          if (sentiment < -0.2) {
            _recommendations.push({
              title: 'Address Negative Sentiment',
              description: `Develop response strategy for negative social sentiment (${(sentiment * 100).toFixed(1)}%).`,
              priority: 'high',
              source: 'social',
              modules: ['social', 'content', 'executive']
            });
          } else if (sentiment > 0.5) {
            _recommendations.push({
              title: 'Leverage Positive Sentiment',
              description: `Capitalize on strong positive sentiment (${(sentiment * 100).toFixed(1)}%) with user-generated content campaign.`,
              priority: 'medium',
              source: 'social',
              modules: ['social', 'content']
            });
          }
        }
      }
      
      // Generate recommendations from engagement data
      if (social.engagement) {
        const engagementRate = social.engagement.rate;
        
        if (engagementRate !== undefined) {
          if (engagementRate < 1) {
            _recommendations.push({
              title: 'Boost Engagement',
              description: `Implement engagement strategy to improve low engagement rate (${engagementRate.toFixed(1)}%).`,
              priority: 'medium',
              source: 'social',
              modules: ['social', 'content']
            });
          }
        }
      }
    } catch (error) {
      console.error('Error generating social recommendations:', error);
    }
  }
  
  /**
   * Generate recommendations from content data
   * @param {Object} content - Content data
   */
  function generateFromContent(content) {
    if (!content) return;
    
    try {
      // Generate recommendations from performance data
      if (content.performance && content.performance.length > 0) {
        // Find top performing content
        const topContent = content.performance[0];
        
        if (topContent) {
          _recommendations.push({
            title: 'Content Strategy',
            description: `Create more content similar to high-performing "${topContent.title}".`,
            priority: 'medium',
            source: 'content',
            modules: ['content', 'agency']
          });
        }
        
        // Find underperforming content
        const underperforming = content.performance.filter(c => c.engagement_rate < 1);
        
        if (underperforming.length > 0) {
          _recommendations.push({
            title: 'Content Optimization',
            description: `Optimize or archive ${underperforming.length} underperforming content pieces.`,
            priority: 'low',
            source: 'content',
            modules: ['content']
          });
        }
      }
    } catch (error) {
      console.error('Error generating content recommendations:', error);
    }
  }
  
  /**
   * Generate recommendations from agency data
   * @param {Object} agency - Agency data
   */
  function generateFromAgency(agency) {
    if (!agency) return;
    
    try {
      // Generate recommendations from project data
      if (agency.projects && agency.projects.length > 0) {
        // Find projects behind schedule
        const behindSchedule = agency.projects.filter(p => p.progress < 50 && new Date(p.end_date) < new Date(new Date().getTime() + 14 * 24 * 60 * 60 * 1000));
        
        if (behindSchedule.length > 0) {
          _recommendations.push({
            title: 'Project Timeline Alert',
            description: `${behindSchedule.length} projects are behind schedule and approaching deadlines.`,
            priority: 'high',
            source: 'agency',
            modules: ['agency', 'executive']
          });
        }
      }
      
      // Generate recommendations from deliverable data
      if (agency.deliverables && agency.deliverables.length > 0) {
        // Find upcoming deadlines
        const upcomingDeadlines = agency.deliverables.filter(d => {
          const dueDate = new Date(d.due_date);
          const today = new Date();
          const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
          return diffDays <= 3 && diffDays >= 0;
        });
        
        if (upcomingDeadlines.length > 0) {
          _recommendations.push({
            title: 'Upcoming Deadlines',
            description: `${upcomingDeadlines.length} deliverables due within the next 3 days.`,
            priority: 'high',
            source: 'agency',
            modules: ['agency', 'executive']
          });
        }
      }
    } catch (error) {
      console.error('Error generating agency recommendations:', error);
    }
  }
  
  /**
   * Generate cross-module recommendations
   * @param {Object} data - Complete intelligence data
   */
  function generateCrossModuleRecommendations(data) {
    try {
      // Connect shopify sales with content strategy
      if (data.shopify && data.shopify.sales && data.content) {
        const salesTrend = data.shopify.sales.revenue_growth;
        
        if (salesTrend !== undefined) {
          if (salesTrend < 0) {
            _recommendations.push({
              title: 'Content-Sales Strategy',
              description: `Develop targeted content strategy to address ${Math.abs(salesTrend).toFixed(1)}% revenue decline.`,
              priority: 'high',
              source: 'cross_module',
              modules: ['shopify', 'content', 'executive']
            });
          }
        }
      }
      
      // Connect intelligence competitors with agency projects
      if (data.intelligence && data.intelligence.competitors && data.agency && data.agency.projects) {
        const topCompetitor = data.intelligence.competitors[0];
        const relevantProjects = data.agency.projects.filter(p => 
          p.name.toLowerCase().includes('campaign') || 
          p.name.toLowerCase().includes('marketing')
        );
        
        if (topCompetitor && relevantProjects.length > 0) {
          _recommendations.push({
            title: 'Competitive Campaign Alignment',
            description: `Align ${relevantProjects.length} active campaigns with competitive intelligence on ${topCompetitor.name}.`,
            priority: 'medium',
            source: 'cross_module',
            modules: ['intelligence', 'agency', 'content']
          });
        }
      }
      
      // Connect social sentiment with content strategy
      if (data.social && data.social.sentiment && data.content) {
        const sentiment = data.social.sentiment.overall;
        
        if (sentiment !== undefined) {
          if (sentiment < -0.1) {
            _recommendations.push({
              title: 'Content-Sentiment Strategy',
              description: `Develop positive content strategy to address negative social sentiment.`,
              priority: 'high',
              source: 'cross_module',
              modules: ['social', 'content']
            });
          }
        }
      }
    } catch (error) {
      console.error('Error generating cross-module recommendations:', error);
    }
  }
  
  /**
   * Get all recommendations
   * @returns {Array} All recommendations
   */
  function getAll() {
    return _recommendations;
  }
  
  /**
   * Get recommendations for a specific module
   * @param {string} module - Module name
   * @returns {Array} Module-specific recommendations
   */
  function getForModule(module) {
    return _recommendations.filter(rec => 
      !rec.modules || rec.modules.includes(module)
    );
  }
  
  /**
   * Get high priority recommendations
   * @returns {Array} High priority recommendations
   */
  function getHighPriority() {
    return _recommendations.filter(rec => 
      rec.priority === 'high'
    );
  }
  
  // Public API
  return {
    initialize,
    getAll,
    getForModule,
    getHighPriority
  };
})();

// Unified Dashboard Components
const DashboardComponents = (function() {
  /**
   * Create a recommendations component
   * @param {Array} recommendations - Recommendations to display
   * @param {string} containerId - ID of the container element
   * @param {Object} options - Display options
   */
  function createRecommendationsComponent(recommendations, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const defaultOptions = {
      title: 'Recommendations',
      maxItems: 5,
      showPriority: true,
      showSource: false
    };
    
    const settings = { ...defaultOptions, ...options };
    
    // Clear container
    container.innerHTML = '';
    
    // Create title
    const titleEl = document.createElement('h3');
    titleEl.textContent = settings.title;
    container.appendChild(titleEl);
    
    // Create recommendations list
    if (!recommendations || recommendations.length === 0) {
      const noRecs = document.createElement('p');
      noRecs.textContent = 'No recommendations available.';
      container.appendChild(noRecs);
      return;
    }
    
    const list = document.createElement('ul');
    list.className = 'recommendations-list';
    
    // Add recommendations
    recommendations.slice(0, settings.maxItems).forEach(rec => {
      const item = document.createElement('li');
      item.className = `recommendation-item priority-${rec.priority || 'medium'}`;
      
      const title = document.createElement('h4');
      title.textContent = rec.title;
      item.appendChild(title);
      
      const desc = document.createElement('p');
      desc.textContent = rec.description;
      item.appendChild(desc);
      
      if (settings.showPriority && rec.priority) {
        const priority = document.createElement('span');
        priority.className = `priority priority-${rec.priority}`;
        priority.textContent = rec.priority;
        item.appendChild(priority);
      }
      
      if (settings.showSource && rec.source) {
        const source = document.createElement('span');
        source.className = 'source';
        source.textContent = `Source: ${rec.source}`;
        item.appendChild(source);
      }
      
      list.appendChild(item);
    });
    
    container.appendChild(list);
  }
  
  /**
   * Create a signals component
   * @param {Array} signals - Signals to display
   * @param {string} containerId - ID of the container element
   * @param {Object} options - Display options
   */
  function createSignalsComponent(signals, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const defaultOptions = {
      title: 'Signals',
      maxItems: 5,
      showSource: false
    };
    
    const settings = { ...defaultOptions, ...options };
    
    // Clear container
    container.innerHTML = '';
    
    // Create title
    const titleEl = document.createElement('h3');
    titleEl.textContent = settings.title;
    container.appendChild(titleEl);
    
    // Create signals list
    if (!signals || signals.length === 0) {
      const noSignals = document.createElement('p');
      noSignals.textContent = 'No signals detected.';
      container.appendChild(noSignals);
      return;
    }
    
    const list = document.createElement('ul');
    list.className = 'signals-list';
    
    // Add signals
    signals.slice(0, settings.maxItems).forEach(signal => {
      const item = document.createElement('li');
      item.className = `signal-item type-${signal.type || 'info'}`;
      
      const title = document.createElement('h4');
      title.textContent = signal.title;
      item.appendChild(title);
      
      const desc = document.createElement('p');
      desc.textContent = signal.description;
      item.appendChild(desc);
      
      if (settings.showSource && signal.source) {
        const source = document.createElement('span');
        source.className = 'source';
        source.textContent = `Source: ${signal.source}`;
        item.appendChild(source);
      }
      
      list.appendChild(item);
    });
    
    container.appendChild(list);
  }
  
  /**
   * Create an insights component
   * @param {Array} insights - Insights to display
   * @param {string} containerId - ID of the container element
   * @param {Object} options - Display options
   */
  function createInsightsComponent(insights, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const defaultOptions = {
      title: 'Insights',
      maxItems: 5,
      showImpact: true,
      showCategory: true
    };
    
    const settings = { ...defaultOptions, ...options };
    
    // Clear container
    container.innerHTML = '';
    
    // Create title
    const titleEl = document.createElement('h3');
    titleEl.textContent = settings.title;
    container.appendChild(titleEl);
    
    // Create insights list
    if (!insights || insights.length === 0) {
      const noInsights = document.createElement('p');
      noInsights.textContent = 'No insights available.';
      container.appendChild(noInsights);
      return;
    }
    
    const list = document.createElement('ul');
    list.className = 'insights-list';
    
    // Add insights
    insights.slice(0, settings.maxItems).forEach(insight => {
      const item = document.createElement('li');
      item.className = `insight-item impact-${insight.impact || 'neutral'}`;
      
      const title = document.createElement('h4');
      title.textContent = insight.title;
      item.appendChild(title);
      
      const desc = document.createElement('p');
      desc.textContent = insight.description;
      item.appendChild(desc);
      
      if (settings.showImpact && insight.impact) {
        const impact = document.createElement('span');
        impact.className = `impact impact-${insight.impact}`;
        impact.textContent = `Impact: ${insight.impact}`;
        item.appendChild(impact);
      }
      
      if (settings.showCategory && insight.category) {
        const category = document.createElement('span');
        category.className = 'category';
        category.textContent = `Category: ${insight.category}`;
        item.appendChild(category);
      }
      
      list.appendChild(item);
    });
    
    container.appendChild(list);
  }
  
  /**
   * Create a metrics component
   * @param {Object} metrics - Metrics to display
   * @param {string} containerId - ID of the container element
   * @param {Object} options - Display options
   */
  function createMetricsComponent(metrics, containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const defaultOptions = {
      title: 'Metrics',
      columns: 2,
      showTrend: true
    };
    
    const settings = { ...defaultOptions, ...options };
    
    // Clear container
    container.innerHTML = '';
    
    // Create title
    const titleEl = document.createElement('h3');
    titleEl.textContent = settings.title;
    container.appendChild(titleEl);
    
    // Create metrics grid
    if (!metrics || Object.keys(metrics).length === 0) {
      const noMetrics = document.createElement('p');
      noMetrics.textContent = 'No metrics available.';
      container.appendChild(noMetrics);
      return;
    }
    
    const grid = document.createElement('div');
    grid.className = `metrics-grid columns-${settings.columns}`;
    
    // Add metrics
    Object.entries(metrics).forEach(([key, value]) => {
      const item = document.createElement('div');
      item.className = 'metric-item';
      
      const label = document.createElement('div');
      label.className = 'metric-label';
      label.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      item.appendChild(label);
      
      const valueEl = document.createElement('div');
      valueEl.className = 'metric-value';
      
      // Format the value based on type
      if (typeof value === 'number') {
        // Format as currency if key contains revenue, sales, etc.
        if (/revenue|sales|price|cost|value/i.test(key)) {
          valueEl.textContent = new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: 'USD',
            maximumFractionDigits: 0
          }).format(value);
        } 
        // Format as percentage if key contains rate, percentage, etc.
        else if (/rate|percentage|percent|ratio/i.test(key)) {
          valueEl.textContent = `${value.toFixed(1)}%`;
        }
        // Format as number with commas for thousands
        else {
          valueEl.textContent = new Intl.NumberFormat('en-US').format(value);
        }
      } else {
        valueEl.textContent = value;
      }
      
      item.appendChild(valueEl);
      
      // Add trend if available
      if (settings.showTrend && metrics[`${key}_trend`]) {
        const trend = document.createElement('div');
        trend.className = `metric-trend trend-${metrics[`${key}_trend`] > 0 ? 'up' : 'down'}`;
        trend.textContent = `${metrics[`${key}_trend`] > 0 ? '↑' : '↓'} ${Math.abs(metrics[`${key}_trend`]).toFixed(1)}%`;
        item.appendChild(trend);
      }
      
      grid.appendChild(item);
    });
    
    container.appendChild(grid);
  }
  
  // Public API
  return {
    createRecommendationsComponent,
    createSignalsComponent,
    createInsightsComponent,
    createMetricsComponent
  };
})();

// Export the modules
window.IntelligenceLayer = IntelligenceLayer;
window.RecommendationEngine = RecommendationEngine;
window.DashboardComponents = DashboardComponents;

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('Intelligence Integration Layer ready to initialize');
  
  // Add initialization code here if needed
  // Example: IntelligenceLayer.initialize().then(() => { ... });
});
