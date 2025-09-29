/ API Path Fixer
// This script fixes API paths by adding the /api/ prefix to all fetch calls

(function() {
  // Store the original fetch function
  const originalFetch = window.fetch;
  
  // Override the fetch function
  window.fetch = function(url, options) {
    // Only modify URLs that are relative and don't already start with /api/
    if (typeof url === 'string' && url.startsWith('/') && !url.startsWith('/api/') && !url.startsWith('/_next/')) {
      // Add /api/ prefix
      url = '/api' + url;
      console.log('Fixed API path:', url);
    }
    
    // Call the original fetch with the modified URL
    return originalFetch.call(this, url, options);
  };
  
  console.log('API path fixer installed');
})();
