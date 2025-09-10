import os
import json
import uuid
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import magic
from colorthief import ColorThief
from werkzeug.utils import secure_filename

class AssetManager:
    def __init__(self, upload_folder, thumbnails_folder, metadata_folder):
        self.upload_folder = upload_folder
        self.thumbnails_folder = thumbnails_folder
        self.metadata_folder = metadata_folder
        
        # KyndVibes brand colors for compliance checking
        self.brand_colors = {
            'deep_teal': (0, 139, 139),
            'vibrant_turquoise': (0, 206, 209),
            'midnight_navy': (27, 41, 81),
            'bright_pink': (255, 20, 147),
            'lime_green': (50, 205, 50),
            'rich_purple': (138, 43, 226),
            'lavender': (213, 189, 228),
            'premium_white': (255, 255, 255),
            'sophisticated_charcoal': (44, 44, 44)
        }
        
        # Campaign templates and asset requirements
        self.campaign_templates = {
            'product_launch': {
                'required_assets': [
                    'hero_image', 'product_shots', 'lifestyle_photos', 
                    'social_media_posts', 'email_header', 'website_banner'
                ],
                'brand_guidelines': ['color_compliance', 'logo_usage', 'typography_check'],
                'formats': {
                    'social_media': {'instagram_post': (1080, 1080), 'instagram_story': (1080, 1920)},
                    'web': {'hero_banner': (1920, 800), 'product_card': (400, 400)},
                    'email': {'header': (600, 200), 'footer': (600, 100)}
                }
            },
            'frequency_collective': {
                'required_assets': [
                    'ambassador_photos', 'ugc_templates', 'recruitment_graphics',
                    'social_media_kit', 'campus_materials'
                ],
                'brand_guidelines': ['authenticity_check', 'diversity_representation', 'brand_voice'],
                'formats': {
                    'social_media': {'ugc_template': (1080, 1080), 'story_template': (1080, 1920)},
                    'print': {'flyer': (8.5, 11), 'poster': (18, 24)}
                }
            },
            'seasonal_drop': {
                'required_assets': [
                    'collection_hero', 'individual_products', 'styling_shots',
                    'countdown_graphics', 'email_campaign', 'website_assets'
                ],
                'brand_guidelines': ['seasonal_color_palette', 'mood_consistency', 'brand_positioning'],
                'formats': {
                    'web': {'collection_banner': (1920, 600), 'product_grid': (300, 400)},
                    'social_media': {'countdown_post': (1080, 1080), 'collection_story': (1080, 1920)}
                }
            }
        }

    def create_thumbnail(self, file_path, filename):
        """Create thumbnail for uploaded asset"""
        try:
            thumbnail_path = os.path.join(self.thumbnails_folder, f"thumb_{filename}")
            
            # Handle different file types
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                # Image thumbnail
                with Image.open(file_path) as img:
                    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    img.save(thumbnail_path, 'JPEG', quality=85)
                    
            elif file_ext == 'pdf':
                # PDF thumbnail (placeholder for now)
                self.create_file_icon_thumbnail(thumbnail_path, 'PDF', '#FF6B6B')
                
            elif file_ext in ['mp4', 'mov']:
                # Video thumbnail (placeholder for now)
                self.create_file_icon_thumbnail(thumbnail_path, 'VIDEO', '#9B59B6')
                
            else:
                # Generic file thumbnail
                self.create_file_icon_thumbnail(thumbnail_path, file_ext.upper(), '#95A5A6')
                
            return f"/static/thumbnails/thumb_{filename}"
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None

    def create_file_icon_thumbnail(self, thumbnail_path, text, color):
        """Create a simple icon thumbnail for non-image files"""
        img = Image.new('RGB', (200, 200), color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), text, fill='white', font=font)
        img.save(thumbnail_path, 'JPEG', quality=85)

    def analyze_brand_compliance(self, file_path, filename):
        """Analyze asset for brand guideline compliance"""
        compliance_report = {
            'overall_score': 0,
            'color_compliance': False,
            'format_compliance': False,
            'size_compliance': False,
            'issues': [],
            'recommendations': []
        }
        
        try:
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                # Image analysis
                with Image.open(file_path) as img:
                    # Check dimensions
                    width, height = img.size
                    
                    # Size compliance check
                    if width >= 1080 and height >= 1080:
                        compliance_report['size_compliance'] = True
                    else:
                        compliance_report['issues'].append(f"Image size {width}x{height} may be too small for social media")
                        compliance_report['recommendations'].append("Minimum 1080x1080 for Instagram posts")
                    
                    # Color analysis
                    try:
                        color_thief = ColorThief(file_path)
                        dominant_colors = color_thief.get_palette(color_count=5)
                        
                        # Check if any dominant colors match brand palette
                        brand_color_found = False
                        for color in dominant_colors:
                            for brand_name, brand_color in self.brand_colors.items():
                                if self.color_distance(color, brand_color) < 50:  # Threshold for similarity
                                    brand_color_found = True
                                    break
                        
                        compliance_report['color_compliance'] = brand_color_found
                        if not brand_color_found:
                            compliance_report['issues'].append("No brand colors detected in image")
                            compliance_report['recommendations'].append("Consider incorporating KyndVibes peacock palette colors")
                            
                    except Exception as e:
                        compliance_report['issues'].append("Could not analyze colors")
            
            # Format compliance
            if file_ext in ['jpg', 'jpeg', 'png']:
                compliance_report['format_compliance'] = True
            else:
                compliance_report['issues'].append(f"File format .{file_ext} may not be optimal for web use")
                compliance_report['recommendations'].append("Consider converting to JPG or PNG for web assets")
            
            # Calculate overall score
            score = 0
            if compliance_report['color_compliance']: score += 40
            if compliance_report['format_compliance']: score += 30
            if compliance_report['size_compliance']: score += 30
            
            compliance_report['overall_score'] = score
            
        except Exception as e:
            compliance_report['issues'].append(f"Analysis error: {str(e)}")
        
        return compliance_report

    def color_distance(self, color1, color2):
        """Calculate Euclidean distance between two RGB colors"""
        return sum([(c1 - c2) ** 2 for c1, c2 in zip(color1, color2)]) ** 0.5

    def save_asset_metadata(self, filename, metadata):
        """Save asset metadata to JSON file"""
        metadata_path = os.path.join(self.metadata_folder, f"{filename}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

    def load_asset_metadata(self, filename):
        """Load asset metadata from JSON file"""
        metadata_path = os.path.join(self.metadata_folder, f"{filename}.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}

    def process_uploaded_asset(self, file_path, original_filename, campaign_tags=None, asset_type=None):
        """Complete processing pipeline for uploaded assets"""
        filename = os.path.basename(file_path)
        
        # Create thumbnail
        thumbnail_url = self.create_thumbnail(file_path, filename)
        
        # Analyze brand compliance
        compliance_report = self.analyze_brand_compliance(file_path, filename)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_type = magic.from_file(file_path, mime=True) if os.path.exists(file_path) else 'unknown'
        
        # Create comprehensive metadata
        metadata = {
            'original_filename': original_filename,
            'upload_date': datetime.now().isoformat(),
            'file_size': file_size,
            'file_type': file_type,
            'thumbnail_url': thumbnail_url,
            'campaign_tags': campaign_tags or [],
            'asset_type': asset_type or 'general',
            'compliance_report': compliance_report,
            'status': 'uploaded',
            'approved': compliance_report['overall_score'] >= 70,
            'usage_rights': 'internal',
            'created_by': 'command_center'
        }
        
        # Save metadata
        self.save_asset_metadata(filename, metadata)
        
        return metadata

    def get_campaign_requirements(self, campaign_type, deliverable_date):
        """Get asset requirements for a specific campaign type"""
        if campaign_type not in self.campaign_templates:
            return None
            
        template = self.campaign_templates[campaign_type].copy()
        
        # Calculate recommended timeline
        days_until_deliverable = (deliverable_date - datetime.now()).days
        
        timeline = {
            'concept_phase': max(1, days_until_deliverable - 14),
            'creation_phase': max(1, days_until_deliverable - 7),
            'review_phase': max(1, days_until_deliverable - 3),
            'final_delivery': days_until_deliverable
        }
        
        template['recommended_timeline'] = timeline
        template['urgency'] = 'high' if days_until_deliverable < 7 else 'medium' if days_until_deliverable < 14 else 'low'
        
        return template

    def analyze_content_gaps(self, campaign_type, existing_assets):
        """Analyze what assets are missing for a campaign"""
        requirements = self.campaign_templates.get(campaign_type, {})
        required_assets = requirements.get('required_assets', [])
        
        existing_types = [asset.get('asset_type', '') for asset in existing_assets]
        missing_assets = [asset for asset in required_assets if asset not in existing_types]
        
        return {
            'required_assets': required_assets,
            'existing_assets': existing_types,
            'missing_assets': missing_assets,
            'completion_percentage': ((len(required_assets) - len(missing_assets)) / len(required_assets)) * 100 if required_assets else 100
        }

    def generate_asset_checklist(self, campaign_type, deliverable_date):
        """Generate a checklist for asset creation"""
        requirements = self.get_campaign_requirements(campaign_type, deliverable_date)
        if not requirements:
            return []
            
        checklist = []
        for asset_type in requirements['required_assets']:
            checklist.append({
                'asset_type': asset_type,
                'status': 'pending',
                'priority': 'high' if requirements['urgency'] == 'high' else 'medium',
                'estimated_hours': self.estimate_creation_time(asset_type),
                'brand_guidelines': requirements['brand_guidelines'],
                'formats_needed': self.get_formats_for_asset(asset_type, requirements)
            })
            
        return checklist

    def estimate_creation_time(self, asset_type):
        """Estimate creation time for different asset types"""
        time_estimates = {
            'hero_image': 4,
            'product_shots': 2,
            'lifestyle_photos': 6,
            'social_media_posts': 1,
            'email_header': 2,
            'website_banner': 3,
            'ugc_templates': 2,
            'collection_hero': 5
        }
        return time_estimates.get(asset_type, 2)

    def get_formats_for_asset(self, asset_type, requirements):
        """Get required formats for specific asset type"""
        formats = requirements.get('formats', {})
        relevant_formats = []
        
        for category, format_specs in formats.items():
            for format_name, dimensions in format_specs.items():
                if asset_type.lower() in format_name.lower() or format_name.lower() in asset_type.lower():
                    relevant_formats.append({
                        'name': format_name,
                        'dimensions': dimensions,
                        'category': category
                    })
                    
        return relevant_formats if relevant_formats else [{'name': 'standard', 'dimensions': (1080, 1080), 'category': 'general'}]

