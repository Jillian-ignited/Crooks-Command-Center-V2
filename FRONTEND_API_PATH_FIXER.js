/**
 * Frontend API Path Fixer for Crooks Command Center V2
 * 
 * This script fixes API paths in the frontend HTML file to ensure
 * all API calls use the correct /api/ prefix.
 * 
 * Usage:
 * 1. Save this file as FRONTEND_API_PATH_FIXER.js
 * 2. Run: node FRONTEND_API_PATH_FIXER.js <path-to-html-file>
 */

const fs = require('fs');
const path = require('path');

// Check if filename is provided
if (process.argv.length < 3) {
  console.error('Please provide the path to the HTML file');
  console.error('Usage: node FRONTEND_API_PATH_FIXER.js <path-to-html-file>');
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

// Count original occurrences of API calls
const originalApiCalls = (htmlContent.match(/fetch\(['"]\/[^'"]*['"]/g) || []).length +
                         (htmlContent.match(/axios\.get\(['"]\/[^'"]*['"]/g) || []).length +
                         (htmlContent.match(/axios\.post\(['"]\/[^'"]*['"]/g) || []).length +
                         (htmlContent.match(/url:\s*['"]\/[^'"]*['"]/g) || []).length;

console.log(`Found ${originalApiCalls} API calls without /api/ prefix`);

// Fix fetch calls
htmlContent = htmlContent.replace(/fetch\(['"]\/(?!api\/|static\/|_next\/)/g, 'fetch(\'/api/');

// Fix axios.get calls
htmlContent = htmlContent.replace(/axios\.get\(['"]\/(?!api\/|static\/|_next\/)/g, 'axios.get(\'/api/');

// Fix axios.post calls
htmlContent = htmlContent.replace(/axios\.post\(['"]\/(?!api\/|static\/|_next\/)/g, 'axios.post(\'/api/');

// Fix url: calls
htmlContent = htmlContent.replace(/url:\s*['"]\/(?!api\/|static\/|_next\/)/g, 'url: \'/api/');

// Fix $.ajax calls
htmlContent = htmlContent.replace(/\$\.ajax\(\{\s*url:\s*['"]\/(?!api\/|static\/|_next\/)/g, '$.ajax({ url: \'/api/');

// Fix $.get calls
htmlContent = htmlContent.replace(/\$\.get\(['"]\/(?!api\/|static\/|_next\/)/g, '$.get(\'/api/');

// Fix $.post calls
htmlContent = htmlContent.replace(/\$\.post\(['"]\/(?!api\/|static\/|_next\/)/g, '$.post(\'/api/');

// Fix double slashes in API calls
htmlContent = htmlContent.replace(/\/api\/\//g, '/api/');

// Count fixed occurrences
const fixedApiCalls = (htmlContent.match(/fetch\(['"]\/api\/[^'"]*['"]/g) || []).length +
                      (htmlContent.match(/axios\.get\(['"]\/api\/[^'"]*['"]/g) || []).length +
                      (htmlContent.match(/axios\.post\(['"]\/api\/[^'"]*['"]/g) || []).length +
                      (htmlContent.match(/url:\s*['"]\/api\/[^'"]*['"]/g) || []).length;

console.log(`Fixed ${fixedApiCalls} API calls to include /api/ prefix`);

// Create a backup of the original file
const backupFilePath = `${htmlFilePath}.backup`;
fs.writeFileSync(backupFilePath, fs.readFileSync(htmlFilePath));
console.log(`Created backup of original file at ${backupFilePath}`);

// Write the fixed content back to the file
fs.writeFileSync(htmlFilePath, htmlContent);
console.log(`Updated ${htmlFilePath} with fixed API paths`);

// Create a report of changes
const reportFilePath = path.join(path.dirname(htmlFilePath), 'api_path_fixes_report.txt');
fs.writeFileSync(reportFilePath, `API Path Fixes Report
=====================

Original file: ${htmlFilePath}
Backup file: ${backupFilePath}
Date: ${new Date().toISOString()}

Changes made:
- Found ${originalApiCalls} API calls without /api/ prefix
- Fixed ${fixedApiCalls} API calls to include /api/ prefix
- Fixed any double slashes in API paths

Types of fixes:
- fetch('/endpoint') → fetch('/api/endpoint')
- axios.get('/endpoint') → axios.get('/api/endpoint')
- axios.post('/endpoint') → axios.post('/api/endpoint')
- url: '/endpoint' → url: '/api/endpoint'
- $.ajax({ url: '/endpoint' }) → $.ajax({ url: '/api/endpoint' })
- $.get('/endpoint') → $.get('/api/endpoint')
- $.post('/endpoint') → $.post('/api/endpoint')
- Fixed '/api//' → '/api/'

Note: No changes were made to paths that already had /api/, /static/, or /_next/ prefixes.
`);

console.log(`Created report at ${reportFilePath}`);
console.log('All API paths have been fixed successfully!');
