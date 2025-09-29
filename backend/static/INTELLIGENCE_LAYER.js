// Intelligence Integration Layer
// This script connects data from all modules to provide cross-module insights

const IntelligenceLayer = {
  // Store data from all modules
  _data: {},
  
  // Initialize the intelligence layer
  initialize: async function() {
    console.log('Initializing Intelligence Layer...');
    
    try {
      // Fetch data from key modules
      await Promise.all([
        this._fetchModuleData('intelligence'),
        this._fetchModuleData('shopify'),
        this._fetchModuleData('executive'),
        this._fetchModuleData('content')
      ]);
      
      // Process cross-module insights
      this._generateCrossModuleInsights();
      
      console.log('Intelligence Layer initialized successfully');
      return true;
    } catch (error) {
      console.error('Intelligence Layer initialization failed:', error);
      return false;
    }
  },
  
  // Fetch data for a specific module
  _fetchModuleData: async function(module) {
    try {
      // Define endpoints for each module
      const endpoints = {
        intelligence: ['/api/intelligence/dashboard', '/api/intelligence/summary'],
        shopify: ['/api/shopify/analytics', '/api/shopify/products'],
        executive: ['/api/executive/overview'],
        content: ['/api/content/dashboard']
      };
      
      // Fetch data from all endpoints for this module
      const results = await Promise.all(
        (endpoints[module] || []).map(endpoint => 
          fetch(endpoint)
            .then(res => res.ok ? res.json() : null)
            .catch(err => {
              console.warn(`Failed to fetch ${endpoint}:`, err);
              return null;
            })
        )
      );
      
      // Combine results
      this._data[module] = results.reduce((acc, result) => {
        return result ? {...acc, ...result} : acc;
      }, {});
      
      console.log(`Loaded data for ${module} module`);
      return this._data[module];
    } catch (error) {
      console.error(`Failed to load ${module} data:`, error);
      this._data[module] = {};
      return null;
    }
  },
  
  // Generate cross-module insights
  _generateCrossModuleInsights: function() {
    const insights = [];
    
    // Connect intelligence data with shopify performance
    if (this._data.intelligence && this._data.shopify) {
      // Example: Connect trending topics with product performance
      if (this._data.intelligence.trending_topics && this._data.shopify.analytics?.top_products) {
        insights.push({
          type: 'product_trend_alignment',
          title: 'Product-Trend Alignment',
          description: 'Align product strategy with emerging trends in streetwear market',
          source: ['intelligence', 'shopify']
        });
      }
    }
    
    // Connect content strategy with sales performance
    if (this._data.content && this._data.shopify) {
      insights.push({
        type: 'content_sales_correlation',
        title: 'Content-Sales Correlation',
        description: 'Content strategy should focus on top-performing product categories',
        source: ['content', 'shopify']
      });
    }
    
    // Store insights
    this._data.cross_module_insights = insights;
    console.log(`Generated ${insights.length} cross-module insights`);
  },
  
  // Get data for a specific module
  getModuleData: function(module) {
    return this._data[module] || null;
  },
  
  // Get cross-module insights
  getInsights: function() {
    return this._data.cross_module_insights || [];
  }
};
