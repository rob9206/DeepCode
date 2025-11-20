"""
DynoAI Plugin System
===================

Extensible plugin system for DynoAI that provides additional capabilities like weather,
calculations, web search, and memory assistance. Plugins are dynamically loaded and
can be enabled/disabled through configuration.

Key Features:
- Dynamic plugin loading and management
- Weather information retrieval
- Mathematical calculations
- Web search capabilities
- Memory assistance and context management
- Plugin configuration and validation
"""

import json
import re
import requests
import math
import operator
import ast
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
import logging

from ..config import get_config, PLUGIN_CONFIGS
from ..utils.helpers import (
    sanitize_input, validate_api_key, safe_json_loads, 
    format_timestamp, extract_keywords, hash_string
)

# Configure logging
logger = logging.getLogger(__name__)

class PluginError(Exception):
    """Custom exception for plugin-related errors"""
    pass

class BasePlugin(ABC):
    """Abstract base class for all DynoAI plugins"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__.lower().replace('plugin', '')
        self.enabled = self.config.get('enabled', True)
        self.priority = self.config.get('priority', 50)
        
    @abstractmethod
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the plugin functionality"""
        pass
    
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Check if this plugin can handle the given query"""
        pass
    
    def get_help(self) -> str:
        """Return help text for this plugin"""
        return f"Plugin: {self.name}"
    
    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        return True

class WeatherPlugin(BasePlugin):
    """Weather information plugin using OpenWeatherMap API"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key', '')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.weather_patterns = [
            r'\b(?:weather|temperature|temp|forecast|rain|snow|sunny|cloudy)\b',
            r'\b(?:how\'s the weather|what\'s the weather)\b',
            r'\b(?:weather in|weather for)\b'
        ]
    
    def can_handle(self, query: str) -> bool:
        """Check if query is weather-related"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.weather_patterns)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get weather information"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'Weather API key not configured',
                    'response': 'Weather service is not available. Please configure the API key.'
                }
            
            # Extract location from query
            location = self._extract_location(query)
            if not location:
                location = self.config.get('default_location', 'New York')
            
            # Get weather data
            weather_data = self._get_weather_data(location)
            if not weather_data:
                return {
                    'success': False,
                    'error': 'Failed to fetch weather data',
                    'response': f'Sorry, I couldn\'t get weather information for {location}.'
                }
            
            # Format response
            response = self._format_weather_response(weather_data, location)
            
            return {
                'success': True,
                'plugin': 'weather',
                'data': weather_data,
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Weather plugin error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error getting weather information.'
            }
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from weather query"""
        # Look for "in [location]" or "for [location]" patterns
        patterns = [
            r'\b(?:in|for)\s+([A-Za-z\s,]+?)(?:\s|$|\?)',
            r'\b([A-Za-z\s,]+?)\s+weather\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:  # Basic validation
                    return location
        
        return None
    
    def _get_weather_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Fetch weather data from API"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return None
    
    def _format_weather_response(self, data: Dict[str, Any], location: str) -> str:
        """Format weather data into readable response"""
        try:
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description'].title()
            
            response = f"Weather in {location}:\n"
            response += f"🌡️ Temperature: {temp}°C (feels like {feels_like}°C)\n"
            response += f"☁️ Conditions: {description}\n"
            response += f"💧 Humidity: {humidity}%"
            
            return response
            
        except KeyError as e:
            logger.error(f"Weather data formatting error: {str(e)}")
            return f"Weather data available for {location}, but formatting failed."
    
    def get_help(self) -> str:
        return "Weather Plugin: Ask about weather conditions, temperature, or forecast for any location."

class CalculatorPlugin(BasePlugin):
    """Mathematical calculation plugin with safe expression evaluation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.math_patterns = [
            r'\b(?:calculate|compute|solve|math|arithmetic)\b',
            r'\b(?:what is|what\'s)\s+[\d\+\-\*\/\(\)\s]+',
            r'[\d\+\-\*\/\(\)\s]+\s*=\s*\?',
            r'\b(?:square root|sqrt|sin|cos|tan|log)\b'
        ]
        
        # Safe operators and functions
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        self.safe_functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            'pi': math.pi,
            'e': math.e
        }
    
    def can_handle(self, query: str) -> bool:
        """Check if query is math-related"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.math_patterns)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform mathematical calculations"""
        try:
            # Extract mathematical expression
            expression = self._extract_expression(query)
            if not expression:
                return {
                    'success': False,
                    'error': 'No valid mathematical expression found',
                    'response': 'I couldn\'t find a mathematical expression to calculate.'
                }
            
            # Evaluate expression safely
            result = self._safe_eval(expression)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Invalid or unsafe expression',
                    'response': 'Sorry, I couldn\'t evaluate that mathematical expression safely.'
                }
            
            # Format response
            response = f"🧮 Calculation: {expression} = {result}"
            
            return {
                'success': True,
                'plugin': 'calculator',
                'data': {
                    'expression': expression,
                    'result': result
                },
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Calculator plugin error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error performing the calculation.'
            }
    
    def _extract_expression(self, query: str) -> Optional[str]:
        """Extract mathematical expression from query"""
        # Clean the query
        query = re.sub(r'\b(?:calculate|compute|solve|what is|what\'s)\b', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\?', '', query)
        query = query.strip()
        
        # Look for mathematical patterns
        math_pattern = r'[\d\+\-\*\/\(\)\.\s]+'
        match = re.search(math_pattern, query)
        
        if match:
            expression = match.group().strip()
            # Basic validation
            if any(char.isdigit() for char in expression) and any(op in expression for op in '+-*/'):
                return expression
        
        return None
    
    def _safe_eval(self, expression: str) -> Optional[Union[int, float]]:
        """Safely evaluate mathematical expression"""
        try:
            # Parse the expression
            node = ast.parse(expression, mode='eval')
            
            # Evaluate safely
            result = self._eval_node(node.body)
            
            # Round to reasonable precision
            if isinstance(result, float):
                result = round(result, 10)
            
            return result
            
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError) as e:
            logger.error(f"Math evaluation error: {str(e)}")
            return None
    
    def _eval_node(self, node):
        """Recursively evaluate AST nodes safely"""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.safe_operators.get(type(node.op))
            if op:
                return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = self.safe_operators.get(type(node.op))
            if op:
                return op(operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name in self.safe_functions:
                args = [self._eval_node(arg) for arg in node.args]
                return self.safe_functions[func_name](*args)
        
        raise ValueError(f"Unsupported operation: {type(node)}")
    
    def get_help(self) -> str:
        return "Calculator Plugin: Perform mathematical calculations, including basic arithmetic and common functions."

class WebSearchPlugin(BasePlugin):
    """Web search plugin using DuckDuckGo Instant Answer API"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.search_patterns = [
            r'\b(?:search|google|find|look up|what is|who is|when is|where is)\b',
            r'\b(?:tell me about|information about)\b'
        ]
        self.ddg_api_url = "https://api.duckduckgo.com/"
    
    def can_handle(self, query: str) -> bool:
        """Check if query is search-related"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.search_patterns)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform web search"""
        try:
            # Extract search terms
            search_query = self._extract_search_query(query)
            if not search_query:
                return {
                    'success': False,
                    'error': 'No search terms found',
                    'response': 'I couldn\'t determine what to search for.'
                }
            
            # Perform search
            search_results = self._search_duckduckgo(search_query)
            
            if not search_results:
                return {
                    'success': False,
                    'error': 'No search results found',
                    'response': f'I couldn\'t find any information about "{search_query}".'
                }
            
            # Format response
            response = self._format_search_response(search_results, search_query)
            
            return {
                'success': True,
                'plugin': 'web_search',
                'data': {
                    'query': search_query,
                    'results': search_results
                },
                'response': response
            }
            
        except Exception as e:
            logger.error(f"Web search plugin error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error performing the web search.'
            }
    
    def _extract_search_query(self, query: str) -> Optional[str]:
        """Extract search terms from query"""
        # Remove common search prefixes
        prefixes = [
            r'\b(?:search for|google|find|look up|tell me about|information about)\b',
            r'\b(?:what is|who is|when is|where is)\b'
        ]
        
        search_query = query
        for prefix in prefixes:
            search_query = re.sub(prefix, '', search_query, flags=re.IGNORECASE)
        
        search_query = search_query.strip()
        
        # Basic validation
        if len(search_query) > 2:
            return search_query
        
        return None
    
    def _search_duckduckgo(self, query: str) -> Optional[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(self.ddg_api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract useful information
            result = {}
            
            if data.get('Abstract'):
                result['abstract'] = data['Abstract']
                result['source'] = data.get('AbstractSource', '')
                result['url'] = data.get('AbstractURL', '')
            
            if data.get('Answer'):
                result['answer'] = data['Answer']
                result['answer_type'] = data.get('AnswerType', '')
            
            if data.get('Definition'):
                result['definition'] = data['Definition']
                result['definition_source'] = data.get('DefinitionSource', '')
            
            return result if result else None
            
        except requests.RequestException as e:
            logger.error(f"DuckDuckGo API request failed: {str(e)}")
            return None
    
    def _format_search_response(self, results: Dict[str, Any], query: str) -> str:
        """Format search results into readable response"""
        response = f"🔍 Search results for '{query}':\n\n"
        
        if results.get('answer'):
            response += f"📋 Answer: {results['answer']}\n\n"
        
        if results.get('definition'):
            response += f"📖 Definition: {results['definition']}\n"
            if results.get('definition_source'):
                response += f"Source: {results['definition_source']}\n\n"
        
        if results.get('abstract'):
            response += f"📄 Summary: {results['abstract']}\n"
            if results.get('source'):
                response += f"Source: {results['source']}\n"
            if results.get('url'):
                response += f"More info: {results['url']}\n"
        
        return response.strip()
    
    def get_help(self) -> str:
        return "Web Search Plugin: Search for information, definitions, and answers from the web."

class MemoryAssistantPlugin(BasePlugin):
    """Memory assistance plugin for conversation context and reminders"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.memory_patterns = [
            r'\b(?:remember|recall|remind|memory|note|save)\b',
            r'\b(?:what did I|what was|when did)\b',
            r'\b(?:forget|delete|remove)\b'
        ]
        self.user_notes = {}  # Simple in-memory storage
    
    def can_handle(self, query: str) -> bool:
        """Check if query is memory-related"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.memory_patterns)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle memory operations"""
        try:
            query_lower = query.lower()
            user_id = context.get('user_id', 'default') if context else 'default'
            
            # Initialize user notes if needed
            if user_id not in self.user_notes:
                self.user_notes[user_id] = []
            
            # Determine operation type
            if 'remember' in query_lower or 'note' in query_lower or 'save' in query_lower:
                return self._save_note(query, user_id)
            elif 'recall' in query_lower or 'what did' in query_lower or 'what was' in query_lower:
                return self._recall_information(query, user_id, context)
            elif 'forget' in query_lower or 'delete' in query_lower or 'remove' in query_lower:
                return self._forget_information(query, user_id)
            else:
                return self._general_memory_help(user_id)
                
        except Exception as e:
            logger.error(f"Memory assistant plugin error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error with memory operations.'
            }
    
    def _save_note(self, query: str, user_id: str) -> Dict[str, Any]:
        """Save a note or reminder"""
        # Extract the content to remember
        content = re.sub(r'\b(?:remember|note|save)\b', '', query, flags=re.IGNORECASE).strip()
        
        if not content:
            return {
                'success': False,
                'error': 'No content to remember',
                'response': 'What would you like me to remember?'
            }
        
        # Create note entry
        note = {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'id': hash_string(content + str(datetime.now()))[:8]
        }
        
        self.user_notes[user_id].append(note)
        
        return {
            'success': True,
            'plugin': 'memory_assistant',
            'data': note,
            'response': f"📝 I've saved that note: \"{content}\""
        }
    
    def _recall_information(self, query: str, user_id: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Recall saved information"""
        user_notes = self.user_notes.get(user_id, [])
        
        if not user_notes:
            return {
                'success': True,
                'plugin': 'memory_assistant',
                'data': {'notes': []},
                'response': "🧠 I don't have any saved notes for you yet."
            }
        
        # Search through notes
        search_terms = extract_keywords(query.lower())
        relevant_notes = []
        
        for note in user_notes:
            note_keywords = extract_keywords(note['content'].lower())
            if any(term in note_keywords for term in search_terms):
                relevant_notes.append(note)
        
        if not relevant_notes:
            # Return recent notes if no specific matches
            relevant_notes = user_notes[-3:]  # Last 3 notes
        
        # Format response
        response = "🧠 Here's what I remember:\n\n"
        for note in relevant_notes[-5:]:  # Limit to 5 most relevant
            timestamp = datetime.fromisoformat(note['timestamp']).strftime("%Y-%m-%d %H:%M")
            response += f"📝 {note['content']} (saved {timestamp})\n"
        
        return {
            'success': True,
            'plugin': 'memory_assistant',
            'data': {'notes': relevant_notes},
            'response': response.strip()
        }
    
    def _forget_information(self, query: str, user_id: str) -> Dict[str, Any]:
        """Remove saved information"""
        user_notes = self.user_notes.get(user_id, [])
        
        if not user_notes:
            return {
                'success': True,
                'plugin': 'memory_assistant',
                'data': {'removed': 0},
                'response': "🧠 There are no notes to remove."
            }
        
        # Extract what to forget
        content = re.sub(r'\b(?:forget|delete|remove)\b', '', query, flags=re.IGNORECASE).strip()
        
        if 'all' in content.lower() or 'everything' in content.lower():
            # Clear all notes
            removed_count = len(user_notes)
            self.user_notes[user_id] = []
            return {
                'success': True,
                'plugin': 'memory_assistant',
                'data': {'removed': removed_count},
                'response': f"🧠 I've forgotten all {removed_count} notes."
            }
        
        # Search and remove specific notes
        search_terms = extract_keywords(content.lower())
        original_count = len(user_notes)
        
        self.user_notes[user_id] = [
            note for note in user_notes
            if not any(term in note['content'].lower() for term in search_terms)
        ]
        
        removed_count = original_count - len(self.user_notes[user_id])
        
        return {
            'success': True,
            'plugin': 'memory_assistant',
            'data': {'removed': removed_count},
            'response': f"🧠 I've forgotten {removed_count} note(s) related to '{content}'."
        }
    
    def _general_memory_help(self, user_id: str) -> Dict[str, Any]:
        """Provide general memory assistance"""
        user_notes = self.user_notes.get(user_id, [])
        note_count = len(user_notes)
        
        response = f"🧠 Memory Assistant:\n"
        response += f"📊 You have {note_count} saved note(s).\n\n"
        response += "Commands:\n"
        response += "• 'Remember [something]' - Save a note\n"
        response += "• 'What did I say about [topic]' - Recall notes\n"
        response += "• 'Forget [something]' - Remove notes\n"
        response += "• 'Forget all' - Clear all notes"
        
        return {
            'success': True,
            'plugin': 'memory_assistant',
            'data': {'note_count': note_count},
            'response': response
        }
    
    def get_help(self) -> str:
        return "Memory Assistant Plugin: Save notes, recall information, and manage conversation memory."

class PluginManager:
    """Central plugin management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config()
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs = PLUGIN_CONFIGS
        self._initialize_plugins()
    
    def _initialize_plugins(self):
        """Initialize all configured plugins"""
        try:
            # Weather Plugin
            if self.plugin_configs.get('weather', {}).get('enabled', True):
                self.plugins['weather'] = WeatherPlugin(self.plugin_configs.get('weather', {}))
            
            # Calculator Plugin
            if self.plugin_configs.get('calculator', {}).get('enabled', True):
                self.plugins['calculator'] = CalculatorPlugin(self.plugin_configs.get('calculator', {}))
            
            # Web Search Plugin
            if self.plugin_configs.get('web_search', {}).get('enabled', True):
                self.plugins['web_search'] = WebSearchPlugin(self.plugin_configs.get('web_search', {}))
            
            # Memory Assistant Plugin
            if self.plugin_configs.get('memory_assistant', {}).get('enabled', True):
                self.plugins['memory_assistant'] = MemoryAssistantPlugin(self.plugin_configs.get('memory_assistant', {}))
            
            logger.info(f"Initialized {len(self.plugins)} plugins: {list(self.plugins.keys())}")
            
        except Exception as e:
            logger.error(f"Plugin initialization error: {str(e)}")
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Process query through available plugins"""
        try:
            # Sanitize input
            query = sanitize_input(query)
            
            # Find suitable plugins
            suitable_plugins = []
            for name, plugin in self.plugins.items():
                if plugin.enabled and plugin.can_handle(query):
                    suitable_plugins.append((plugin.priority, name, plugin))
            
            if not suitable_plugins:
                return None
            
            # Sort by priority (higher priority first)
            suitable_plugins.sort(reverse=True)
            
            # Execute the highest priority plugin
            _, plugin_name, plugin = suitable_plugins[0]
            
            logger.info(f"Executing plugin: {plugin_name} for query: {query[:50]}...")
            result = plugin.execute(query, context)
            
            # Add plugin metadata
            if result:
                result['plugin_name'] = plugin_name
                result['timestamp'] = format_timestamp()
            
            return result
            
        except Exception as e:
            logger.error(f"Plugin processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error processing your request with plugins.'
            }
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get specific plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all available plugins with their status"""
        plugin_list = {}
        for name, plugin in self.plugins.items():
            plugin_list[name] = {
                'enabled': plugin.enabled,
                'priority': plugin.priority,
                'help': plugin.get_help()
            }
        return plugin_list
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a specific plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = True
            logger.info(f"Enabled plugin: {name}")
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a specific plugin"""
        if name in self.plugins:
            self.plugins[name].enabled = False
            logger.info(f"Disabled plugin: {name}")
            return True
        return False
    
    def get_help(self) -> str:
        """Get help text for all plugins"""
        help_text = "🔌 Available Plugins:\n\n"
        for name, plugin in self.plugins.items():
            status = "✅" if plugin.enabled else "❌"
            help_text += f"{status} {plugin.get_help()}\n"
        return help_text

# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager(config: Optional[Dict[str, Any]] = None) -> PluginManager:
    """Get global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager(config)
    return _plugin_manager

def initialize_plugin_system(config: Optional[Dict[str, Any]] = None) -> bool:
    """Initialize the plugin system"""
    try:
        global _plugin_manager
        _plugin_manager = PluginManager(config)
        logger.info("Plugin system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize plugin system: {str(e)}")
        return False

def shutdown_plugin_system():
    """Shutdown the plugin system"""
    global _plugin_manager
    if _plugin_manager:
        logger.info("Plugin system shutdown")
        _plugin_manager = None