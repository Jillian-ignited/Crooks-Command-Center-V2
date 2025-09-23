"""
Data Freshness and Source Validation Module
Tracks data sources, timestamps, and freshness indicators for all intelligence data
Ensures users can validate the reliability and currency of competitive insights
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class DataFreshnessValidator:
    def __init__(self):
        self.data_sources = self.get_data_sources()
        self.freshness_thresholds = {
            'real_time': timedelta(hours=1),
            'fresh': timedelta(hours=24),
            'current': timedelta(days=3),
            'aging': timedelta(days=7),
            'stale': timedelta(days=30)
        }
    
    def get_data_sources(self):
        """Get all data sources with metadata"""
        sources = []
        
        # Check Instagram scraper data
        instagram_path = 'uploads/intel/dataset_instagram-hashtag-scraper_2025-09-21_13-10-57-668.jsonl'
        if os.path.exists(instagram_path):
            stat = os.stat(instagram_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Count records
            record_count = 0
            with open(instagram_path, 'r') as f:
                for line in f:
                    if line.strip():
                        record_count += 1
            
            sources.append({
                'name': 'Instagram Hashtag Scraper',
                'source_type': 'Apify Scraper',
                'file_path': instagram_path,
                'last_updated': modified_time,
                'record_count': record_count,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'data_range': 'September 21, 2025',
                'collection_method': 'Automated hashtag scraping',
                'reliability': 'High',
                'coverage': 'Crooks & Castles and heritage brand hashtags'
            })
        
        # Check TikTok scraper data
        tiktok_path = 'uploads/intel/dataset_tiktok-scraper_2025-09-21_13-33-25-969.jsonl'
        if os.path.exists(tiktok_path):
            stat = os.stat(tiktok_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            record_count = 0
            with open(tiktok_path, 'r') as f:
                for line in f:
                    if line.strip():
                        record_count += 1
            
            sources.append({
                'name': 'TikTok Content Scraper',
                'source_type': 'Apify Scraper',
                'file_path': tiktok_path,
                'last_updated': modified_time,
                'record_count': record_count,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'data_range': 'September 21, 2025',
                'collection_method': 'Automated TikTok content scraping',
                'reliability': 'High',
                'coverage': 'Streetwear and fashion content'
            })
        
        # Check competitive data
        competitive_path = 'uploads/intel/instagram_competitive_data.jsonl'
        if os.path.exists(competitive_path):
            stat = os.stat(competitive_path)
            file_size = stat.st_size
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            record_count = 0
            with open(competitive_path, 'r') as f:
                for line in f:
                    if line.strip():
                        record_count += 1
            
            sources.append({
                'name': 'Competitive Intelligence Data',
                'source_type': 'Aggregated Scraper Data',
                'file_path': competitive_path,
                'last_updated': modified_time,
                'record_count': record_count,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'data_range': 'Multi-platform competitive analysis',
                'collection_method': 'Cross-platform brand monitoring',
                'reliability': 'High',
                'coverage': '17 major streetwear brands'
            })
        
        return sources
    
    def get_freshness_status(self, last_updated):
        """Determine freshness status based on timestamp"""
        now = datetime.now()
        age = now - last_updated
        
        if age <= self.freshness_thresholds['real_time']:
            return {'status': 'real_time', 'color': '#00ff00', 'label': 'Real-time'}
        elif age <= self.freshness_thresholds['fresh']:
            return {'status': 'fresh', 'color': '#90EE90', 'label': 'Fresh'}
        elif age <= self.freshness_thresholds['current']:
            return {'status': 'current', 'color': '#FFD700', 'label': 'Current'}
        elif age <= self.freshness_thresholds['aging']:
            return {'status': 'aging', 'color': '#FFA500', 'label': 'Aging'}
        else:
            return {'status': 'stale', 'color': '#FF6B6B', 'label': 'Stale'}
    
    def validate_data_quality(self):
        """Validate data quality and completeness"""
        validation_results = []
        
        for source in self.data_sources:
            freshness = self.get_freshness_status(source['last_updated'])
            age_hours = (datetime.now() - source['last_updated']).total_seconds() / 3600
            
            # Quality score based on freshness, size, and record count
            quality_score = 100
            
            # Deduct points for age
            if age_hours > 24:
                quality_score -= min(30, (age_hours - 24) / 24 * 10)
            
            # Deduct points for small datasets
            if source['record_count'] < 10:
                quality_score -= 20
            elif source['record_count'] < 50:
                quality_score -= 10
            
            # Deduct points for very small files
            if source['file_size_mb'] < 0.1:
                quality_score -= 15
            
            quality_score = max(0, round(quality_score))
            
            validation_results.append({
                'source_name': source['name'],
                'freshness_status': freshness,
                'age_hours': round(age_hours, 1),
                'quality_score': quality_score,
                'record_count': source['record_count'],
                'file_size_mb': source['file_size_mb'],
                'last_updated': source['last_updated'].strftime('%Y-%m-%d %H:%M:%S'),
                'reliability': source['reliability'],
                'coverage': source['coverage'],
                'collection_method': source['collection_method']
            })
        
        return validation_results
    
    def get_data_health_summary(self):
        """Get overall data health summary"""
        validation_results = self.validate_data_quality()
        
        if not validation_results:
            return {
                'overall_status': 'No Data',
                'average_quality': 0,
                'total_sources': 0,
                'fresh_sources': 0,
                'stale_sources': 0,
                'total_records': 0,
                'last_refresh': 'Never'
            }
        
        total_sources = len(validation_results)
        fresh_sources = len([r for r in validation_results if r['freshness_status']['status'] in ['real_time', 'fresh', 'current']])
        stale_sources = len([r for r in validation_results if r['freshness_status']['status'] == 'stale'])
        average_quality = sum(r['quality_score'] for r in validation_results) / total_sources
        total_records = sum(r['record_count'] for r in validation_results)
        
        # Determine overall status
        if average_quality >= 90 and fresh_sources == total_sources:
            overall_status = 'Excellent'
        elif average_quality >= 75 and stale_sources == 0:
            overall_status = 'Good'
        elif average_quality >= 60:
            overall_status = 'Fair'
        else:
            overall_status = 'Poor'
        
        # Get most recent update
        most_recent = max(validation_results, key=lambda x: x['age_hours'])
        
        return {
            'overall_status': overall_status,
            'average_quality': round(average_quality, 1),
            'total_sources': total_sources,
            'fresh_sources': fresh_sources,
            'stale_sources': stale_sources,
            'total_records': total_records,
            'last_refresh': most_recent['last_updated'],
            'data_coverage': f"{total_records:,} posts across {total_sources} sources"
        }
    
    def get_source_recommendations(self):
        """Get recommendations for data source improvements"""
        validation_results = self.validate_data_quality()
        recommendations = []
        
        for result in validation_results:
            if result['age_hours'] > 48:
                recommendations.append({
                    'priority': 'High',
                    'action': f"Refresh {result['source_name']} data",
                    'reason': f"Data is {result['age_hours']:.1f} hours old",
                    'impact': 'Data freshness and accuracy'
                })
            
            if result['record_count'] < 20:
                recommendations.append({
                    'priority': 'Medium',
                    'action': f"Expand {result['source_name']} collection",
                    'reason': f"Only {result['record_count']} records available",
                    'impact': 'Statistical significance and insights'
                })
            
            if result['quality_score'] < 70:
                recommendations.append({
                    'priority': 'Medium',
                    'action': f"Improve {result['source_name']} quality",
                    'reason': f"Quality score: {result['quality_score']}/100",
                    'impact': 'Analysis reliability and confidence'
                })
        
        # Add general recommendations
        if len(validation_results) < 3:
            recommendations.append({
                'priority': 'Low',
                'action': 'Add additional data sources',
                'reason': 'Limited source diversity',
                'impact': 'Comprehensive competitive intelligence'
            })
        
        return recommendations

# API functions for integration
def get_data_freshness():
    """Get data freshness validation for API"""
    try:
        validator = DataFreshnessValidator()
        return {
            'validation_results': validator.validate_data_quality(),
            'health_summary': validator.get_data_health_summary(),
            'recommendations': validator.get_source_recommendations(),
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': f'Data validation error: {str(e)}',
            'validation_results': [],
            'health_summary': {'overall_status': 'Error'},
            'recommendations': [],
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def get_source_metadata():
    """Get detailed source metadata for API"""
    try:
        validator = DataFreshnessValidator()
        return {
            'sources': validator.data_sources,
            'freshness_thresholds': {k: str(v) for k, v in validator.freshness_thresholds.items()},
            'total_sources': len(validator.data_sources)
        }
    except Exception as e:
        return {
            'error': f'Source metadata error: {str(e)}',
            'sources': [],
            'freshness_thresholds': {},
            'total_sources': 0
        }

if __name__ == "__main__":
    # Test data freshness validation
    freshness_data = get_data_freshness()
    print("=== DATA FRESHNESS VALIDATION ===")
    print(f"Overall Status: {freshness_data['health_summary']['overall_status']}")
    print(f"Average Quality: {freshness_data['health_summary']['average_quality']}/100")
    print(f"Total Sources: {freshness_data['health_summary']['total_sources']}")
    print(f"Fresh Sources: {freshness_data['health_summary']['fresh_sources']}")
    print(f"Total Records: {freshness_data['health_summary']['total_records']:,}")
    print(f"Last Refresh: {freshness_data['health_summary']['last_refresh']}")
    
    print("\n=== SOURCE DETAILS ===")
    for result in freshness_data['validation_results']:
        print(f"{result['source_name']:25} | {result['freshness_status']['label']:10} | {result['quality_score']:3}/100 | {result['record_count']:4} records | {result['age_hours']:5.1f}h old")
    
    print(f"\n=== RECOMMENDATIONS ({len(freshness_data['recommendations'])}) ===")
    for rec in freshness_data['recommendations']:
        print(f"{rec['priority']:6} | {rec['action']:40} | {rec['reason']}")
