"""
Enhanced Data Loading System for Automatic Apify Data Updates
Automatically scans for latest data files and provides data refresh capabilities
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

class ApifyDataManager:
    def __init__(self, data_directory='uploads/intel'):
        self.data_directory = data_directory
        self.supported_patterns = {
            'instagram_hashtag': 'dataset_instagram-hashtag-scraper_*.jsonl',
            'instagram_competitive': 'instagram_competitive_data*.jsonl',
            'tiktok': 'dataset_tiktok-scraper_*.jsonl'
        }
    
    def scan_for_latest_files(self):
        """Automatically scan for the latest Apify data files"""
        latest_files = {}
        
        for data_type, pattern in self.supported_patterns.items():
            file_pattern = os.path.join(self.data_directory, pattern)
            matching_files = glob.glob(file_pattern)
            
            if matching_files:
                # Sort by modification time (newest first)
                latest_file = max(matching_files, key=os.path.getmtime)
                file_info = {
                    'path': latest_file,
                    'filename': os.path.basename(latest_file),
                    'modified': datetime.fromtimestamp(os.path.getmtime(latest_file)),
                    'size_mb': os.path.getsize(latest_file) / (1024 * 1024)
                }
                latest_files[data_type] = file_info
                print(f"✅ Found {data_type}: {file_info['filename']} ({file_info['size_mb']:.1f}MB)")
            else:
                print(f"⚠️  No files found for {data_type} (pattern: {pattern})")
        
        return latest_files
    
    def get_data_freshness_report(self):
        """Generate a report on data freshness and recommendations"""
        latest_files = self.scan_for_latest_files()
        current_time = datetime.now()
        
        report = {
            'scan_time': current_time.isoformat(),
            'total_files_found': len(latest_files),
            'files': latest_files,
            'recommendations': []
        }
        
        for data_type, file_info in latest_files.items():
            age_hours = (current_time - file_info['modified']).total_seconds() / 3600
            
            if age_hours > 168:  # 1 week
                report['recommendations'].append({
                    'type': 'data_refresh_needed',
                    'file': file_info['filename'],
                    'age_hours': age_hours,
                    'message': f"{data_type} data is {age_hours/24:.1f} days old - consider refreshing"
                })
            elif age_hours > 24:  # 1 day
                report['recommendations'].append({
                    'type': 'data_aging',
                    'file': file_info['filename'],
                    'age_hours': age_hours,
                    'message': f"{data_type} data is {age_hours:.1f} hours old - still fresh"
                })
        
        return report
    
    def validate_new_data_file(self, file_path):
        """Validate that a new data file is properly formatted"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Check first few lines
                for i, line in enumerate(f):
                    if i >= 3:  # Check first 3 lines
                        break
                    data = json.loads(line.strip())
                    
                    # Basic validation - should have expected fields
                    if 'caption' not in data and 'text' not in data and 'description' not in data:
                        return False, "Missing text content fields"
            
            return True, "File validation passed"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

# Enhanced data processor functions that use automatic file scanning
def load_latest_apify_data():
    """Load the latest Apify data files automatically"""
    manager = ApifyDataManager()
    latest_files = manager.scan_for_latest_files()
    
    all_data = []
    data_sources = []
    
    for data_type, file_info in latest_files.items():
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                file_data = []
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        data['data_source'] = data_type
                        data['source_file'] = file_info['filename']
                        file_data.append(data)
                
                all_data.extend(file_data)
                data_sources.append({
                    'type': data_type,
                    'filename': file_info['filename'],
                    'records': len(file_data),
                    'last_modified': file_info['modified'].isoformat()
                })
                
                print(f"Loaded {len(file_data)} records from {file_info['filename']}")
        
        except Exception as e:
            print(f"Error loading {file_info['filename']}: {e}")
    
    return all_data, data_sources

def get_data_update_instructions():
    """Provide instructions for updating Apify data"""
    return {
        'automatic_method': {
            'description': 'Upload new files via the web interface',
            'steps': [
                '1. Click "📤 Upload Assets" in the Assets tab',
                '2. Drag your new Apify JSONL files to the upload area',
                '3. Files are automatically categorized as intelligence_data',
                '4. System automatically scans for latest files on next analysis',
                '5. Dashboard refreshes with new data immediately'
            ],
            'supported_formats': [
                'dataset_instagram-hashtag-scraper_YYYY-MM-DD_*.jsonl',
                'dataset_tiktok-scraper_YYYY-MM-DD_*.jsonl', 
                'instagram_competitive_data*.jsonl'
            ]
        },
        'manual_method': {
            'description': 'Replace files directly in the uploads/intel directory',
            'steps': [
                '1. Access your deployment file system',
                '2. Navigate to uploads/intel/ directory',
                '3. Upload new JSONL files (keep original naming pattern)',
                '4. System automatically detects newest files by modification date',
                '5. Restart application or wait for next data refresh cycle'
            ]
        },
        'data_validation': {
            'description': 'Ensure new data files are properly formatted',
            'requirements': [
                'Valid JSONL format (one JSON object per line)',
                'Text content in caption, text, or description fields',
                'Consistent with Apify scraper output format',
                'UTF-8 encoding'
            ]
        }
    }

# Integration function for the main application
def refresh_intelligence_data():
    """Refresh intelligence data with latest files"""
    print("🔄 Refreshing intelligence data...")
    
    # Get data freshness report
    manager = ApifyDataManager()
    freshness_report = manager.get_data_freshness_report()
    
    print(f"📊 Data Freshness Report:")
    print(f"   Files found: {freshness_report['total_files_found']}")
    
    for rec in freshness_report['recommendations']:
        if rec['type'] == 'data_refresh_needed':
            print(f"   ⚠️  {rec['message']}")
        else:
            print(f"   ✅ {rec['message']}")
    
    # Load latest data
    all_data, data_sources = load_latest_apify_data()
    
    print(f"✅ Loaded {len(all_data)} total records from {len(data_sources)} sources")
    
    return {
        'total_records': len(all_data),
        'data_sources': data_sources,
        'freshness_report': freshness_report,
        'last_refresh': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test the enhanced data loading system
    print("=== TESTING ENHANCED DATA LOADING ===")
    
    manager = ApifyDataManager()
    latest_files = manager.scan_for_latest_files()
    
    freshness_report = manager.get_data_freshness_report()
    print(f"\nData Freshness Report:")
    print(f"Total files: {freshness_report['total_files_found']}")
    
    for rec in freshness_report['recommendations']:
        print(f"- {rec['message']}")
    
    print("\nData Update Instructions:")
    instructions = get_data_update_instructions()
    print("Automatic method:", instructions['automatic_method']['description'])
    for step in instructions['automatic_method']['steps']:
        print(f"  {step}")
