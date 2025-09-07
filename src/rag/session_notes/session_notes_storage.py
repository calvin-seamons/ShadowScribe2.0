"""
Session Notes Storage System

Centralized manager for multiple campaign session notes storage systems.
Handles loading/saving campaigns and provides access to campaign-specific storage.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from .session_types import (
    SessionMetadata, ProcessedSession, SessionEntity,
    QueryEngineResult, SessionNotesQueryPerformanceMetrics
)
from .campaign_session_notes_storage import CampaignSessionNotesStorage


class SessionNotesStorage:
    """
    Manager for multiple campaign session notes storage systems.
    Handles file I/O and provides access to campaign-specific data.
    """
    
    def __init__(self, storage_dir: str = "knowledge_base/processed_session_notes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache of loaded campaigns
        self._campaigns: Dict[str, CampaignSessionNotesStorage] = {}
        
        # Load list of available campaigns
        self._discover_campaigns()
    
    def get_campaign(self, campaign_name: str) -> Optional[CampaignSessionNotesStorage]:
        """
        Get a campaign's session notes storage.
        Loads from disk if not already in memory.
        """
        if campaign_name not in self._campaigns or self._campaigns[campaign_name] is None:
            loaded_campaign = self._load_campaign(campaign_name)
            if loaded_campaign:
                self._campaigns[campaign_name] = loaded_campaign
        
        return self._campaigns.get(campaign_name)
    
    def get_all_campaigns(self) -> List[str]:
        """Get list of all available campaign names."""
        return list(self._campaigns.keys())
    
    def create_campaign(self, campaign_name: str) -> CampaignSessionNotesStorage:
        """Create a new campaign storage."""
        campaign = CampaignSessionNotesStorage(campaign_name=campaign_name)
        self._campaigns[campaign_name] = campaign
        self.save_campaign(campaign_name)
        return campaign
    
    def save_campaign(self, campaign_name: str) -> bool:
        """Save a campaign to disk."""
        campaign = self._campaigns.get(campaign_name)
        if not campaign:
            return False
        
        campaign_dir = self.storage_dir / campaign_name
        campaign_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save each component separately
            with open(campaign_dir / "sessions.pkl", "wb") as f:
                pickle.dump(campaign.sessions, f)
            
            with open(campaign_dir / "entities.pkl", "wb") as f:
                pickle.dump(campaign.entities, f)
                
            with open(campaign_dir / "embeddings.pkl", "wb") as f:
                pickle.dump(campaign.embeddings, f)
                
            with open(campaign_dir / "metadata.pkl", "wb") as f:
                pickle.dump(campaign.metadata, f)
            
            # Save campaign settings
            campaign_info = {
                'campaign_name': campaign.campaign_name,
                'embedding_model': campaign.embedding_model,
                'chunk_size': campaign.chunk_size,
                'chunk_overlap': campaign.chunk_overlap,
                'last_saved': datetime.now()
            }
            with open(campaign_dir / "campaign_info.pkl", "wb") as f:
                pickle.dump(campaign_info, f)
            
            return True
        except Exception as e:
            print(f"Error saving campaign {campaign_name}: {e}")
            return False
    
    def save_all_campaigns(self) -> int:
        """Save all loaded campaigns to disk. Returns number of campaigns saved."""
        saved_count = 0
        for campaign_name in self._campaigns:
            if self.save_campaign(campaign_name):
                saved_count += 1
        return saved_count
    
    def _load_campaign(self, campaign_name: str) -> Optional[CampaignSessionNotesStorage]:
        """Load a campaign from disk."""
        campaign_dir = self.storage_dir / campaign_name
        
        if not campaign_dir.exists():
            return None
        
        try:
            # Load campaign info first
            campaign_info = {}
            info_file = campaign_dir / "campaign_info.pkl"
            if info_file.exists():
                with open(info_file, "rb") as f:
                    campaign_info = pickle.load(f)
            
            # Create campaign storage instance
            campaign = CampaignSessionNotesStorage(
                campaign_name=campaign_name,
                embedding_model=campaign_info.get('embedding_model', 'text-embedding-3-small'),
                chunk_size=campaign_info.get('chunk_size', 1000),
                chunk_overlap=campaign_info.get('chunk_overlap', 200)
            )
            
            # Load each component if it exists
            sessions_file = campaign_dir / "sessions.pkl"
            if sessions_file.exists():
                with open(sessions_file, "rb") as f:
                    campaign.sessions = pickle.load(f)
            
            entities_file = campaign_dir / "entities.pkl"
            if entities_file.exists():
                with open(entities_file, "rb") as f:
                    campaign.entities = pickle.load(f)
                    
            embeddings_file = campaign_dir / "embeddings.pkl"
            if embeddings_file.exists():
                with open(embeddings_file, "rb") as f:
                    campaign.embeddings = pickle.load(f)
                    
            metadata_file = campaign_dir / "metadata.pkl"
            if metadata_file.exists():
                with open(metadata_file, "rb") as f:
                    campaign.metadata = pickle.load(f)
            
            return campaign
            
        except Exception as e:
            print(f"Error loading campaign {campaign_name}: {e}")
            return None
    
    def _discover_campaigns(self) -> None:
        """Discover available campaigns by scanning the storage directory."""
        if not self.storage_dir.exists():
            return
        
        for item in self.storage_dir.iterdir():
            if item.is_dir():
                campaign_name = item.name
                # Check if it has expected campaign files
                if (item / "sessions.pkl").exists() or (item / "campaign_info.pkl").exists():
                    # Don't load yet, just register as available
                    if campaign_name not in self._campaigns:
                        self._campaigns[campaign_name] = None  # Placeholder
    
    def list_campaigns(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information about all campaigns."""
        campaign_summaries = {}
        
        for campaign_name in self.get_all_campaigns():
            campaign = self.get_campaign(campaign_name)
            if campaign:
                campaign_summaries[campaign_name] = campaign.get_campaign_summary()
            else:
                # If campaign failed to load, provide basic info
                campaign_dir = self.storage_dir / campaign_name
                campaign_summaries[campaign_name] = {
                    'campaign_name': campaign_name,
                    'status': 'failed_to_load',
                    'directory': str(campaign_dir)
                }
        
        return campaign_summaries
    
    def delete_campaign(self, campaign_name: str) -> bool:
        """Delete a campaign from disk and memory."""
        try:
            # Remove from memory
            if campaign_name in self._campaigns:
                del self._campaigns[campaign_name]
            
            # Remove from disk
            campaign_dir = self.storage_dir / campaign_name
            if campaign_dir.exists():
                import shutil
                shutil.rmtree(campaign_dir)
            
            return True
        except Exception as e:
            print(f"Error deleting campaign {campaign_name}: {e}")
            return False
    
    def get_total_session_count(self) -> int:
        """Get total number of sessions across all campaigns."""
        total = 0
        for campaign_name in self.get_all_campaigns():
            campaign = self.get_campaign(campaign_name)
            if campaign:
                total += campaign.get_session_count()
        return total
    
    def get_total_entity_count(self) -> int:
        """Get total number of entities across all campaigns."""
        total = 0
        for campaign_name in self.get_all_campaigns():
            campaign = self.get_campaign(campaign_name)
            if campaign:
                total += campaign.get_entity_count()
        return total
    
    def search_across_campaigns(self, keyword: str) -> Dict[str, List[ProcessedSession]]:
        """Search for sessions containing a keyword across all campaigns."""
        results = {}
        for campaign_name in self.get_all_campaigns():
            campaign = self.get_campaign(campaign_name)
            if campaign:
                matching_sessions = campaign.search_sessions_by_keyword(keyword)
                if matching_sessions:
                    results[campaign_name] = matching_sessions
        return results
