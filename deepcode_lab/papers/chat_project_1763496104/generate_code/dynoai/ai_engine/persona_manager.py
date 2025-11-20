"""
AI Persona Management System

This module provides comprehensive persona management capabilities for the DynoAI system,
allowing dynamic switching between different AI personalities, behavior patterns, and
conversation styles. It integrates with the prompt template system to provide consistent
and customizable AI interactions.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from .prompt_templates import (
    PromptTemplates, 
    PersonaType, 
    get_default_prompt_templates,
    PromptTemplateError
)

# Configure logging
logger = logging.getLogger(__name__)


class PersonaManagerError(Exception):
    """Custom exception for persona management errors"""
    pass


class PersonaStatus(Enum):
    """Status of a persona"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    CUSTOM = "custom"


@dataclass
class PersonaConfig:
    """Configuration for an AI persona"""
    persona_type: PersonaType
    name: str
    description: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_prompt_override: Optional[str] = None
    custom_instructions: Optional[str] = None
    conversation_style: str = "balanced"
    expertise_level: str = "intermediate"
    response_format: str = "conversational"
    status: PersonaStatus = PersonaStatus.ACTIVE
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    tags: List[str] = None
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert persona config to dictionary"""
        data = asdict(self)
        # Convert enum values to strings
        data['persona_type'] = self.persona_type.value
        data['status'] = self.status.value
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaConfig':
        """Create persona config from dictionary"""
        # Convert string values back to enums
        if isinstance(data.get('persona_type'), str):
            data['persona_type'] = PersonaType(data['persona_type'])
        if isinstance(data.get('status'), str):
            data['status'] = PersonaStatus(data['status'])
        
        # Convert ISO strings back to datetime objects
        if data.get('created_at') and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used') and isinstance(data['last_used'], str):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        
        return cls(**data)


class PersonaManager:
    """
    Manages AI personas, their configurations, and behavior patterns.
    
    This class provides a comprehensive system for managing different AI personalities,
    allowing users to switch between different conversation styles, expertise levels,
    and behavioral patterns. It integrates with the prompt template system to ensure
    consistent AI responses.
    """
    
    def __init__(self, prompt_templates: Optional[PromptTemplates] = None):
        """
        Initialize the persona manager.
        
        Args:
            prompt_templates: Optional PromptTemplates instance. If None, uses default.
        """
        self.prompt_templates = prompt_templates or get_default_prompt_templates()
        self.personas: Dict[str, PersonaConfig] = {}
        self.current_persona: Optional[str] = None
        self.persona_history: List[Tuple[str, datetime]] = []
        
        # Initialize with default personas
        self._initialize_default_personas()
        
        logger.info("PersonaManager initialized with %d personas", len(self.personas))
    
    def _initialize_default_personas(self) -> None:
        """Initialize default persona configurations"""
        default_personas = {
            "assistant": PersonaConfig(
                persona_type=PersonaType.ASSISTANT,
                name="AI Assistant",
                description="Helpful, harmless, and honest AI assistant for general tasks",
                temperature=0.7,
                conversation_style="helpful",
                expertise_level="intermediate",
                tags=["general", "helpful", "default"]
            ),
            "creative": PersonaConfig(
                persona_type=PersonaType.CREATIVE,
                name="Creative Writer",
                description="Imaginative and artistic AI for creative writing and brainstorming",
                temperature=0.9,
                conversation_style="creative",
                expertise_level="advanced",
                tags=["creative", "writing", "artistic"]
            ),
            "technical": PersonaConfig(
                persona_type=PersonaType.TECHNICAL,
                name="Technical Expert",
                description="Precise and detailed AI for technical discussions and problem-solving",
                temperature=0.3,
                conversation_style="precise",
                expertise_level="expert",
                tags=["technical", "programming", "analytical"]
            ),
            "casual": PersonaConfig(
                persona_type=PersonaType.CASUAL,
                name="Casual Friend",
                description="Relaxed and friendly AI for informal conversations",
                temperature=0.8,
                conversation_style="casual",
                expertise_level="beginner",
                tags=["casual", "friendly", "informal"]
            ),
            "professional": PersonaConfig(
                persona_type=PersonaType.PROFESSIONAL,
                name="Business Professional",
                description="Formal and structured AI for business and professional contexts",
                temperature=0.5,
                conversation_style="formal",
                expertise_level="advanced",
                tags=["professional", "business", "formal"]
            ),
            "educational": PersonaConfig(
                persona_type=PersonaType.EDUCATIONAL,
                name="Teacher",
                description="Patient and explanatory AI for learning and education",
                temperature=0.6,
                conversation_style="educational",
                expertise_level="intermediate",
                tags=["educational", "teaching", "learning"]
            ),
            "analytical": PersonaConfig(
                persona_type=PersonaType.ANALYTICAL,
                name="Data Analyst",
                description="Logical and methodical AI for analysis and research",
                temperature=0.4,
                conversation_style="analytical",
                expertise_level="expert",
                tags=["analytical", "research", "logical"]
            )
        }
        
        for persona_id, config in default_personas.items():
            self.personas[persona_id] = config
        
        # Set default active persona
        if "assistant" in self.personas:
            self.current_persona = "assistant"
    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """
        Get list of available personas with their basic information.
        
        Returns:
            List of persona dictionaries with id, name, description, and status
        """
        personas = []
        for persona_id, config in self.personas.items():
            personas.append({
                "id": persona_id,
                "name": config.name,
                "description": config.description,
                "persona_type": config.persona_type.value,
                "status": config.status.value,
                "conversation_style": config.conversation_style,
                "expertise_level": config.expertise_level,
                "tags": config.tags,
                "usage_count": config.usage_count,
                "last_used": config.last_used.isoformat() if config.last_used else None
            })
        return personas
    
    def get_persona_config(self, persona_id: str) -> Optional[PersonaConfig]:
        """
        Get configuration for a specific persona.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            PersonaConfig object or None if not found
        """
        return self.personas.get(persona_id)
    
    def set_active_persona(self, persona_id: str) -> bool:
        """
        Set the active persona for conversations.
        
        Args:
            persona_id: ID of the persona to activate
            
        Returns:
            True if successful, False if persona not found
        """
        if persona_id not in self.personas:
            logger.warning("Attempted to set unknown persona: %s", persona_id)
            return False
        
        if self.personas[persona_id].status == PersonaStatus.ARCHIVED:
            logger.warning("Attempted to set archived persona: %s", persona_id)
            return False
        
        # Update persona usage
        old_persona = self.current_persona
        self.current_persona = persona_id
        self.personas[persona_id].last_used = datetime.now()
        self.personas[persona_id].usage_count += 1
        
        # Add to history
        self.persona_history.append((persona_id, datetime.now()))
        
        logger.info("Switched persona from %s to %s", old_persona, persona_id)
        return True
    
    def get_current_persona(self) -> Optional[PersonaConfig]:
        """
        Get the currently active persona configuration.
        
        Returns:
            Current PersonaConfig or None if no persona is active
        """
        if self.current_persona:
            return self.personas.get(self.current_persona)
        return None
    
    def get_current_persona_id(self) -> Optional[str]:
        """
        Get the ID of the currently active persona.
        
        Returns:
            Current persona ID or None if no persona is active
        """
        return self.current_persona
    
    def create_custom_persona(self, persona_id: str, config: PersonaConfig) -> bool:
        """
        Create a new custom persona.
        
        Args:
            persona_id: Unique ID for the new persona
            config: PersonaConfig object with persona settings
            
        Returns:
            True if successful, False if persona ID already exists
        """
        if persona_id in self.personas:
            logger.warning("Attempted to create persona with existing ID: %s", persona_id)
            return False
        
        # Mark as custom persona
        config.status = PersonaStatus.CUSTOM
        config.created_at = datetime.now()
        
        self.personas[persona_id] = config
        logger.info("Created custom persona: %s", persona_id)
        return True
    
    def update_persona(self, persona_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing persona configuration.
        
        Args:
            persona_id: ID of the persona to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False if persona not found
        """
        if persona_id not in self.personas:
            logger.warning("Attempted to update unknown persona: %s", persona_id)
            return False
        
        config = self.personas[persona_id]
        
        # Update allowed fields
        allowed_fields = {
            'name', 'description', 'temperature', 'max_tokens', 'top_p',
            'frequency_penalty', 'presence_penalty', 'system_prompt_override',
            'custom_instructions', 'conversation_style', 'expertise_level',
            'response_format', 'tags'
        }
        
        for field, value in updates.items():
            if field in allowed_fields and hasattr(config, field):
                setattr(config, field, value)
        
        logger.info("Updated persona: %s", persona_id)
        return True
    
    def delete_persona(self, persona_id: str) -> bool:
        """
        Delete a persona (only custom personas can be deleted).
        
        Args:
            persona_id: ID of the persona to delete
            
        Returns:
            True if successful, False if persona not found or is default persona
        """
        if persona_id not in self.personas:
            logger.warning("Attempted to delete unknown persona: %s", persona_id)
            return False
        
        config = self.personas[persona_id]
        if config.status != PersonaStatus.CUSTOM:
            logger.warning("Attempted to delete non-custom persona: %s", persona_id)
            return False
        
        # If this is the current persona, switch to default
        if self.current_persona == persona_id:
            self.set_active_persona("assistant")
        
        del self.personas[persona_id]
        logger.info("Deleted custom persona: %s", persona_id)
        return True
    
    def archive_persona(self, persona_id: str) -> bool:
        """
        Archive a persona (makes it inactive but keeps it).
        
        Args:
            persona_id: ID of the persona to archive
            
        Returns:
            True if successful, False if persona not found
        """
        if persona_id not in self.personas:
            logger.warning("Attempted to archive unknown persona: %s", persona_id)
            return False
        
        self.personas[persona_id].status = PersonaStatus.ARCHIVED
        
        # If this is the current persona, switch to default
        if self.current_persona == persona_id:
            self.set_active_persona("assistant")
        
        logger.info("Archived persona: %s", persona_id)
        return True
    
    def get_persona_prompt(self, persona_id: Optional[str] = None, 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get the system prompt for a persona.
        
        Args:
            persona_id: ID of the persona (uses current if None)
            context: Optional context for prompt customization
            
        Returns:
            System prompt string
        """
        if persona_id is None:
            persona_id = self.current_persona
        
        if not persona_id or persona_id not in self.personas:
            logger.warning("No valid persona for prompt generation")
            return self.prompt_templates.get_system_prompt(PersonaType.ASSISTANT)
        
        config = self.personas[persona_id]
        
        # Use custom system prompt if provided
        if config.system_prompt_override:
            base_prompt = config.system_prompt_override
        else:
            base_prompt = self.prompt_templates.get_system_prompt(config.persona_type)
        
        # Add custom instructions if provided
        if config.custom_instructions:
            base_prompt += f"\n\nAdditional Instructions: {config.custom_instructions}"
        
        # Add context-specific modifications
        if context:
            conversation_style = context.get('conversation_style', config.conversation_style)
            expertise_level = context.get('expertise_level', config.expertise_level)
            
            base_prompt += f"\n\nConversation Style: {conversation_style}"
            base_prompt += f"\nExpertise Level: {expertise_level}"
        
        return base_prompt
    
    def get_conversation_starter(self, persona_id: Optional[str] = None) -> str:
        """
        Get a conversation starter for a persona.
        
        Args:
            persona_id: ID of the persona (uses current if None)
            
        Returns:
            Conversation starter string
        """
        if persona_id is None:
            persona_id = self.current_persona
        
        if not persona_id or persona_id not in self.personas:
            return self.prompt_templates.get_conversation_starter(PersonaType.ASSISTANT)
        
        config = self.personas[persona_id]
        return self.prompt_templates.get_conversation_starter(config.persona_type)
    
    def get_ai_parameters(self, persona_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AI model parameters for a persona.
        
        Args:
            persona_id: ID of the persona (uses current if None)
            
        Returns:
            Dictionary of AI model parameters
        """
        if persona_id is None:
            persona_id = self.current_persona
        
        if not persona_id or persona_id not in self.personas:
            # Return default parameters
            return {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        
        config = self.personas[persona_id]
        return {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty
        }
    
    def get_persona_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent persona usage history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of history entries with persona info and timestamps
        """
        history = []
        for persona_id, timestamp in self.persona_history[-limit:]:
            if persona_id in self.personas:
                config = self.personas[persona_id]
                history.append({
                    "persona_id": persona_id,
                    "name": config.name,
                    "timestamp": timestamp.isoformat(),
                    "persona_type": config.persona_type.value
                })
        return history
    
    def search_personas(self, query: str, search_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search personas by name, description, or tags.
        
        Args:
            query: Search query string
            search_fields: Fields to search in (default: name, description, tags)
            
        Returns:
            List of matching personas
        """
        if search_fields is None:
            search_fields = ["name", "description", "tags"]
        
        query_lower = query.lower()
        matches = []
        
        for persona_id, config in self.personas.items():
            match_score = 0
            
            # Search in specified fields
            if "name" in search_fields and query_lower in config.name.lower():
                match_score += 3
            if "description" in search_fields and query_lower in config.description.lower():
                match_score += 2
            if "tags" in search_fields:
                for tag in config.tags:
                    if query_lower in tag.lower():
                        match_score += 1
            
            if match_score > 0:
                persona_info = {
                    "id": persona_id,
                    "name": config.name,
                    "description": config.description,
                    "persona_type": config.persona_type.value,
                    "match_score": match_score,
                    "tags": config.tags
                }
                matches.append(persona_info)
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
    
    def export_personas(self, include_usage_stats: bool = True) -> Dict[str, Any]:
        """
        Export all personas to a dictionary format.
        
        Args:
            include_usage_stats: Whether to include usage statistics
            
        Returns:
            Dictionary containing all persona data
        """
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "current_persona": self.current_persona,
            "personas": {}
        }
        
        for persona_id, config in self.personas.items():
            persona_data = config.to_dict()
            
            if not include_usage_stats:
                # Remove usage statistics
                persona_data.pop("usage_count", None)
                persona_data.pop("last_used", None)
            
            export_data["personas"][persona_id] = persona_data
        
        if include_usage_stats:
            export_data["persona_history"] = [
                {"persona_id": pid, "timestamp": ts.isoformat()}
                for pid, ts in self.persona_history
            ]
        
        return export_data
    
    def import_personas(self, import_data: Dict[str, Any], 
                       overwrite_existing: bool = False) -> Dict[str, Any]:
        """
        Import personas from a dictionary format.
        
        Args:
            import_data: Dictionary containing persona data
            overwrite_existing: Whether to overwrite existing personas
            
        Returns:
            Dictionary with import results
        """
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "messages": []
        }
        
        try:
            personas_data = import_data.get("personas", {})
            
            for persona_id, persona_data in personas_data.items():
                try:
                    # Skip if persona exists and overwrite is False
                    if persona_id in self.personas and not overwrite_existing:
                        results["skipped"] += 1
                        results["messages"].append(f"Skipped existing persona: {persona_id}")
                        continue
                    
                    # Create persona config from data
                    config = PersonaConfig.from_dict(persona_data)
                    self.personas[persona_id] = config
                    
                    results["imported"] += 1
                    results["messages"].append(f"Imported persona: {persona_id}")
                    
                except Exception as e:
                    results["errors"] += 1
                    results["messages"].append(f"Error importing {persona_id}: {str(e)}")
                    logger.error("Error importing persona %s: %s", persona_id, str(e))
            
            # Import persona history if available
            if "persona_history" in import_data:
                try:
                    history_data = import_data["persona_history"]
                    for entry in history_data:
                        persona_id = entry["persona_id"]
                        timestamp = datetime.fromisoformat(entry["timestamp"])
                        self.persona_history.append((persona_id, timestamp))
                except Exception as e:
                    results["messages"].append(f"Error importing history: {str(e)}")
            
            logger.info("Import completed: %d imported, %d skipped, %d errors", 
                       results["imported"], results["skipped"], results["errors"])
            
        except Exception as e:
            results["errors"] += 1
            results["messages"].append(f"Import failed: {str(e)}")
            logger.error("Persona import failed: %s", str(e))
        
        return results
    
    def validate_persona_config(self, config: PersonaConfig) -> List[str]:
        """
        Validate a persona configuration.
        
        Args:
            config: PersonaConfig to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not config.name or not config.name.strip():
            errors.append("Persona name is required")
        
        if not config.description or not config.description.strip():
            errors.append("Persona description is required")
        
        # Validate numeric parameters
        if not 0.0 <= config.temperature <= 2.0:
            errors.append("Temperature must be between 0.0 and 2.0")
        
        if not 1 <= config.max_tokens <= 4000:
            errors.append("Max tokens must be between 1 and 4000")
        
        if not 0.0 <= config.top_p <= 1.0:
            errors.append("Top-p must be between 0.0 and 1.0")
        
        if not -2.0 <= config.frequency_penalty <= 2.0:
            errors.append("Frequency penalty must be between -2.0 and 2.0")
        
        if not -2.0 <= config.presence_penalty <= 2.0:
            errors.append("Presence penalty must be between -2.0 and 2.0")
        
        # Validate persona type
        if not isinstance(config.persona_type, PersonaType):
            errors.append("Invalid persona type")
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get persona usage and system statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        total_personas = len(self.personas)
        active_personas = sum(1 for p in self.personas.values() 
                            if p.status == PersonaStatus.ACTIVE)
        custom_personas = sum(1 for p in self.personas.values() 
                            if p.status == PersonaStatus.CUSTOM)
        
        # Most used personas
        most_used = sorted(
            [(pid, config.usage_count) for pid, config in self.personas.items()],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Recent activity
        recent_switches = len([h for h in self.persona_history 
                             if (datetime.now() - h[1]).days <= 7])
        
        return {
            "total_personas": total_personas,
            "active_personas": active_personas,
            "custom_personas": custom_personas,
            "archived_personas": total_personas - active_personas - custom_personas,
            "current_persona": self.current_persona,
            "most_used_personas": [{"id": pid, "usage_count": count} 
                                 for pid, count in most_used],
            "recent_switches": recent_switches,
            "total_switches": len(self.persona_history),
            "available_persona_types": [pt.value for pt in PersonaType]
        }


# Singleton instance for global access
_default_persona_manager: Optional[PersonaManager] = None


def get_default_persona_manager() -> PersonaManager:
    """
    Get the default persona manager instance (singleton pattern).
    
    Returns:
        Default PersonaManager instance
    """
    global _default_persona_manager
    if _default_persona_manager is None:
        _default_persona_manager = PersonaManager()
    return _default_persona_manager


def reset_persona_manager() -> None:
    """Reset the default persona manager instance (for testing)"""
    global _default_persona_manager
    _default_persona_manager = None


# Export main classes and functions
__all__ = [
    'PersonaManager',
    'PersonaConfig', 
    'PersonaStatus',
    'PersonaManagerError',
    'get_default_persona_manager',
    'reset_persona_manager'
]