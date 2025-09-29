/**
 * Cross-Module Recommendation Engine for Crooks Command Center V2
 * 
 * This engine analyzes data from all modules to generate intelligent
 * recommendations that span across different areas of the business.
 * 
 * Features:
 * - Analyzes data from all modules (intelligence, shopify, content, etc.)
 * - Generates recommendations based on cross-module correlations
 * - Prioritizes recommendations based on business impact
 * - Distributes relevant recommendations to each module
 */

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
   * @param {Object} data - Data from all modules
   * @returns {Array} Generated recommendations
   */
  function initialize(data) {
    _recommendations = [];
    
    if (!data) return _recommendations;
    
    try {
      // Generate recommendations from intelligence data
      if (data.intelligence) {
        generateFromIntelligence(data.intelligence);
      }
      
      // Generate recommendations from shopify data
      if (data.shopify) {
        generateFromShopify(data.shopify);
      }
      
      // Generate recommendations from social data
      if (data.social) {
        generateFromSocial(data.social);
      }
      
      // Generate recommendations from content data
      if (data.content) {
        generateFromContent(data.content);
      }
      
      // Generate recommendations from agency data
      if (data.agency) {
        generateFromAgency(data.agency);
      }
      
      // Generate cross-module recommendations
      generateCrossModuleRecommendations(data);
      
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
   * @param {Object} data - Complete data from all modules
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
      
      // Connect shopify customer data with content targeting
      if (data.shopify && data.shopify.customers && data.content) {
        const customers = data.shopify.customers;
        
        if (customers && customers.length > 0) {
          // Find top customer segment
          const segments = {};
          customers.forEach(customer => {
            const segment = customer.segment || 'unknown';
            segments[segment] = (segments[segment] || 0) + 1;
          });
          
          const topSegment = Object.entries(segments).sort((a, b) => b[1] - a[1])[0];
          
          if (topSegment) {
            _recommendations.push({
              title: 'Content Targeting Strategy',
              description: `Develop targeted content for top customer segment: ${topSegment[0]} (${topSegment[1]} customers).`,
              priority: 'medium',
              source: 'cross_module',
              modules: ['shopify', 'content']
            });
          }
        }
      }
      
      // Connect intelligence trends with executive strategy
      if (data.intelligence && data.intelligence.trends && data.executive) {
        const highImpactTrends = data.intelligence.trends.filter(t => t.impact === 'high');
        
        if (highImpactTrends.length > 0) {
          _recommendations.push({
            title: 'Strategic Trend Response',
            description: `Develop executive strategy to address ${highImpactTrends.length} high-impact market trends.`,
            priority: 'high',
            source: 'cross_module',
            modules: ['intelligence', 'executive']
          });
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
  
  /**
   * Get cross-module recommendations
   * @returns {Array} Cross-module recommendations
   */
  function getCrossModuleRecommendations() {
    return _recommendations.filter(rec => 
      rec.source === 'cross_module'
    );
  }
  
  // Public API
  return {
    initialize,
    getAll,
    getForModule,
    getHighPriority,
    getCrossModuleRecommendations
  };
})();

// Export the module
window.RecommendationEngine = RecommendationEngine;

// Initialize when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('Cross-Module Recommendation Engine ready to initialize');
  
  // Add initialization code here if needed
});
