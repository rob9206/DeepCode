"""
AI Chat Handler Module

This module provides the core conversation handling capabilities for the DynoAI system,
managing AI interactions, conversation history, streaming responses, and integration
with persona management and prompt templates.

Key Features:
- OpenAI API integration with streaming support
- Conversation history management and persistence
- Dynamic persona switching during conversations
- Error handling and retry logic
- Token usage tracking and optimization
- Context window management
"""

import logging
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Iterator, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from openai import OpenAI
import requests

# Internal imports
from .persona_manager import PersonaManager, PersonaConfig, get_default_persona_manager, PersonaManagerError
from .prompt_templates import PromptTemplates, PersonaType, get_default_prompt_templates, PromptTemplateError
from ..config import get_config, Config

# Configure logging
logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Enumeration for message roles in conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class ConversationStatus(Enum):
    """Enumeration for conversation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class StreamingStatus(Enum):
    """Enumeration for streaming response status"""
    STARTING = "starting"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ChatMessage:
    """Data class representing a single chat message"""
    role: MessageRole
    content: str
    timestamp: datetime
    persona_type: Optional[PersonaType] = None
    token_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'persona_type': self.persona_type.value if self.persona_type else None,
            'token_count': self.token_count,
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary"""
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            persona_type=PersonaType(data['persona_type']) if data.get('persona_type') else None,
            token_count=data.get('token_count'),
            metadata=data.get('metadata', {})
        )


@dataclass
class ConversationContext:
    """Data class for conversation context and settings"""
    conversation_id: str
    persona_type: PersonaType
    status: ConversationStatus
    created_at: datetime
    updated_at: datetime
    total_tokens: int = 0
    message_count: int = 0
    settings: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary format"""
        return {
            'conversation_id': self.conversation_id,
            'persona_type': self.persona_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_tokens': self.total_tokens,
            'message_count': self.message_count,
            'settings': self.settings or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create context from dictionary"""
        return cls(
            conversation_id=data['conversation_id'],
            persona_type=PersonaType(data['persona_type']),
            status=ConversationStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            total_tokens=data.get('total_tokens', 0),
            message_count=data.get('message_count', 0),
            settings=data.get('settings', {})
        )


@dataclass
class StreamingResponse:
    """Data class for streaming response information"""
    status: StreamingStatus
    content: str
    delta: str
    token_count: int
    finish_reason: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert streaming response to dictionary"""
        return {
            'status': self.status.value,
            'content': self.content,
            'delta': self.delta,
            'token_count': self.token_count,
            'finish_reason': self.finish_reason,
            'error': self.error,
            'metadata': self.metadata or {}
        }


class ChatHandlerError(Exception):
    """Custom exception for chat handler errors"""
    pass


class TokenLimitError(ChatHandlerError):
    """Exception raised when token limit is exceeded"""
    pass


class APIError(ChatHandlerError):
    """Exception raised for API-related errors"""
    pass


class ChatHandler:
    """
    Main chat handler class for managing AI conversations
    
    This class provides comprehensive conversation management including:
    - OpenAI API integration with streaming support
    - Conversation history and context management
    - Dynamic persona switching
    - Token usage tracking and optimization
    - Error handling and retry logic
    """
    
    def __init__(self, 
                 config: Optional[Config] = None,
                 persona_manager: Optional[PersonaManager] = None,
                 prompt_templates: Optional[PromptTemplates] = None):
        """
        Initialize chat handler
        
        Args:
            config: Configuration instance (uses default if None)
            persona_manager: Persona manager instance (uses default if None)
            prompt_templates: Prompt templates instance (uses default if None)
        """
        self.config = config or get_config()
        self.persona_manager = persona_manager or get_default_persona_manager()
        self.prompt_templates = prompt_templates or get_default_prompt_templates()
        
        # Initialize OpenAI client
        self.client = None
        self._initialize_client()
        
        # Conversation storage
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        
        # Configuration settings
        self.max_context_tokens = 4000  # Reserve tokens for response
        self.max_retry_attempts = 3
        self.retry_delay = 1.0
        
        logger.info("ChatHandler initialized successfully")
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client with configuration"""
        try:
            ai_config = self.config.get_ai_config()
            
            if ai_config.get('provider') == 'openai':
                api_key = ai_config.get('openai_api_key')
                if not api_key:
                    raise ChatHandlerError("OpenAI API key not configured")
                
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                raise ChatHandlerError(f"Unsupported AI provider: {ai_config.get('provider')}")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            raise ChatHandlerError(f"Client initialization failed: {e}")
    
    def create_conversation(self, 
                          persona_type: PersonaType = PersonaType.ASSISTANT,
                          conversation_id: Optional[str] = None) -> str:
        """
        Create a new conversation with specified persona
        
        Args:
            persona_type: AI persona to use for conversation
            conversation_id: Optional custom conversation ID
            
        Returns:
            str: Conversation ID
        """
        if conversation_id is None:
            conversation_id = f"conv_{int(time.time() * 1000)}"
        
        # Initialize conversation
        self.conversations[conversation_id] = []
        
        # Create conversation context
        context = ConversationContext(
            conversation_id=conversation_id,
            persona_type=persona_type,
            status=ConversationStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.conversation_contexts[conversation_id] = context
        
        # Add system message with persona prompt
        try:
            system_prompt = self.persona_manager.get_persona_prompt(persona_type)
            system_message = ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt,
                timestamp=datetime.now(),
                persona_type=persona_type
            )
            self.conversations[conversation_id].append(system_message)
            
            logger.info(f"Created conversation {conversation_id} with persona {persona_type.value}")
            return conversation_id
            
        except (PersonaManagerError, PromptTemplateError) as e:
            logger.error(f"Failed to create conversation: {e}")
            raise ChatHandlerError(f"Conversation creation failed: {e}")
    
    def send_message(self, 
                    conversation_id: str, 
                    message: str,
                    stream: bool = False) -> Union[str, Iterator[StreamingResponse]]:
        """
        Send a message and get AI response
        
        Args:
            conversation_id: ID of the conversation
            message: User message content
            stream: Whether to stream the response
            
        Returns:
            Union[str, Iterator[StreamingResponse]]: Response content or streaming iterator
        """
        if conversation_id not in self.conversations:
            raise ChatHandlerError(f"Conversation {conversation_id} not found")
        
        try:
            # Add user message
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=message,
                timestamp=datetime.now()
            )
            self.conversations[conversation_id].append(user_message)
            
            # Update context
            context = self.conversation_contexts[conversation_id]
            context.message_count += 1
            context.updated_at = datetime.now()
            
            # Get AI response
            if stream:
                return self._get_streaming_response(conversation_id)
            else:
                return self._get_response(conversation_id)
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            context.status = ConversationStatus.ERROR
            raise ChatHandlerError(f"Message sending failed: {e}")
    
    def _get_response(self, conversation_id: str) -> str:
        """
        Get non-streaming AI response
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            str: AI response content
        """
        messages = self._prepare_messages(conversation_id)
        context = self.conversation_contexts[conversation_id]
        
        # Get AI parameters from persona
        ai_params = self.persona_manager.get_ai_parameters(context.persona_type)
        
        for attempt in range(self.max_retry_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=ai_params.get('model', 'gpt-3.5-turbo'),
                    messages=messages,
                    temperature=ai_params.get('temperature', 0.7),
                    max_tokens=ai_params.get('max_tokens', 1000),
                    top_p=ai_params.get('top_p', 1.0),
                    frequency_penalty=ai_params.get('frequency_penalty', 0.0),
                    presence_penalty=ai_params.get('presence_penalty', 0.0)
                )
                
                # Extract response content
                assistant_content = response.choices[0].message.content
                
                # Add assistant message to conversation
                assistant_message = ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=assistant_content,
                    timestamp=datetime.now(),
                    persona_type=context.persona_type,
                    token_count=response.usage.completion_tokens if response.usage else None
                )
                self.conversations[conversation_id].append(assistant_message)
                
                # Update context with token usage
                if response.usage:
                    context.total_tokens += response.usage.total_tokens
                
                context.message_count += 1
                context.updated_at = datetime.now()
                
                logger.info(f"Generated response for conversation {conversation_id}")
                return assistant_content
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit, attempt {attempt + 1}: {e}")
                if attempt < self.max_retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise APIError(f"Rate limit exceeded after {self.max_retry_attempts} attempts")
                    
            except openai.APIError as e:
                logger.error(f"OpenAI API error: {e}")
                raise APIError(f"API request failed: {e}")
                
            except Exception as e:
                logger.error(f"Unexpected error in response generation: {e}")
                raise ChatHandlerError(f"Response generation failed: {e}")
    
    def _get_streaming_response(self, conversation_id: str) -> Iterator[StreamingResponse]:
        """
        Get streaming AI response
        
        Args:
            conversation_id: ID of the conversation
            
        Yields:
            StreamingResponse: Streaming response chunks
        """
        messages = self._prepare_messages(conversation_id)
        context = self.conversation_contexts[conversation_id]
        
        # Get AI parameters from persona
        ai_params = self.persona_manager.get_ai_parameters(context.persona_type)
        
        full_content = ""
        token_count = 0
        
        try:
            # Yield starting status
            yield StreamingResponse(
                status=StreamingStatus.STARTING,
                content="",
                delta="",
                token_count=0
            )
            
            # Create streaming request
            stream = self.client.chat.completions.create(
                model=ai_params.get('model', 'gpt-3.5-turbo'),
                messages=messages,
                temperature=ai_params.get('temperature', 0.7),
                max_tokens=ai_params.get('max_tokens', 1000),
                top_p=ai_params.get('top_p', 1.0),
                frequency_penalty=ai_params.get('frequency_penalty', 0.0),
                presence_penalty=ai_params.get('presence_penalty', 0.0),
                stream=True
            )
            
            # Process streaming chunks
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    token_count += 1  # Approximate token counting
                    
                    yield StreamingResponse(
                        status=StreamingStatus.STREAMING,
                        content=full_content,
                        delta=delta,
                        token_count=token_count,
                        finish_reason=chunk.choices[0].finish_reason
                    )
                
                # Check for completion
                if chunk.choices[0].finish_reason:
                    break
            
            # Add final assistant message to conversation
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=full_content,
                timestamp=datetime.now(),
                persona_type=context.persona_type,
                token_count=token_count
            )
            self.conversations[conversation_id].append(assistant_message)
            
            # Update context
            context.total_tokens += token_count
            context.message_count += 1
            context.updated_at = datetime.now()
            
            # Yield completion status
            yield StreamingResponse(
                status=StreamingStatus.COMPLETED,
                content=full_content,
                delta="",
                token_count=token_count,
                finish_reason="stop"
            )
            
            logger.info(f"Completed streaming response for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Streaming response error: {e}")
            yield StreamingResponse(
                status=StreamingStatus.ERROR,
                content=full_content,
                delta="",
                token_count=token_count,
                error=str(e)
            )
    
    def _prepare_messages(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Prepare messages for API request with context window management
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List[Dict[str, str]]: Formatted messages for API
        """
        messages = self.conversations[conversation_id]
        
        # Convert to API format
        api_messages = []
        total_tokens = 0
        
        # Always include system message (first message)
        if messages and messages[0].role == MessageRole.SYSTEM:
            api_messages.append({
                'role': messages[0].role.value,
                'content': messages[0].content
            })
            total_tokens += len(messages[0].content.split()) * 1.3  # Rough token estimation
        
        # Add recent messages within token limit
        for message in reversed(messages[1:]):  # Skip system message
            message_tokens = len(message.content.split()) * 1.3
            
            if total_tokens + message_tokens > self.max_context_tokens:
                break
                
            api_messages.insert(-1 if api_messages else 0, {
                'role': message.role.value,
                'content': message.content
            })
            total_tokens += message_tokens
        
        return api_messages
    
    def switch_persona(self, conversation_id: str, persona_type: PersonaType) -> bool:
        """
        Switch persona for an existing conversation
        
        Args:
            conversation_id: ID of the conversation
            persona_type: New persona type to switch to
            
        Returns:
            bool: True if switch was successful
        """
        if conversation_id not in self.conversations:
            raise ChatHandlerError(f"Conversation {conversation_id} not found")
        
        try:
            # Update conversation context
            context = self.conversation_contexts[conversation_id]
            old_persona = context.persona_type
            context.persona_type = persona_type
            context.updated_at = datetime.now()
            
            # Update system message with new persona prompt
            messages = self.conversations[conversation_id]
            if messages and messages[0].role == MessageRole.SYSTEM:
                new_system_prompt = self.persona_manager.get_persona_prompt(persona_type)
                messages[0].content = new_system_prompt
                messages[0].persona_type = persona_type
                messages[0].timestamp = datetime.now()
            
            logger.info(f"Switched persona from {old_persona.value} to {persona_type.value} for conversation {conversation_id}")
            return True
            
        except (PersonaManagerError, PromptTemplateError) as e:
            logger.error(f"Failed to switch persona: {e}")
            raise ChatHandlerError(f"Persona switch failed: {e}")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List[Dict[str, Any]]: List of message dictionaries
        """
        if conversation_id not in self.conversations:
            raise ChatHandlerError(f"Conversation {conversation_id} not found")
        
        return [msg.to_dict() for msg in self.conversations[conversation_id]]
    
    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation context information
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dict[str, Any]: Conversation context dictionary
        """
        if conversation_id not in self.conversation_contexts:
            raise ChatHandlerError(f"Conversation {conversation_id} not found")
        
        return self.conversation_contexts[conversation_id].to_dict()
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversation contexts
        
        Returns:
            List[Dict[str, Any]]: List of conversation context dictionaries
        """
        return [context.to_dict() for context in self.conversation_contexts.values()]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and its context
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            bool: True if deletion was successful
        """
        if conversation_id not in self.conversations:
            return False
        
        del self.conversations[conversation_id]
        del self.conversation_contexts[conversation_id]
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    def clear_all_conversations(self) -> int:
        """
        Clear all conversations and contexts
        
        Returns:
            int: Number of conversations cleared
        """
        count = len(self.conversations)
        self.conversations.clear()
        self.conversation_contexts.clear()
        
        logger.info(f"Cleared {count} conversations")
        return count
    
    def export_conversation(self, conversation_id: str, format: str = 'json') -> str:
        """
        Export conversation in specified format
        
        Args:
            conversation_id: ID of the conversation to export
            format: Export format ('json', 'text', 'markdown')
            
        Returns:
            str: Exported conversation data
        """
        if conversation_id not in self.conversations:
            raise ChatHandlerError(f"Conversation {conversation_id} not found")
        
        messages = self.conversations[conversation_id]
        context = self.conversation_contexts[conversation_id]
        
        if format.lower() == 'json':
            export_data = {
                'context': context.to_dict(),
                'messages': [msg.to_dict() for msg in messages]
            }
            return json.dumps(export_data, indent=2, default=str)
        
        elif format.lower() == 'text':
            lines = [f"Conversation: {conversation_id}"]
            lines.append(f"Persona: {context.persona_type.value}")
            lines.append(f"Created: {context.created_at}")
            lines.append("-" * 50)
            
            for msg in messages:
                if msg.role != MessageRole.SYSTEM:
                    lines.append(f"{msg.role.value.upper()}: {msg.content}")
                    lines.append("")
            
            return "\n".join(lines)
        
        elif format.lower() == 'markdown':
            lines = [f"# Conversation: {conversation_id}"]
            lines.append(f"**Persona:** {context.persona_type.value}")
            lines.append(f"**Created:** {context.created_at}")
            lines.append("")
            
            for msg in messages:
                if msg.role != MessageRole.SYSTEM:
                    role_header = "**User:**" if msg.role == MessageRole.USER else "**Assistant:**"
                    lines.append(f"{role_header} {msg.content}")
                    lines.append("")
            
            return "\n".join(lines)
        
        else:
            raise ChatHandlerError(f"Unsupported export format: {format}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics across all conversations
        
        Returns:
            Dict[str, Any]: Usage statistics
        """
        total_conversations = len(self.conversations)
        total_messages = sum(len(msgs) for msgs in self.conversations.values())
        total_tokens = sum(ctx.total_tokens for ctx in self.conversation_contexts.values())
        
        # Persona usage statistics
        persona_usage = {}
        for context in self.conversation_contexts.values():
            persona = context.persona_type.value
            persona_usage[persona] = persona_usage.get(persona, 0) + 1
        
        # Active conversations
        active_conversations = sum(
            1 for ctx in self.conversation_contexts.values() 
            if ctx.status == ConversationStatus.ACTIVE
        )
        
        return {
            'total_conversations': total_conversations,
            'active_conversations': active_conversations,
            'total_messages': total_messages,
            'total_tokens': total_tokens,
            'persona_usage': persona_usage,
            'average_messages_per_conversation': total_messages / total_conversations if total_conversations > 0 else 0,
            'average_tokens_per_conversation': total_tokens / total_conversations if total_conversations > 0 else 0
        }


# Singleton instance for global access
_default_chat_handler: Optional[ChatHandler] = None


def get_default_chat_handler() -> ChatHandler:
    """
    Get the default chat handler instance (singleton pattern)
    
    Returns:
        ChatHandler: Default chat handler instance
    """
    global _default_chat_handler
    if _default_chat_handler is None:
        _default_chat_handler = ChatHandler()
    return _default_chat_handler


def reset_chat_handler() -> None:
    """Reset the default chat handler (useful for testing)"""
    global _default_chat_handler
    _default_chat_handler = None


# Utility functions for common operations
def create_quick_conversation(message: str, 
                            persona_type: PersonaType = PersonaType.ASSISTANT) -> Tuple[str, str]:
    """
    Create a conversation and send a message in one call
    
    Args:
        message: User message to send
        persona_type: AI persona to use
        
    Returns:
        Tuple[str, str]: (conversation_id, ai_response)
    """
    handler = get_default_chat_handler()
    conversation_id = handler.create_conversation(persona_type)
    response = handler.send_message(conversation_id, message)
    return conversation_id, response


def get_streaming_conversation(message: str, 
                             persona_type: PersonaType = PersonaType.ASSISTANT) -> Tuple[str, Iterator[StreamingResponse]]:
    """
    Create a conversation and get streaming response
    
    Args:
        message: User message to send
        persona_type: AI persona to use
        
    Returns:
        Tuple[str, Iterator[StreamingResponse]]: (conversation_id, streaming_iterator)
    """
    handler = get_default_chat_handler()
    conversation_id = handler.create_conversation(persona_type)
    stream = handler.send_message(conversation_id, message, stream=True)
    return conversation_id, stream


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create chat handler
        handler = ChatHandler()
        
        # Create conversation
        conv_id = handler.create_conversation(PersonaType.ASSISTANT)
        print(f"Created conversation: {conv_id}")
        
        # Send message
        response = handler.send_message(conv_id, "Hello! How are you today?")
        print(f"AI Response: {response}")
        
        # Get conversation history
        history = handler.get_conversation_history(conv_id)
        print(f"Conversation has {len(history)} messages")
        
        # Get usage stats
        stats = handler.get_usage_stats()
        print(f"Usage stats: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")