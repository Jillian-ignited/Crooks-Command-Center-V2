/**
 * Frontend JSON Formatter Fix for Crooks Command Center V2
 * 
 * This script fixes common JSON formatting issues in the frontend:
 * 1. Ensures proper JSON parsing of API responses
 * 2. Adds proper formatting for JSON display elements
 * 3. Fixes escaped quotes and special characters
 * 4. Adds syntax highlighting for JSON display
 * 
 * Usage:
 * 1. Save this file as FRONTEND_JSON_FORMATTER.js
 * 2. Run: node FRONTEND_JSON_FORMATTER.js <path-to-html-file>
 */

const fs = require('fs');
const path = require('path');

// Check if filename is provided
if (process.argv.length < 3) {
  console.error('Please provide the path to the HTML file');
  console.error('Usage: node FRONTEND_JSON_FORMATTER.js <path-to-html-file>');
  process.exit(1);
}

// Get the HTML file path
const htmlFilePath = process.argv[2];

// Check if file exists
if (!fs.existsSync(htmlFilePath)) {
  console.error(`File not found: ${htmlFilePath}`);
  process.exit(1);
}

// Read the HTML file
let htmlContent = fs.readFileSync(htmlFilePath, 'utf8');

console.log('Fixing JSON formatting issues in frontend...');

// 1. Fix JSON parsing in fetch responses
htmlContent = htmlContent.replace(
  /fetch\([^)]+\)\.then\(\s*response\s*=>\s*response\.text\(\)\s*\)/g,
  'fetch($&).then(response => response.json())'
);

// 2. Add proper JSON.parse for any text responses
htmlContent = htmlContent.replace(
  /\.then\(\s*data\s*=>\s*\{(?!\s*try\s*\{)/g,
  '.then(data => {\n' +
  '  try {\n' +
  '    if (typeof data === "string") data = JSON.parse(data);\n' +
  '  } catch (e) { console.error("JSON parse error:", e); }\n'
);

// 3. Fix escaped quotes in JSON display
htmlContent = htmlContent.replace(
  /JSON\.stringify\(([^,)]+)\)/g,
  'JSON.stringify($1, null, 2)'
);

// 4. Add JSON syntax highlighting CSS
const jsonSyntaxHighlightingCSS = `
<style>
/* JSON Syntax Highlighting */
.json-formatter {
  font-family: monospace;
  white-space: pre;
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
  overflow: auto;
  max-height: 400px;
}
.json-formatter .json-key { color: #0451a5; }
.json-formatter .json-string { color: #a31515; }
.json-formatter .json-number { color: #098658; }
.json-formatter .json-boolean { color: #0000ff; }
.json-formatter .json-null { color: #0000ff; }
</style>
`;

// Insert the CSS before the closing </head> tag
htmlContent = htmlContent.replace('</head>', `${jsonSyntaxHighlightingCSS}\n</head>`);

// 5. Add JSON formatter function
const jsonFormatterFunction = `
<script>
// JSON Formatter function
function formatJSON(json) {
  if (typeof json === 'string') {
    try {
      json = JSON.parse(json);
    } catch (e) {
      return json;
    }
  }
  
  const formatted = JSON.stringify(json, null, 2)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/("(\\\\u[a-zA-Z0-9]{4}|\\\\[^u]|[^\\\\"])*"(\\s*:)?|\\b(true|false|null)\\b|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?)/g, 
      function (match) {
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
      }
    );
  
  return formatted;
}

// Find all JSON display elements and format them
document.addEventListener('DOMContentLoaded', function() {
  // Format any pre-existing JSON elements
  document.querySelectorAll('.json-display').forEach(el => {
    try {
      const jsonData = JSON.parse(el.textContent);
      el.innerHTML = formatJSON(jsonData);
      el.classList.add('json-formatter');
    } catch (e) {
      console.error('Error formatting JSON:', e);
    }
  });
  
  // Add observer to format dynamically added JSON elements
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.nodeType === 1) { // Element node
          node.querySelectorAll('.json-display').forEach(el => {
            try {
              const jsonData = JSON.parse(el.textContent);
              el.innerHTML = formatJSON(jsonData);
              el.classList.add('json-formatter');
            } catch (e) {
              // Ignore parsing errors for non-JSON content
            }
          });
        }
      });
    });
  });
  
  observer.observe(document.body, { childList: true, subtree: true });
});
</script>
`;

// Insert the formatter function before the closing </body> tag
htmlContent = htmlContent.replace('</body>', `${jsonFormatterFunction}\n</body>`);

// 6. Fix any raw JSON display elements
htmlContent = htmlContent.replace(
  /<pre>(\s*\{\s*"|\s*\[\s*\{)/g,
  '<pre class="json-display">$1'
);

// 7. Fix any JSON.stringify outputs that are directly inserted into the DOM
htmlContent = htmlContent.replace(
  /\.innerHTML\s*=\s*JSON\.stringify\(([^,)]+)\)/g,
  '.innerHTML = formatJSON($1)'
);

// Create a backup of the original file
const backupFilePath = `${htmlFilePath}.json-backup`;
fs.writeFileSync(backupFilePath, fs.readFileSync(htmlFilePath));
console.log(`Created backup of original file at ${backupFilePath}`);

// Write the fixed content back to the file
fs.writeFileSync(htmlFilePath, htmlContent);
console.log(`Updated ${htmlFilePath} with fixed JSON formatting`);

// Create a report of changes
const reportFilePath = path.join(path.dirname(htmlFilePath), 'json_formatting_fixes_report.txt');
fs.writeFileSync(reportFilePath, `JSON Formatting Fixes Report
==========================

Original file: ${htmlFilePath}
Backup file: ${backupFilePath}
Date: ${new Date().toISOString()}

Changes made:
1. Fixed JSON parsing in fetch responses
2. Added proper JSON.parse for text responses
3. Fixed JSON.stringify to include formatting
4. Added JSON syntax highlighting CSS
5. Added JSON formatter function
6. Fixed raw JSON display elements
7. Fixed JSON.stringify outputs directly inserted into the DOM

These changes will ensure that:
- All API responses are properly parsed as JSON
- JSON data is properly formatted and displayed
- JSON syntax is highlighted for better readability
- Escaped quotes and special characters are properly handled
`);

console.log(`Created report at ${reportFilePath}`);
console.log('All JSON formatting issues have been fixed successfully!');
