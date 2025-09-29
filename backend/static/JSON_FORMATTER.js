// JSON Formatter
// This script formats JSON responses for better display in the UI

(function() {
  // Add syntax highlighting styles
  const style = document.createElement('style');
  style.textContent = `
    .json-key { color: #f92672; }
    .json-value { color: #a6e22e; }
    .json-string { color: #e6db74; }
    .json-number { color: #ae81ff; }
    .json-boolean { color: #66d9ef; }
    .json-null { color: #fd971f; }
  `;
  document.head.appendChild(style);
  
  // Function to format JSON with syntax highlighting
  window.formatJSON = function(json) {
    if (typeof json !== 'string') {
      json = JSON.stringify(json, null, 2);
    }
    
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
      let cls = 'json-number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key';
        } else {
          cls = 'json-string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-boolean';
      } else if (/null/.test(match)) {
        cls = 'json-null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
    });
  };
  
  // Find and format any JSON content in the page
  function formatJSONInPage() {
    // Look for elements with raw JSON content
    document.querySelectorAll('pre, code, .json-content').forEach(el => {
      try {
        const text = el.textContent.trim();
        if (text.startsWith('{') || text.startsWith('[')) {
          // Try to parse as JSON
          const json = JSON.parse(text);
          // Format with syntax highlighting
          el.innerHTML = formatJSON(json);
        }
      } catch (e) {
        // Not valid JSON, ignore
      }
    });
  }
  
  // Run formatter when page loads and after any XHR requests
  document.addEventListener('DOMContentLoaded', formatJSONInPage);
  
  // Monitor for DOM changes and format new JSON content
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.addedNodes && mutation.addedNodes.length > 0) {
        formatJSONInPage();
      }
    });
  });
  
  // Start observing the document
  observer.observe(document.body, { childList: true, subtree: true });
  
  console.log('JSON formatter installed');
})();
