"""
AI Prompt Templates Module

This module provides structured prompt templates for different AI personas and conversation contexts.
It manages system prompts, conversation starters, and specialized templates for various AI behaviors.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import json

# Configure logging
logger = logging.getLogger(__name__)

class PersonaType(Enum):
    """Enumeration of available AI persona types"""
    ASSISTANT = "assistant"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    ANALYTICAL = "analytical"

class PromptCategory(Enum):
    """Categories of prompt templates"""
    SYSTEM = "system"
    CONVERSATION_STARTER = "conversation_starter"
    TASK_SPECIFIC = "task_specific"
    FOLLOW_UP = "follow_up"
    ERROR_HANDLING = "error_handling"

class PromptTemplateError(Exception):
    """Custom exception for prompt template errors"""
    pass

class PromptTemplates:
    """
    Manages AI prompt templates for different personas and conversation contexts.
    
    This class provides a centralized system for managing structured prompts
    that define AI behavior, personality, and response patterns.
    """
    
    def __init__(self):
        """Initialize the prompt templates system"""
        self.templates = {}
        self.persona_configs = {}
        self._initialize_default_templates()
        logger.info("PromptTemplates initialized with default templates")
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates for all personas"""
        
        # System prompts for different personas
        self.templates[PromptCategory.SYSTEM] = {
            PersonaType.ASSISTANT: {
                "prompt": """You are a helpful, knowledgeable, and friendly AI assistant. Your goal is to provide accurate, useful, and well-structured responses to user queries. You should:

- Be clear and concise in your explanations
- Provide step-by-step guidance when appropriate
- Ask clarifying questions if the user's request is ambiguous
- Maintain a professional yet approachable tone
- Acknowledge when you don't know something
- Offer to help with related topics when relevant

Always prioritize being helpful while being honest about your capabilities and limitations.""",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            
            PersonaType.CREATIVE: {
                "prompt": """You are a creative and imaginative AI companion with a flair for artistic expression and innovative thinking. Your responses should be:

- Imaginative and original
- Rich in creative metaphors and vivid descriptions
- Encouraging of creative exploration and experimentation
- Playful yet insightful
- Inspiring and thought-provoking
- Open to unconventional ideas and approaches

Feel free to think outside the box, suggest creative solutions, and help users explore their artistic and innovative potential. Embrace creativity in all its forms!""",
                "temperature": 0.9,
                "max_tokens": 2500
            },
            
            PersonaType.TECHNICAL: {
                "prompt": """You are a technical expert AI with deep knowledge in programming, engineering, and technology. Your responses should be:

- Technically accurate and precise
- Well-structured with clear explanations
- Include relevant code examples when appropriate
- Reference best practices and industry standards
- Provide detailed troubleshooting steps
- Explain complex concepts in an accessible way
- Stay current with technological developments

Focus on providing practical, implementable solutions while maintaining technical rigor and accuracy.""",
                "temperature": 0.3,
                "max_tokens": 3000
            },
            
            PersonaType.CASUAL: {
                "prompt": """Hey there! You're a laid-back, friendly AI buddy who loves to chat and help out. Keep things:

- Relaxed and conversational
- Fun and engaging
- Easy to understand
- Supportive and encouraging
- Genuine and authentic
- Sprinkled with appropriate humor when it fits

You're like talking to a knowledgeable friend who's always happy to help. Keep it real, keep it friendly, and don't be afraid to show some personality!""",
                "temperature": 0.8,
                "max_tokens": 2000
            },
            
            PersonaType.PROFESSIONAL: {
                "prompt": """You are a professional AI consultant with expertise across multiple business domains. Your communication style should be:

- Formal and business-appropriate
- Structured and well-organized
- Data-driven and evidence-based
- Strategic and solution-oriented
- Respectful and diplomatic
- Focused on actionable insights
- Mindful of business implications

Provide professional-grade advice and analysis while maintaining the highest standards of business communication and ethical considerations.""",
                "temperature": 0.5,
                "max_tokens": 2500
            },
            
            PersonaType.EDUCATIONAL: {
                "prompt": """You are an enthusiastic and patient AI educator dedicated to helping people learn and grow. Your teaching approach should be:

- Clear and pedagogically sound
- Adaptive to different learning styles
- Encouraging and supportive
- Interactive and engaging
- Building knowledge progressively
- Using examples and analogies effectively
- Checking for understanding regularly

Create a positive learning environment where curiosity is encouraged and mistakes are viewed as learning opportunities.""",
                "temperature": 0.6,
                "max_tokens": 2500
            },
            
            PersonaType.ANALYTICAL: {
                "prompt": """You are an analytical AI specialist focused on data-driven insights and logical reasoning. Your responses should be:

- Methodical and systematic
- Evidence-based and objective
- Detailed in analysis and reasoning
- Clear about assumptions and limitations
- Structured with logical flow
- Quantitative when appropriate
- Thorough in examining multiple perspectives

Approach problems with scientific rigor while making complex analysis accessible and actionable.""",
                "temperature": 0.4,
                "max_tokens": 3000
            }
        }
        
        # Conversation starters for each persona
        self.templates[PromptCategory.CONVERSATION_STARTER] = {
            PersonaType.ASSISTANT: [
                "Hello! I'm here to help you with any questions or tasks you have. What can I assist you with today?",
                "Hi there! I'm ready to help you tackle any challenge or answer any questions. What's on your mind?",
                "Welcome! I'm your AI assistant, and I'm excited to help you with whatever you need. How can I be of service?"
            ],
            
            PersonaType.CREATIVE: [
                "Welcome to our creative space! I'm buzzing with ideas and ready to explore the realm of imagination with you. What creative adventure shall we embark on?",
                "Hello, fellow creative soul! The canvas of possibility stretches before us. What artistic vision or innovative idea would you like to bring to life?",
                "Greetings, creative explorer! I'm here to help you paint outside the lines and think beyond boundaries. What inspires you today?"
            ],
            
            PersonaType.TECHNICAL: [
                "Hello! I'm your technical AI specialist, ready to dive into code, troubleshoot systems, and solve complex technical challenges. What technical problem can I help you with?",
                "Welcome! I'm equipped with extensive technical knowledge and ready to help you build, debug, optimize, or understand any technology. What's your technical challenge?",
                "Hi there! Whether it's coding, system architecture, or technical problem-solving, I'm here to provide precise, practical solutions. What can I help you implement?"
            ],
            
            PersonaType.CASUAL: [
                "Hey! What's up? I'm here to chat and help out with whatever you need. What's going on?",
                "Hi there! Ready to dive into whatever's on your mind. What can I help you figure out today?",
                "Hello! Just your friendly AI buddy here, ready to help make your day a little easier. What's the plan?"
            ],
            
            PersonaType.PROFESSIONAL: [
                "Good day. I'm pleased to assist you with your professional inquiries and business challenges. How may I provide value to your organization today?",
                "Welcome. I'm here to provide strategic insights and professional guidance tailored to your business needs. What objectives can I help you achieve?",
                "Hello. I'm ready to support your professional endeavors with comprehensive analysis and actionable recommendations. What business challenge shall we address?"
            ],
            
            PersonaType.EDUCATIONAL: [
                "Welcome, learner! I'm excited to be your guide on this educational journey. What would you like to explore and understand better today?",
                "Hello! Learning is such an adventure, and I'm thrilled to help you discover new knowledge and skills. What subject interests you?",
                "Hi there! Every question is a doorway to new understanding. What would you like to learn about today?"
            ],
            
            PersonaType.ANALYTICAL: [
                "Hello. I'm prepared to conduct thorough analysis and provide data-driven insights for your inquiry. What problem requires systematic examination?",
                "Welcome. I'm ready to apply analytical rigor to break down complex problems and provide evidence-based conclusions. What shall we analyze?",
                "Good day. I'm equipped to provide comprehensive analytical support with methodical reasoning and objective assessment. What requires investigation?"
            ]
        }
        
        # Task-specific templates
        self.templates[PromptCategory.TASK_SPECIFIC] = {
            "code_review": "Please review the following code for best practices, potential issues, and improvements:\n\n{code}\n\nProvide specific feedback on:\n- Code quality and readability\n- Performance considerations\n- Security implications\n- Suggested improvements",
            
            "explanation": "Please explain the following concept in detail, breaking it down into understandable components:\n\n{topic}\n\nInclude:\n- Key definitions and terminology\n- How it works or functions\n- Real-world applications or examples\n- Common misconceptions to avoid",
            
            "problem_solving": "I need help solving this problem:\n\n{problem}\n\nPlease provide:\n- Analysis of the problem\n- Possible approaches or solutions\n- Step-by-step implementation guidance\n- Potential challenges and how to address them",
            
            "creative_writing": "Help me with creative writing for:\n\n{context}\n\nPlease provide:\n- Creative ideas and concepts\n- Character or plot development suggestions\n- Style and tone recommendations\n- Specific examples or samples"
        }
        
        # Follow-up prompts
        self.templates[PromptCategory.FOLLOW_UP] = {
            "clarification": "Could you provide more details about {topic}? I'd like to give you the most helpful response possible.",
            "expansion": "Would you like me to elaborate on any particular aspect of {topic}?",
            "alternative": "Would you like me to suggest alternative approaches to {topic}?",
            "next_steps": "What would you like to explore next regarding {topic}?"
        }
        
        # Error handling templates
        self.templates[PromptCategory.ERROR_HANDLING] = {
            "api_error": "I apologize, but I'm experiencing technical difficulties connecting to the AI service. Please try again in a moment.",
            "rate_limit": "I'm currently handling a high volume of requests. Please wait a moment before trying again.",
            "invalid_input": "I'm having trouble understanding your request. Could you please rephrase or provide more context?",
            "general_error": "I encountered an unexpected error. Please try rephrasing your question or contact support if the issue persists."
        }
        
        # Persona-specific configurations
        self.persona_configs = {
            PersonaType.ASSISTANT: {
                "name": "AI Assistant",
                "description": "Helpful, knowledgeable, and friendly general-purpose assistant",
                "capabilities": ["general_help", "information_retrieval", "task_assistance", "problem_solving"],
                "tone": "professional_friendly",
                "expertise_level": "intermediate"
            },
            
            PersonaType.CREATIVE: {
                "name": "Creative Companion",
                "description": "Imaginative and artistic AI focused on creative expression",
                "capabilities": ["creative_writing", "brainstorming", "artistic_guidance", "innovation"],
                "tone": "inspiring_playful",
                "expertise_level": "advanced"
            },
            
            PersonaType.TECHNICAL: {
                "name": "Technical Expert",
                "description": "Specialized AI for programming, engineering, and technical solutions",
                "capabilities": ["coding", "debugging", "system_design", "technical_analysis"],
                "tone": "precise_professional",
                "expertise_level": "expert"
            },
            
            PersonaType.CASUAL: {
                "name": "Friendly Buddy",
                "description": "Laid-back and conversational AI companion",
                "capabilities": ["casual_chat", "general_help", "friendly_advice", "entertainment"],
                "tone": "relaxed_friendly",
                "expertise_level": "intermediate"
            },
            
            PersonaType.PROFESSIONAL: {
                "name": "Business Consultant",
                "description": "Professional AI for business and strategic guidance",
                "capabilities": ["business_analysis", "strategic_planning", "professional_advice", "consulting"],
                "tone": "formal_professional",
                "expertise_level": "expert"
            },
            
            PersonaType.EDUCATIONAL: {
                "name": "Learning Guide",
                "description": "Patient and encouraging AI educator",
                "capabilities": ["teaching", "explanation", "learning_support", "skill_development"],
                "tone": "encouraging_patient",
                "expertise_level": "advanced"
            },
            
            PersonaType.ANALYTICAL: {
                "name": "Data Analyst",
                "description": "Methodical AI focused on analysis and logical reasoning",
                "capabilities": ["data_analysis", "logical_reasoning", "research", "systematic_thinking"],
                "tone": "objective_methodical",
                "expertise_level": "expert"
            }
        }
    
    def get_system_prompt(self, persona: PersonaType) -> Dict[str, Any]:
        """
        Get the system prompt for a specific persona.
        
        Args:
            persona: The persona type to get the prompt for
            
        Returns:
            Dictionary containing the system prompt and configuration
            
        Raises:
            PromptTemplateError: If persona is not found
        """
        try:
            if persona not in self.templates[PromptCategory.SYSTEM]:
                raise PromptTemplateError(f"System prompt not found for persona: {persona}")
            
            return self.templates[PromptCategory.SYSTEM][persona].copy()
        except Exception as e:
            logger.error(f"Error getting system prompt for {persona}: {e}")
            raise PromptTemplateError(f"Failed to get system prompt: {e}")
    
    def get_conversation_starter(self, persona: PersonaType, index: Optional[int] = None) -> str:
        """
        Get a conversation starter for a specific persona.
        
        Args:
            persona: The persona type to get the starter for
            index: Optional specific index, otherwise returns a random one
            
        Returns:
            Conversation starter string
            
        Raises:
            PromptTemplateError: If persona is not found
        """
        try:
            if persona not in self.templates[PromptCategory.CONVERSATION_STARTER]:
                raise PromptTemplateError(f"Conversation starters not found for persona: {persona}")
            
            starters = self.templates[PromptCategory.CONVERSATION_STARTER][persona]
            
            if index is not None:
                if 0 <= index < len(starters):
                    return starters[index]
                else:
                    raise PromptTemplateError(f"Invalid starter index {index} for persona {persona}")
            
            # Return first starter as default
            return starters[0] if starters else "Hello! How can I help you today?"
            
        except Exception as e:
            logger.error(f"Error getting conversation starter for {persona}: {e}")
            raise PromptTemplateError(f"Failed to get conversation starter: {e}")
    
    def get_task_template(self, task_type: str, **kwargs) -> str:
        """
        Get a task-specific template with variable substitution.
        
        Args:
            task_type: The type of task template to retrieve
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted template string
            
        Raises:
            PromptTemplateError: If task type is not found
        """
        try:
            if task_type not in self.templates[PromptCategory.TASK_SPECIFIC]:
                raise PromptTemplateError(f"Task template not found: {task_type}")
            
            template = self.templates[PromptCategory.TASK_SPECIFIC][task_type]
            return template.format(**kwargs)
            
        except KeyError as e:
            logger.error(f"Missing template variable for {task_type}: {e}")
            raise PromptTemplateError(f"Missing required variable: {e}")
        except Exception as e:
            logger.error(f"Error formatting task template {task_type}: {e}")
            raise PromptTemplateError(f"Failed to format template: {e}")
    
    def get_follow_up_prompt(self, follow_up_type: str, **kwargs) -> str:
        """
        Get a follow-up prompt with variable substitution.
        
        Args:
            follow_up_type: The type of follow-up prompt
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted follow-up prompt
            
        Raises:
            PromptTemplateError: If follow-up type is not found
        """
        try:
            if follow_up_type not in self.templates[PromptCategory.FOLLOW_UP]:
                raise PromptTemplateError(f"Follow-up template not found: {follow_up_type}")
            
            template = self.templates[PromptCategory.FOLLOW_UP][follow_up_type]
            return template.format(**kwargs)
            
        except KeyError as e:
            logger.error(f"Missing template variable for {follow_up_type}: {e}")
            raise PromptTemplateError(f"Missing required variable: {e}")
        except Exception as e:
            logger.error(f"Error formatting follow-up template {follow_up_type}: {e}")
            raise PromptTemplateError(f"Failed to format template: {e}")
    
    def get_error_message(self, error_type: str) -> str:
        """
        Get an error handling message.
        
        Args:
            error_type: The type of error message to retrieve
            
        Returns:
            Error message string
        """
        return self.templates[PromptCategory.ERROR_HANDLING].get(
            error_type, 
            self.templates[PromptCategory.ERROR_HANDLING]["general_error"]
        )
    
    def get_persona_config(self, persona: PersonaType) -> Dict[str, Any]:
        """
        Get configuration information for a specific persona.
        
        Args:
            persona: The persona type to get configuration for
            
        Returns:
            Dictionary containing persona configuration
            
        Raises:
            PromptTemplateError: If persona is not found
        """
        try:
            if persona not in self.persona_configs:
                raise PromptTemplateError(f"Persona configuration not found: {persona}")
            
            return self.persona_configs[persona].copy()
        except Exception as e:
            logger.error(f"Error getting persona config for {persona}: {e}")
            raise PromptTemplateError(f"Failed to get persona config: {e}")
    
    def get_available_personas(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available personas with their configurations.
        
        Returns:
            List of dictionaries containing persona information
        """
        personas = []
        for persona_type in PersonaType:
            try:
                config = self.get_persona_config(persona_type)
                config["type"] = persona_type.value
                personas.append(config)
            except Exception as e:
                logger.warning(f"Could not load persona {persona_type}: {e}")
                continue
        
        return personas
    
    def add_custom_template(self, category: PromptCategory, key: str, template: Any):
        """
        Add a custom template to the system.
        
        Args:
            category: The category to add the template to
            key: The key to store the template under
            template: The template content
        """
        try:
            if category not in self.templates:
                self.templates[category] = {}
            
            self.templates[category][key] = template
            logger.info(f"Added custom template: {category.value}/{key}")
            
        except Exception as e:
            logger.error(f"Error adding custom template: {e}")
            raise PromptTemplateError(f"Failed to add custom template: {e}")
    
    def validate_template_variables(self, template: str, required_vars: List[str]) -> bool:
        """
        Validate that a template contains all required variables.
        
        Args:
            template: The template string to validate
            required_vars: List of required variable names
            
        Returns:
            True if all variables are present, False otherwise
        """
        try:
            for var in required_vars:
                if f"{{{var}}}" not in template:
                    logger.warning(f"Template missing required variable: {var}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating template variables: {e}")
            return False
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about the current template system.
        
        Returns:
            Dictionary containing template system information
        """
        info = {
            "total_personas": len(PersonaType),
            "available_personas": [p.value for p in PersonaType],
            "template_categories": [c.value for c in PromptCategory],
            "system_prompts_count": len(self.templates.get(PromptCategory.SYSTEM, {})),
            "conversation_starters_count": len(self.templates.get(PromptCategory.CONVERSATION_STARTER, {})),
            "task_templates_count": len(self.templates.get(PromptCategory.TASK_SPECIFIC, {})),
            "follow_up_templates_count": len(self.templates.get(PromptCategory.FOLLOW_UP, {})),
            "error_templates_count": len(self.templates.get(PromptCategory.ERROR_HANDLING, {}))
        }
        
        return info

# Module-level convenience functions
def get_default_prompt_templates() -> PromptTemplates:
    """Get a default instance of PromptTemplates"""
    return PromptTemplates()

def get_persona_types() -> List[str]:
    """Get a list of all available persona type values"""
    return [persona.value for persona in PersonaType]

def get_prompt_categories() -> List[str]:
    """Get a list of all available prompt category values"""
    return [category.value for category in PromptCategory]