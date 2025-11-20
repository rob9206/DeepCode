"""
DynoAI Core Engine - AI conversation logic and model management

This module implements the core AI functionality including:
- OpenAI and local model integration
- Conversation context management
- Dynamic response generation
- Model switching and configuration
- Error handling and fallback mechanisms
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# External dependencies
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Local models only.")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. OpenAI models only.")

# Internal dependencies
from ..config import get_config, AI_MODEL_PRESETS
from ..utils import (
    sanitize_input, generate_session_id, validate_api_key,
    calculate_response_time, log_conversation, format_timestamp,
    truncate_text, extract_keywords
)


@dataclass
class ConversationContext:
    """Manages conversation context and state"""
    session_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    context_window: int = 10
    total_tokens: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation context"""
        message = {
            "role": role,
            "content": content,
            "timestamp": format_timestamp(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # Maintain context window
        if len(self.messages) > self.context_window * 2:  # *2 for user+assistant pairs
            self.messages = self.messages[-self.context_window * 2:]
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get messages formatted for AI model"""
        return [{"role": msg["role"], "content": msg["content"]} for msg in self.messages]
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation"""
        if not self.messages:
            return "No conversation history"
        
        recent_messages = self.messages[-6:]  # Last 3 exchanges
        summary_parts = []
        
        for msg in recent_messages:
            role = msg["role"].capitalize()
            content = truncate_text(msg["content"], 100)
            summary_parts.append(f"{role}: {content}")
        
        return " | ".join(summary_parts)
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if conversation context has expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class AIEngine:
    """Core AI engine for conversation management and response generation"""
    
    def __init__(self, config=None):
        """Initialize AI engine with configuration"""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)
        
        # Model configuration
        self.current_model = self.config.AI_MODEL
        self.model_presets = AI_MODEL_PRESETS
        
        # OpenAI client
        self.openai_client = None
        if OPENAI_AVAILABLE and self.config.OPENAI_API_KEY:
            try:
                openai.api_key = self.config.OPENAI_API_KEY
                self.openai_client = openai
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Local model components
        self.local_model = None
        self.local_tokenizer = None
        self.local_pipeline = None
        
        # Conversation contexts
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # Performance metrics
        self.response_times = []
        self.total_requests = 0
        self.successful_requests = 0
        
        # Initialize default model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model based on configuration"""
        try:
            if self.current_model.startswith("gpt-") and self.openai_client:
                self.logger.info(f"Using OpenAI model: {self.current_model}")
                return True
            elif TRANSFORMERS_AVAILABLE:
                return self._initialize_local_model()
            else:
                self.logger.error("No AI models available")
                return False
        except Exception as e:
            self.logger.error(f"Model initialization failed: {e}")
            return False
    
    def _initialize_local_model(self):
        """Initialize local transformer model"""
        try:
            model_name = self.config.LOCAL_MODEL_PATH or "microsoft/DialoGPT-medium"
            self.logger.info(f"Loading local model: {model_name}")
            
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token if not present
            if self.local_tokenizer.pad_token is None:
                self.local_tokenizer.pad_token = self.local_tokenizer.eos_token
            
            # Create pipeline for easier inference
            self.local_pipeline = pipeline(
                "text-generation",
                model=self.local_model,
                tokenizer=self.local_tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("Local model initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Local model initialization failed: {e}")
            return False
    
    def get_or_create_context(self, session_id: str, user_id: Optional[str] = None) -> ConversationContext:
        """Get existing context or create new one"""
        if session_id not in self.active_contexts:
            self.active_contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                conversation_id=generate_session_id()
            )
        
        return self.active_contexts[session_id]
    
    def cleanup_expired_contexts(self, timeout_minutes: int = 60):
        """Remove expired conversation contexts"""
        expired_sessions = [
            session_id for session_id, context in self.active_contexts.items()
            if context.is_expired(timeout_minutes)
        ]
        
        for session_id in expired_sessions:
            del self.active_contexts[session_id]
            self.logger.info(f"Cleaned up expired context: {session_id}")
    
    async def generate_response(
        self,
        user_message: str,
        session_id: str,
        user_id: Optional[str] = None,
        model_preset: str = "balanced",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response to user message"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Input validation and sanitization
            user_message = sanitize_input(user_message)
            if not user_message.strip():
                return self._create_error_response("Empty message received")
            
            # Get or create conversation context
            context = self.get_or_create_context(session_id, user_id)
            context.add_message("user", user_message)
            
            # Apply model preset
            model_config = self._get_model_config(model_preset)
            
            # Generate response based on available models
            if self.openai_client and self.current_model.startswith("gpt-"):
                response_data = await self._generate_openai_response(context, model_config)
            elif self.local_pipeline:
                response_data = await self._generate_local_response(context, model_config)
            else:
                return self._create_error_response("No AI models available")
            
            # Add response to context
            if response_data.get("success"):
                context.add_message("assistant", response_data["content"])
                self.successful_requests += 1
            
            # Calculate performance metrics
            response_time = calculate_response_time(start_time)
            self.response_times.append(response_time)
            
            # Log conversation
            log_conversation(
                user_id or session_id,
                user_message,
                response_data.get("content", "Error occurred"),
                context.conversation_id
            )
            
            # Prepare final response
            response_data.update({
                "session_id": session_id,
                "conversation_id": context.conversation_id,
                "response_time": response_time,
                "model_used": self.current_model,
                "context_length": len(context.messages)
            })
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            return self._create_error_response(f"Generation error: {str(e)}")
    
    async def _generate_openai_response(
        self,
        context: ConversationContext,
        model_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API"""
        try:
            messages = context.get_context_messages()
            
            # Add system message if configured
            if model_config.get("system_message"):
                messages.insert(0, {
                    "role": "system",
                    "content": model_config["system_message"]
                })
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model=self.current_model,
                messages=messages,
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 1000),
                top_p=model_config.get("top_p", 1.0),
                frequency_penalty=model_config.get("frequency_penalty", 0.0),
                presence_penalty=model_config.get("presence_penalty", 0.0)
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": content,
                "model": self.current_model,
                "tokens_used": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return self._create_error_response(f"OpenAI error: {str(e)}")
    
    async def _generate_local_response(
        self,
        context: ConversationContext,
        model_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response using local transformer model"""
        try:
            # Prepare input text from conversation context
            messages = context.get_context_messages()
            conversation_text = ""
            
            for msg in messages[-6:]:  # Use last 3 exchanges
                role_prefix = "Human: " if msg["role"] == "user" else "Assistant: "
                conversation_text += f"{role_prefix}{msg['content']}\n"
            
            conversation_text += "Assistant: "
            
            # Generate response
            response = await asyncio.to_thread(
                self.local_pipeline,
                conversation_text,
                max_length=len(conversation_text) + model_config.get("max_tokens", 100),
                temperature=model_config.get("temperature", 0.7),
                do_sample=True,
                pad_token_id=self.local_tokenizer.eos_token_id,
                num_return_sequences=1
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            assistant_response = generated_text[len(conversation_text):].strip()
            
            # Clean up response
            if "\nHuman:" in assistant_response:
                assistant_response = assistant_response.split("\nHuman:")[0].strip()
            
            return {
                "success": True,
                "content": assistant_response or "I'm not sure how to respond to that.",
                "model": "local_model",
                "tokens_used": len(generated_text.split()),
                "finish_reason": "stop"
            }
            
        except Exception as e:
            self.logger.error(f"Local model error: {e}")
            return self._create_error_response(f"Local model error: {str(e)}")
    
    def _get_model_config(self, preset: str) -> Dict[str, Any]:
        """Get model configuration for preset"""
        return self.model_presets.get(preset, self.model_presets["balanced"])
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
            "error": error_message,
            "model": self.current_model,
            "tokens_used": 0,
            "finish_reason": "error"
        }
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to different AI model"""
        try:
            if model_name.startswith("gpt-") and self.openai_client:
                self.current_model = model_name
                self.logger.info(f"Switched to OpenAI model: {model_name}")
                return True
            elif model_name == "local" and self.local_pipeline:
                self.current_model = "local_model"
                self.logger.info("Switched to local model")
                return True
            else:
                self.logger.error(f"Model not available: {model_name}")
                return False
        except Exception as e:
            self.logger.error(f"Model switch failed: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and capabilities"""
        return {
            "current_model": self.current_model,
            "openai_available": bool(self.openai_client),
            "local_model_available": bool(self.local_pipeline),
            "active_contexts": len(self.active_contexts),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": (self.successful_requests / max(self.total_requests, 1)) * 100,
            "average_response_time": sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0,
            "available_presets": list(self.model_presets.keys())
        }
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        if session_id in self.active_contexts:
            return self.active_contexts[session_id].messages
        return []
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for session"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
            self.logger.info(f"Cleared conversation: {session_id}")
            return True
        return False
    
    def export_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export conversation data"""
        if session_id not in self.active_contexts:
            return None
        
        context = self.active_contexts[session_id]
        return {
            "session_id": session_id,
            "conversation_id": context.conversation_id,
            "user_id": context.user_id,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "message_count": len(context.messages),
            "messages": context.messages,
            "metadata": context.metadata
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        recent_times = self.response_times[-100:] if self.response_times else []
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.total_requests - self.successful_requests,
            "success_rate": (self.successful_requests / max(self.total_requests, 1)) * 100,
            "average_response_time": sum(recent_times) / len(recent_times) if recent_times else 0,
            "min_response_time": min(recent_times) if recent_times else 0,
            "max_response_time": max(recent_times) if recent_times else 0,
            "active_conversations": len(self.active_contexts),
            "model_status": self.get_model_status()
        }
    
    def shutdown(self):
        """Gracefully shutdown AI engine"""
        self.logger.info("Shutting down AI engine...")
        
        # Clear all contexts
        self.active_contexts.clear()
        
        # Clean up model resources
        if self.local_model:
            del self.local_model
        if self.local_tokenizer:
            del self.local_tokenizer
        if self.local_pipeline:
            del self.local_pipeline
        
        self.logger.info("AI engine shutdown complete")


# Global AI engine instance
_ai_engine_instance = None

def get_ai_engine(config=None) -> AIEngine:
    """Get global AI engine instance"""
    global _ai_engine_instance
    if _ai_engine_instance is None:
        _ai_engine_instance = AIEngine(config)
    return _ai_engine_instance

def initialize_ai_engine(config=None) -> bool:
    """Initialize global AI engine"""
    try:
        global _ai_engine_instance
        _ai_engine_instance = AIEngine(config)
        return True
    except Exception as e:
        logging.error(f"AI engine initialization failed: {e}")
        return False

def shutdown_ai_engine():
    """Shutdown global AI engine"""
    global _ai_engine_instance
    if _ai_engine_instance:
        _ai_engine_instance.shutdown()
        _ai_engine_instance = None