from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Any
import uuid
from enum import Enum

class AssetStatus(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class UserRole(Enum):
    ADMIN = "admin"
    BRAND_MANAGER = "brand_manager"
    CREATIVE_DIRECTOR = "creative_director"
    DESIGNER = "designer"
    CONTENT_CREATOR = "content_creator"
    AGENCY_PARTNER = "agency_partner"
    PHOTOGRAPHER = "photographer"
    COPYWRITER = "copywriter"

class CrooksAssetManager:
    """Enhanced Collaborative Asset Management System for Crooks & Castles"""
    
    def __init__(self):
        self.assets_file = 'data/brand_assets.json'
        self.projects_file = 'data/collaborative_projects.json'
        self.users_file = 'data/team_members.json'
        self.workflows_file = 'data/approval_workflows.json'
        self.ensure_data_directory()
        self.load_all_data()
        
        # Crooks & Castles brand asset categories
        self.asset_categories = {
            'logos_branding': {
                'name': 'Logos & Branding',
                'description': 'Primary brand marks, logos, and brand identity elements',
                'icon': '👑',
                'color': '#FFD700',
                'subcategories': ['primary_logo', 'secondary_marks', 'wordmarks', 'icons', 'brand_guidelines']
            },
            'heritage_archive': {
                'name': 'Heritage Archive',
                'description': 'Historical designs, vintage pieces, and archive collections',
                'icon': '📚',
                'color': '#8B4513',
                'subcategories': ['vintage_designs', 'archive_photography', 'historical_campaigns', 'founder_content']
            },
            'product_imagery': {
                'name': 'Product Imagery',
                'description': 'Product photography, lifestyle shots, and e-commerce assets',
                'icon': '📸',
                'color': '#32CD32',
                'subcategories': ['product_photos', 'lifestyle_shots', 'detail_shots', 'model_photography', 'flat_lays']
            },
            'campaign_creative': {
                'name': 'Campaign Creative',
                'description': 'Marketing campaigns, advertisements, and promotional materials',
                'icon': '📢',
                'color': '#FF1493',
                'subcategories': ['print_ads', 'digital_campaigns', 'social_media', 'video_content', 'influencer_kits']
            },
            'collaboration_assets': {
                'name': 'Collaboration Assets',
                'description': 'Artist collaborations, partnerships, and co-branded content',
                'icon': '🤝',
                'color': '#FF6347',
                'subcategories': ['artist_collabs', 'musician_partnerships', 'brand_partnerships', 'limited_editions']
            },
            'cultural_content': {
                'name': 'Cultural Content',
                'description': 'Street culture, lifestyle, and community-focused content',
                'icon': '🏙️',
                'color': '#20B2AA',
                'subcategories': ['street_photography', 'culture_docs', 'community_content', 'event_coverage']
            },
            'design_templates': {
                'name': 'Design Templates',
                'description': 'Reusable design templates and brand-consistent layouts',
                'icon': '🎨',
                'color': '#4B0082',
                'subcategories': ['social_templates', 'print_templates', 'web_templates', 'packaging_templates']
            },
            'video_content': {
                'name': 'Video Content',
                'description': 'Video assets, motion graphics, and multimedia content',
                'icon': '🎬',
                'color': '#DC143C',
                'subcategories': ['brand_videos', 'product_videos', 'behind_scenes', 'tutorials', 'tiktok_content']
            }
        }
        
        # Collaborative project types
        self.project_types = {
            'product_launch': {
                'name': 'Product Launch Campaign',
                'duration_days': 45,
                'required_roles': ['brand_manager', 'creative_director', 'designer', 'photographer'],
                'phases': ['concept', 'design', 'production', 'review', 'launch']
            },
            'seasonal_collection': {
                'name': 'Seasonal Collection',
                'duration_days': 90,
                'required_roles': ['creative_director', 'designer', 'photographer', 'copywriter'],
                'phases': ['research', 'concept', 'design', 'photography', 'marketing', 'launch']
            },
            'collaboration_project': {
                'name': 'Artist Collaboration',
                'duration_days': 60,
                'required_roles': ['brand_manager', 'creative_director', 'designer', 'agency_partner'],
                'phases': ['partnership', 'concept', 'design', 'production', 'marketing', 'launch']
            },
            'heritage_revival': {
                'name': 'Heritage Revival Campaign',
                'duration_days': 30,
                'required_roles': ['brand_manager', 'designer', 'photographer', 'content_creator'],
                'phases': ['archive_research', 'concept', 'design', 'content_creation', 'launch']
            },
            'cultural_moment': {
                'name': 'Cultural Moment Response',
                'duration_days': 7,
                'required_roles': ['content_creator', 'designer', 'brand_manager'],
                'phases': ['trend_analysis', 'concept', 'creation', 'approval', 'publish']
            }
        }
        
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('uploads/assets', exist_ok=True)
        
    def load_all_data(self):
        """Load all data files"""
        self.load_assets()
        self.load_projects()
        self.load_users()
        self.load_workflows()
        
    def load_assets(self):
        """Load brand assets"""
        try:
            if os.path.exists(self.assets_file):
                with open(self.assets_file, 'r') as f:
                    self.assets = json.load(f)
            else:
                self.assets = self.create_default_assets()
                self.save_assets()
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.assets = self.create_default_assets()
            
    def load_projects(self):
        """Load collaborative projects"""
        try:
            if os.path.exists(self.projects_file):
                with open(self.projects_file, 'r') as f:
                    self.projects = json.load(f)
            else:
                self.projects = self.create_default_projects()
                self.save_projects()
        except Exception as e:
            print(f"Error loading projects: {e}")
            self.projects = self.create_default_projects()
            
    def load_users(self):
        """Load team members and collaborators"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = self.create_default_users()
                self.save_users()
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = self.create_default_users()
            
    def load_workflows(self):
        """Load approval workflows"""
        try:
            if os.path.exists(self.workflows_file):
                with open(self.workflows_file, 'r') as f:
                    self.workflows = json.load(f)
            else:
                self.workflows = self.create_default_workflows()
                self.save_workflows()
        except Exception as e:
            print(f"Error loading workflows: {e}")
            self.workflows = self.create_default_workflows()
            
    def save_assets(self):
        """Save assets to file"""
        try:
            with open(self.assets_file, 'w') as f:
                json.dump(self.assets, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving assets: {e}")
            
    def save_projects(self):
        """Save projects to file"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving projects: {e}")
            
    def save_users(self):
        """Save users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving users: {e}")
            
    def save_workflows(self):
        """Save workflows to file"""
        try:
            with open(self.workflows_file, 'w') as f:
                json.dump(self.workflows, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving workflows: {e}")
            
    def create_default_assets(self):
        """Create default Crooks & Castles brand assets"""
        return [
            {
                'id': 'medusa_primary_logo',
                'name': 'Medusa Primary Logo',
                'description': 'Primary Medusa logo - heritage brand mark',
                'category': 'logos_branding',
                'subcategory': 'primary_logo',
                'file_type': 'vector',
                'file_path': '/assets/logos/medusa_primary.svg',
                'thumbnail_path': '/assets/thumbnails/medusa_primary_thumb.jpg',
                'status': AssetStatus.APPROVED.value,
                'created_by': 'creative_director',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': ['medusa', 'primary', 'heritage', 'logo'],
                'usage_rights': 'internal_use',
                'brand_guidelines': {
                    'minimum_size': '20px',
                    'clear_space': '1x logo height',
                    'approved_colors': ['black', 'white', 'gold'],
                    'usage_notes': 'Primary brand mark for all official communications'
                },
                'versions': [
                    {'format': 'svg', 'path': '/assets/logos/medusa_primary.svg'},
                    {'format': 'png', 'path': '/assets/logos/medusa_primary.png'},
                    {'format': 'eps', 'path': '/assets/logos/medusa_primary.eps'}
                ]
            },
            {
                'id': 'crown_icon_set',
                'name': 'Crown Icon Collection',
                'description': 'Secondary crown icons for brand applications',
                'category': 'logos_branding',
                'subcategory': 'icons',
                'file_type': 'vector',
                'file_path': '/assets/icons/crown_collection.svg',
                'thumbnail_path': '/assets/thumbnails/crown_collection_thumb.jpg',
                'status': AssetStatus.APPROVED.value,
                'created_by': 'designer',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': ['crown', 'icons', 'secondary', 'branding'],
                'usage_rights': 'internal_use',
                'brand_guidelines': {
                    'usage_notes': 'Secondary brand elements for supporting applications'
                }
            },
            {
                'id': 'sean_paul_collab_assets',
                'name': 'Sean Paul Collaboration Assets',
                'description': 'Complete asset package for Sean Paul collaboration',
                'category': 'collaboration_assets',
                'subcategory': 'musician_partnerships',
                'file_type': 'package',
                'file_path': '/assets/collaborations/sean_paul/',
                'thumbnail_path': '/assets/thumbnails/sean_paul_collab_thumb.jpg',
                'status': AssetStatus.PUBLISHED.value,
                'created_by': 'agency_partner',
                'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': ['sean_paul', 'collaboration', 'music', 'partnership'],
                'usage_rights': 'limited_license',
                'collaboration_details': {
                    'partner': 'Sean Paul',
                    'contract_end': '2025-12-31',
                    'usage_restrictions': 'Music-related content only',
                    'approval_required': True
                }
            },
            {
                'id': 'archive_medusa_photography',
                'name': 'Archive Medusa Product Photography',
                'description': 'Heritage Medusa pieces product photography for resale market',
                'category': 'product_imagery',
                'subcategory': 'product_photos',
                'file_type': 'photography',
                'file_path': '/assets/photography/archive_medusa/',
                'thumbnail_path': '/assets/thumbnails/archive_medusa_thumb.jpg',
                'status': AssetStatus.APPROVED.value,
                'created_by': 'photographer',
                'created_at': (datetime.now() - timedelta(days=14)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tags': ['medusa', 'archive', 'heritage', 'product', 'resale'],
                'usage_rights': 'full_rights',
                'photography_details': {
                    'photographer': 'Studio Team',
                    'shoot_date': '2025-09-07',
                    'location': 'Studio A',
                    'image_count': 45,
                    'resolution': '4K'
                }
            }
        ]
        
    def create_default_projects(self):
        """Create default collaborative projects"""
        return [
            {
                'id': 'archive_remastered_launch',
                'name': 'Archive Remastered Collection Launch',
                'description': 'Y2K revival archive collection based on cultural intelligence insights',
                'project_type': 'heritage_revival',
                'status': 'active',
                'priority': 'high',
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'created_by': 'brand_manager',
                'team_members': [
                    {'user_id': 'brand_manager_1', 'role': 'brand_manager', 'lead': True},
                    {'user_id': 'creative_director_1', 'role': 'creative_director', 'lead': False},
                    {'user_id': 'designer_1', 'role': 'designer', 'lead': False},
                    {'user_id': 'photographer_1', 'role': 'photographer', 'lead': False}
                ],
                'phases': [
                    {
                        'name': 'Archive Research',
                        'status': 'completed',
                        'start_date': datetime.now().isoformat(),
                        'end_date': (datetime.now() + timedelta(days=5)).isoformat(),
                        'deliverables': ['Archive piece selection', 'Cultural trend analysis']
                    },
                    {
                        'name': 'Concept Development',
                        'status': 'in_progress',
                        'start_date': (datetime.now() + timedelta(days=5)).isoformat(),
                        'end_date': (datetime.now() + timedelta(days=12)).isoformat(),
                        'deliverables': ['Design concepts', 'Brand positioning']
                    },
                    {
                        'name': 'Design Execution',
                        'status': 'pending',
                        'start_date': (datetime.now() + timedelta(days=12)).isoformat(),
                        'end_date': (datetime.now() + timedelta(days=20)).isoformat(),
                        'deliverables': ['Final designs', 'Production files']
                    },
                    {
                        'name': 'Content Creation',
                        'status': 'pending',
                        'start_date': (datetime.now() + timedelta(days=20)).isoformat(),
                        'end_date': (datetime.now() + timedelta(days=27)).isoformat(),
                        'deliverables': ['Product photography', 'Marketing content']
                    },
                    {
                        'name': 'Launch Preparation',
                        'status': 'pending',
                        'start_date': (datetime.now() + timedelta(days=27)).isoformat(),
                        'end_date': (datetime.now() + timedelta(days=30)).isoformat(),
                        'deliverables': ['Launch assets', 'Marketing campaign']
                    }
                ],
                'assets': ['archive_medusa_photography', 'medusa_primary_logo'],
                'budget': 25000,
                'cultural_insights': {
                    'trend_basis': 'Y2K fashion +340% velocity',
                    'target_price': '$25-35',
                    'market_opportunity': 'Heritage revival + resale market strength'
                }
            },
            {
                'id': 'tiktok_strategy_development',
                'name': 'TikTok Platform Strategy Development',
                'description': 'Develop comprehensive TikTok content strategy for Gen Z engagement',
                'project_type': 'cultural_moment',
                'status': 'planning',
                'priority': 'high',
                'start_date': (datetime.now() + timedelta(days=3)).isoformat(),
                'end_date': (datetime.now() + timedelta(days=10)).isoformat(),
                'created_by': 'brand_manager',
                'team_members': [
                    {'user_id': 'content_creator_1', 'role': 'content_creator', 'lead': True},
                    {'user_id': 'brand_manager_1', 'role': 'brand_manager', 'lead': False},
                    {'user_id': 'agency_partner_1', 'role': 'agency_partner', 'lead': False}
                ],
                'cultural_insights': {
                    'trend_basis': 'TikTok streetwear drop content +2.3x growth',
                    'opportunity': 'Zero current presence while competitors gain mindshare',
                    'target_audience': 'Gen Z streetwear enthusiasts'
                }
            }
        ]
        
    def create_default_users(self):
        """Create default team members and collaborators"""
        return [
            {
                'id': 'brand_manager_1',
                'name': 'Brand Strategy Lead',
                'email': 'strategy@crooksandcastles.com',
                'role': UserRole.BRAND_MANAGER.value,
                'department': 'Brand Strategy',
                'permissions': ['view_all', 'edit_strategy', 'approve_campaigns'],
                'active': True,
                'joined_date': '2025-01-01',
                'specialties': ['brand_positioning', 'competitive_analysis', 'strategic_planning']
            },
            {
                'id': 'creative_director_1',
                'name': 'Creative Director',
                'email': 'creative@crooksandcastles.com',
                'role': UserRole.CREATIVE_DIRECTOR.value,
                'department': 'Creative',
                'permissions': ['view_all', 'edit_creative', 'approve_designs'],
                'active': True,
                'joined_date': '2025-01-01',
                'specialties': ['creative_direction', 'brand_identity', 'campaign_development']
            },
            {
                'id': 'designer_1',
                'name': 'Senior Designer',
                'email': 'design@crooksandcastles.com',
                'role': UserRole.DESIGNER.value,
                'department': 'Creative',
                'permissions': ['view_projects', 'edit_designs', 'upload_assets'],
                'active': True,
                'joined_date': '2025-01-15',
                'specialties': ['graphic_design', 'product_design', 'digital_design']
            },
            {
                'id': 'content_creator_1',
                'name': 'Content Creator',
                'email': 'content@crooksandcastles.com',
                'role': UserRole.CONTENT_CREATOR.value,
                'department': 'Marketing',
                'permissions': ['view_projects', 'create_content', 'upload_assets'],
                'active': True,
                'joined_date': '2025-02-01',
                'specialties': ['social_media', 'video_content', 'cultural_trends']
            },
            {
                'id': 'agency_partner_1',
                'name': 'Agency Partner',
                'email': 'partner@agency.com',
                'role': UserRole.AGENCY_PARTNER.value,
                'department': 'External',
                'permissions': ['view_assigned', 'edit_assigned', 'collaborate'],
                'active': True,
                'joined_date': '2025-01-01',
                'specialties': ['campaign_management', 'media_planning', 'partnership_development']
            },
            {
                'id': 'photographer_1',
                'name': 'Brand Photographer',
                'email': 'photo@crooksandcastles.com',
                'role': UserRole.PHOTOGRAPHER.value,
                'department': 'Creative',
                'permissions': ['view_projects', 'upload_photography', 'edit_assigned'],
                'active': True,
                'joined_date': '2025-01-10',
                'specialties': ['product_photography', 'lifestyle_photography', 'brand_imagery']
            }
        ]
        
    def create_default_workflows(self):
        """Create default approval workflows"""
        return {
            'brand_asset_approval': {
                'name': 'Brand Asset Approval',
                'description': 'Standard approval process for brand assets',
                'steps': [
                    {'role': 'designer', 'action': 'create', 'required': True},
                    {'role': 'creative_director', 'action': 'review', 'required': True},
                    {'role': 'brand_manager', 'action': 'approve', 'required': True}
                ],
                'auto_advance': False,
                'notification_enabled': True
            },
            'campaign_approval': {
                'name': 'Campaign Approval',
                'description': 'Approval process for marketing campaigns',
                'steps': [
                    {'role': 'content_creator', 'action': 'create', 'required': True},
                    {'role': 'creative_director', 'action': 'creative_review', 'required': True},
                    {'role': 'brand_manager', 'action': 'brand_review', 'required': True},
                    {'role': 'admin', 'action': 'final_approval', 'required': True}
                ],
                'auto_advance': False,
                'notification_enabled': True
            },
            'collaboration_approval': {
                'name': 'Collaboration Asset Approval',
                'description': 'Special approval for collaboration assets',
                'steps': [
                    {'role': 'agency_partner', 'action': 'create', 'required': True},
                    {'role': 'creative_director', 'action': 'creative_review', 'required': True},
                    {'role': 'brand_manager', 'action': 'brand_review', 'required': True},
                    {'role': 'admin', 'action': 'legal_review', 'required': True},
                    {'role': 'admin', 'action': 'final_approval', 'required': True}
                ],
                'auto_advance': False,
                'notification_enabled': True
            }
        }
        
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new collaborative project"""
        project_id = str(uuid.uuid4())
        
        project = {
            'id': project_id,
            'name': project_data.get('name'),
            'description': project_data.get('description'),
            'project_type': project_data.get('project_type'),
            'status': 'planning',
            'priority': project_data.get('priority', 'medium'),
            'start_date': project_data.get('start_date'),
            'end_date': project_data.get('end_date'),
            'created_by': project_data.get('created_by'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'team_members': project_data.get('team_members', []),
            'phases': project_data.get('phases', []),
            'assets': [],
            'budget': project_data.get('budget', 0),
            'cultural_insights': project_data.get('cultural_insights', {}),
            'collaboration_notes': []
        }
        
        self.projects.append(project)
        self.save_projects()
        return project_id
        
    def add_asset(self, asset_data: Dict[str, Any]) -> str:
        """Add a new brand asset"""
        asset_id = str(uuid.uuid4())
        
        asset = {
            'id': asset_id,
            'name': asset_data.get('name'),
            'description': asset_data.get('description'),
            'category': asset_data.get('category'),
            'subcategory': asset_data.get('subcategory'),
            'file_type': asset_data.get('file_type'),
            'file_path': asset_data.get('file_path'),
            'thumbnail_path': asset_data.get('thumbnail_path'),
            'status': AssetStatus.DRAFT.value,
            'created_by': asset_data.get('created_by'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tags': asset_data.get('tags', []),
            'usage_rights': asset_data.get('usage_rights', 'internal_use'),
            'versions': asset_data.get('versions', []),
            'approval_history': [],
            'collaboration_notes': []
        }
        
        self.assets.append(asset)
        self.save_assets()
        return asset_id
        
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get projects assigned to a specific user"""
        user_projects = []
        for project in self.projects:
            for member in project.get('team_members', []):
                if member.get('user_id') == user_id:
                    user_projects.append(project)
                    break
        return user_projects
        
    def get_assets_by_category(self, category: str) -> List[Dict]:
        """Get assets by category"""
        return [asset for asset in self.assets if asset.get('category') == category]
        
    def get_collaborative_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get collaborative dashboard data for a user"""
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return {}
            
        user_projects = self.get_user_projects(user_id)
        
        # Get pending approvals for user's role
        pending_approvals = []
        for asset in self.assets:
            if asset.get('status') == AssetStatus.IN_REVIEW.value:
                # Check if user's role is next in approval workflow
                workflow = self.get_approval_workflow(asset)
                if workflow and self.is_user_next_approver(user, asset, workflow):
                    pending_approvals.append(asset)
                    
        # Get recent activity
        recent_activity = self.get_recent_activity(user_id, limit=10)
        
        return {
            'user': user,
            'active_projects': [p for p in user_projects if p['status'] == 'active'],
            'pending_approvals': pending_approvals,
            'recent_activity': recent_activity,
            'team_stats': self.get_team_statistics(),
            'cultural_insights': self.get_latest_cultural_insights()
        }
        
    def get_approval_workflow(self, asset: Dict) -> Optional[Dict]:
        """Get appropriate approval workflow for an asset"""
        category = asset.get('category')
        if 'collaboration' in category:
            return self.workflows.get('collaboration_approval')
        elif 'campaign' in category:
            return self.workflows.get('campaign_approval')
        else:
            return self.workflows.get('brand_asset_approval')
            
    def is_user_next_approver(self, user: Dict, asset: Dict, workflow: Dict) -> bool:
        """Check if user is the next approver in workflow"""
        user_role = user.get('role')
        approval_history = asset.get('approval_history', [])
        
        # Find next required step
        for step in workflow.get('steps', []):
            step_completed = any(
                h.get('step_role') == step['role'] 
                for h in approval_history
            )
            if not step_completed and step['role'] == user_role:
                return True
        return False
        
    def get_recent_activity(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent activity for a user"""
        # This would typically query an activity log
        # For now, return sample activity
        return [
            {
                'type': 'asset_uploaded',
                'description': 'Uploaded new product photography',
                'timestamp': datetime.now().isoformat(),
                'asset_id': 'archive_medusa_photography'
            },
            {
                'type': 'project_updated',
                'description': 'Updated Archive Remastered project timeline',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'project_id': 'archive_remastered_launch'
            }
        ]
        
    def get_team_statistics(self) -> Dict[str, Any]:
        """Get team collaboration statistics"""
        active_projects = len([p for p in self.projects if p['status'] == 'active'])
        total_assets = len(self.assets)
        pending_approvals = len([a for a in self.assets if a['status'] == AssetStatus.IN_REVIEW.value])
        
        return {
            'active_projects': active_projects,
            'total_assets': total_assets,
            'pending_approvals': pending_approvals,
            'team_members': len(self.users)
        }
        
    def get_latest_cultural_insights(self) -> Dict[str, Any]:
        """Get latest cultural insights for team context"""
        return {
            'trending_hashtags': ['#y2kfashion (+340%)', '#streetweararchive (+280%)'],
            'cultural_moments': ['Sean Paul collaboration engagement', 'Archive pieces resale strength'],
            'competitive_gaps': ['TikTok platform absence', 'Content frequency below average'],
            'opportunities': ['Archive Remastered timing', 'Y2K revival trend alignment']
        }
        
    def submit_for_approval(self, asset_id: str, user_id: str) -> bool:
        """Submit asset for approval"""
        asset = next((a for a in self.assets if a['id'] == asset_id), None)
        if not asset:
            return False
            
        asset['status'] = AssetStatus.IN_REVIEW.value
        asset['updated_at'] = datetime.now().isoformat()
        
        # Add to approval history
        if 'approval_history' not in asset:
            asset['approval_history'] = []
            
        asset['approval_history'].append({
            'action': 'submitted',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'notes': 'Submitted for approval'
        })
        
        self.save_assets()
        return True
        
    def approve_asset(self, asset_id: str, user_id: str, notes: str = '') -> bool:
        """Approve an asset"""
        asset = next((a for a in self.assets if a['id'] == asset_id), None)
        if not asset:
            return False
            
        user = next((u for u in self.users if u['id'] == user_id), None)
        if not user:
            return False
            
        # Add approval to history
        asset['approval_history'].append({
            'action': 'approved',
            'user_id': user_id,
            'user_role': user['role'],
            'timestamp': datetime.now().isoformat(),
            'notes': notes
        })
        
        # Check if all approvals are complete
        workflow = self.get_approval_workflow(asset)
        if self.is_approval_complete(asset, workflow):
            asset['status'] = AssetStatus.APPROVED.value
        
        asset['updated_at'] = datetime.now().isoformat()
        self.save_assets()
        return True
        
    def is_approval_complete(self, asset: Dict, workflow: Dict) -> bool:
        """Check if all required approvals are complete"""
        approval_history = asset.get('approval_history', [])
        required_roles = [step['role'] for step in workflow.get('steps', []) if step.get('required')]
        
        approved_roles = [
            h.get('user_role') for h in approval_history 
            if h.get('action') == 'approved'
        ]
        
        return all(role in approved_roles for role in required_roles)
