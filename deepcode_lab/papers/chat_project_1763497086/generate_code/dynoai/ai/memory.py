"""
Memory Management System for DynoAI
Handles persistent conversation history, user preferences, and learning capabilities.
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

from ..config import get_config
from ..utils.helpers import (
    format_timestamp, sanitize_input, generate_session_id, 
    safe_json_loads, truncate_text, extract_keywords, 
    ensure_directory_exists, hash_string, get_file_size
)


@dataclass
class ConversationMemory:
    """Represents a stored conversation memory."""
    conversation_id: str
    user_id: str
    session_id: str
    timestamp: float
    messages: List[Dict[str, Any]]
    summary: str
    keywords: List[str]
    sentiment: str
    importance_score: float
    context_data: Dict[str, Any]


@dataclass
class UserPreference:
    """Represents user preferences and learning data."""
    user_id: str
    preference_type: str
    preference_value: Any
    confidence_score: float
    last_updated: float
    usage_count: int
    context: Dict[str, Any]


class MemoryDatabase:
    """SQLite database manager for conversation memory and user preferences."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_pool = {}
        self.lock = threading.Lock()
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-safe database connection."""
        thread_id = threading.get_ident()
        
        if thread_id not in self.connection_pool:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.connection_pool[thread_id] = conn
        
        return self.connection_pool[thread_id]
    
    def _initialize_database(self):
        """Initialize database tables."""
        ensure_directory_exists(os.path.dirname(self.db_path))
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                messages TEXT NOT NULL,
                summary TEXT,
                keywords TEXT,
                sentiment TEXT,
                importance_score REAL DEFAULT 0.0,
                context_data TEXT,
                created_at REAL DEFAULT (julianday('now')),
                updated_at REAL DEFAULT (julianday('now'))
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                confidence_score REAL DEFAULT 0.0,
                last_updated REAL NOT NULL,
                usage_count INTEGER DEFAULT 1,
                context TEXT,
                created_at REAL DEFAULT (julianday('now')),
                UNIQUE(user_id, preference_type)
            )
        ''')
        
        # Memory analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_preferences_user_id ON user_preferences(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON memory_analytics(user_id)')
        
        conn.commit()
    
    def store_conversation(self, memory: ConversationMemory) -> bool:
        """Store conversation memory in database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            with self.lock:
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, user_id, session_id, timestamp, messages, 
                     summary, keywords, sentiment, importance_score, context_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, julianday('now'))
                ''', (
                    memory.conversation_id,
                    memory.user_id,
                    memory.session_id,
                    memory.timestamp,
                    json.dumps(memory.messages),
                    memory.summary,
                    json.dumps(memory.keywords),
                    memory.sentiment,
                    memory.importance_score,
                    json.dumps(memory.context_data)
                ))
                conn.commit()
            
            return True
        except Exception as e:
            print(f"Error storing conversation: {e}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationMemory]:
        """Retrieve conversation memory by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM conversations WHERE conversation_id = ?
            ''', (conversation_id,))
            
            row = cursor.fetchone()
            if row:
                return ConversationMemory(
                    conversation_id=row['conversation_id'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    timestamp=row['timestamp'],
                    messages=safe_json_loads(row['messages']) or [],
                    summary=row['summary'] or '',
                    keywords=safe_json_loads(row['keywords']) or [],
                    sentiment=row['sentiment'] or 'neutral',
                    importance_score=row['importance_score'] or 0.0,
                    context_data=safe_json_loads(row['context_data']) or {}
                )
            return None
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 50, 
                             days_back: int = 30) -> List[ConversationMemory]:
        """Get recent conversations for a user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_time = datetime.now().timestamp() - (days_back * 24 * 3600)
            
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, cutoff_time, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append(ConversationMemory(
                    conversation_id=row['conversation_id'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    timestamp=row['timestamp'],
                    messages=safe_json_loads(row['messages']) or [],
                    summary=row['summary'] or '',
                    keywords=safe_json_loads(row['keywords']) or [],
                    sentiment=row['sentiment'] or 'neutral',
                    importance_score=row['importance_score'] or 0.0,
                    context_data=safe_json_loads(row['context_data']) or {}
                ))
            
            return conversations
        except Exception as e:
            print(f"Error retrieving user conversations: {e}")
            return []
    
    def store_user_preference(self, preference: UserPreference) -> bool:
        """Store or update user preference."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            with self.lock:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, preference_type, preference_value, confidence_score, 
                     last_updated, usage_count, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    preference.user_id,
                    preference.preference_type,
                    json.dumps(preference.preference_value),
                    preference.confidence_score,
                    preference.last_updated,
                    preference.usage_count,
                    json.dumps(preference.context)
                ))
                conn.commit()
            
            return True
        except Exception as e:
            print(f"Error storing user preference: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> List[UserPreference]:
        """Get all preferences for a user."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_preferences WHERE user_id = ?
                ORDER BY confidence_score DESC, usage_count DESC
            ''', (user_id,))
            
            preferences = []
            for row in cursor.fetchall():
                preferences.append(UserPreference(
                    user_id=row['user_id'],
                    preference_type=row['preference_type'],
                    preference_value=safe_json_loads(row['preference_value']),
                    confidence_score=row['confidence_score'],
                    last_updated=row['last_updated'],
                    usage_count=row['usage_count'],
                    context=safe_json_loads(row['context']) or {}
                ))
            
            return preferences
        except Exception as e:
            print(f"Error retrieving user preferences: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> int:
        """Clean up old conversation data."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            with self.lock:
                cursor.execute('''
                    DELETE FROM conversations 
                    WHERE timestamp < ? AND importance_score < 0.5
                ''', (cutoff_time,))
                
                deleted_count = cursor.rowcount
                conn.commit()
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return 0


class ConversationMemoryManager:
    """Manages conversation memory and learning capabilities."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.db_path = os.path.join(self.config.DATA_DIR, 'conversations', 'memory.db')
        self.database = MemoryDatabase(self.db_path)
        self.user_contexts = defaultdict(dict)
        self.learning_enabled = getattr(self.config, 'ENABLE_LEARNING', True)
        
        # Memory configuration
        self.max_conversation_age_days = getattr(self.config, 'MAX_CONVERSATION_AGE_DAYS', 30)
        self.max_conversations_per_user = getattr(self.config, 'MAX_CONVERSATIONS_PER_USER', 100)
        self.importance_threshold = getattr(self.config, 'IMPORTANCE_THRESHOLD', 0.3)
    
    def store_conversation(self, conversation_id: str, user_id: str, session_id: str,
                         messages: List[Dict[str, Any]], context_data: Dict[str, Any] = None) -> bool:
        """Store a conversation in memory with analysis."""
        try:
            # Generate conversation summary and analysis
            summary = self._generate_conversation_summary(messages)
            keywords = self._extract_conversation_keywords(messages)
            sentiment = self._analyze_sentiment(messages)
            importance_score = self._calculate_importance_score(messages, keywords, sentiment)
            
            # Create memory object
            memory = ConversationMemory(
                conversation_id=conversation_id,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.now().timestamp(),
                messages=messages,
                summary=summary,
                keywords=keywords,
                sentiment=sentiment,
                importance_score=importance_score,
                context_data=context_data or {}
            )
            
            # Store in database
            success = self.database.store_conversation(memory)
            
            # Learn from conversation if enabled
            if success and self.learning_enabled:
                self._learn_from_conversation(memory)
            
            return success
        except Exception as e:
            print(f"Error storing conversation memory: {e}")
            return False
    
    def get_conversation_context(self, user_id: str, current_session_id: str = None,
                               max_conversations: int = 5) -> Dict[str, Any]:
        """Get relevant conversation context for a user."""
        try:
            # Get recent conversations
            conversations = self.database.get_user_conversations(
                user_id, 
                limit=max_conversations * 2,  # Get more to filter
                days_back=self.max_conversation_age_days
            )
            
            # Filter and prioritize conversations
            relevant_conversations = []
            for conv in conversations:
                if conv.importance_score >= self.importance_threshold:
                    relevant_conversations.append(conv)
                
                if len(relevant_conversations) >= max_conversations:
                    break
            
            # Build context
            context = {
                'user_id': user_id,
                'conversation_count': len(relevant_conversations),
                'recent_topics': self._extract_recent_topics(relevant_conversations),
                'user_preferences': self._get_user_context_preferences(user_id),
                'conversation_summaries': [
                    {
                        'id': conv.conversation_id,
                        'summary': conv.summary,
                        'keywords': conv.keywords,
                        'sentiment': conv.sentiment,
                        'timestamp': format_timestamp(conv.timestamp)
                    }
                    for conv in relevant_conversations[:3]  # Top 3 most relevant
                ],
                'learning_insights': self._get_learning_insights(user_id)
            }
            
            return context
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return {'user_id': user_id, 'conversation_count': 0}
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned user preferences."""
        try:
            preferences = self.database.get_user_preferences(user_id)
            
            # Organize preferences by type
            organized_prefs = {}
            for pref in preferences:
                organized_prefs[pref.preference_type] = {
                    'value': pref.preference_value,
                    'confidence': pref.confidence_score,
                    'usage_count': pref.usage_count,
                    'last_updated': format_timestamp(pref.last_updated)
                }
            
            return organized_prefs
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return {}
    
    def update_user_preference(self, user_id: str, preference_type: str, 
                             preference_value: Any, confidence_score: float = 0.5,
                             context: Dict[str, Any] = None) -> bool:
        """Update or create a user preference."""
        try:
            # Get existing preference to update usage count
            existing_prefs = self.database.get_user_preferences(user_id)
            usage_count = 1
            
            for pref in existing_prefs:
                if pref.preference_type == preference_type:
                    usage_count = pref.usage_count + 1
                    break
            
            # Create preference object
            preference = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_value=preference_value,
                confidence_score=confidence_score,
                last_updated=datetime.now().timestamp(),
                usage_count=usage_count,
                context=context or {}
            )
            
            return self.database.store_user_preference(preference)
        except Exception as e:
            print(f"Error updating user preference: {e}")
            return False
    
    def search_conversations(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by keywords or content."""
        try:
            conversations = self.database.get_user_conversations(user_id, limit=100)
            query_keywords = extract_keywords(query.lower())
            
            # Score conversations based on relevance
            scored_conversations = []
            for conv in conversations:
                score = 0
                
                # Check keywords match
                for keyword in query_keywords:
                    if keyword in conv.keywords:
                        score += 2
                    if keyword in conv.summary.lower():
                        score += 1
                
                # Check message content
                for message in conv.messages:
                    content = message.get('content', '').lower()
                    for keyword in query_keywords:
                        if keyword in content:
                            score += 0.5
                
                if score > 0:
                    scored_conversations.append((score, conv))
            
            # Sort by score and return top results
            scored_conversations.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for score, conv in scored_conversations[:limit]:
                results.append({
                    'conversation_id': conv.conversation_id,
                    'summary': conv.summary,
                    'keywords': conv.keywords,
                    'timestamp': format_timestamp(conv.timestamp),
                    'relevance_score': score,
                    'message_count': len(conv.messages)
                })
            
            return results
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for backup or transfer."""
        try:
            conversations = self.database.get_user_conversations(user_id, limit=1000, days_back=365)
            preferences = self.database.get_user_preferences(user_id)
            
            export_data = {
                'user_id': user_id,
                'export_timestamp': format_timestamp(),
                'conversations': [asdict(conv) for conv in conversations],
                'preferences': [asdict(pref) for pref in preferences],
                'statistics': {
                    'total_conversations': len(conversations),
                    'total_preferences': len(preferences),
                    'date_range': {
                        'earliest': format_timestamp(min(conv.timestamp for conv in conversations)) if conversations else None,
                        'latest': format_timestamp(max(conv.timestamp for conv in conversations)) if conversations else None
                    }
                }
            }
            
            return export_data
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old conversation data."""
        try:
            deleted_conversations = self.database.cleanup_old_data(days_to_keep=90)
            
            return {
                'deleted_conversations': deleted_conversations,
                'cleanup_timestamp': format_timestamp()
            }
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return {'error': str(e)}
    
    def _generate_conversation_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a summary of the conversation."""
        try:
            if not messages:
                return ""
            
            # Extract key points from messages
            key_points = []
            for message in messages[-5:]:  # Last 5 messages
                content = message.get('content', '')
                if len(content) > 50:  # Only meaningful messages
                    key_points.append(truncate_text(content, 100))
            
            if key_points:
                return " | ".join(key_points)
            else:
                return "Brief conversation"
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Conversation summary unavailable"
    
    def _extract_conversation_keywords(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract keywords from conversation messages."""
        try:
            all_text = ""
            for message in messages:
                content = message.get('content', '')
                all_text += f" {content}"
            
            return extract_keywords(all_text, max_keywords=15)
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def _analyze_sentiment(self, messages: List[Dict[str, Any]]) -> str:
        """Analyze overall sentiment of the conversation."""
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'like', 'amazing', 'wonderful']
            negative_words = ['bad', 'terrible', 'hate', 'dislike', 'awful', 'horrible', 'sad', 'angry']
            
            positive_count = 0
            negative_count = 0
            
            for message in messages:
                content = message.get('content', '').lower()
                for word in positive_words:
                    if word in content:
                        positive_count += 1
                for word in negative_words:
                    if word in content:
                        negative_count += 1
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return 'neutral'
    
    def _calculate_importance_score(self, messages: List[Dict[str, Any]], 
                                  keywords: List[str], sentiment: str) -> float:
        """Calculate importance score for the conversation."""
        try:
            score = 0.0
            
            # Message count factor
            message_count = len(messages)
            if message_count > 10:
                score += 0.3
            elif message_count > 5:
                score += 0.2
            elif message_count > 2:
                score += 0.1
            
            # Keyword richness factor
            if len(keywords) > 10:
                score += 0.3
            elif len(keywords) > 5:
                score += 0.2
            
            # Sentiment factor
            if sentiment == 'positive':
                score += 0.2
            elif sentiment == 'negative':
                score += 0.1  # Negative conversations might be important for learning
            
            # Message length factor
            total_length = sum(len(msg.get('content', '')) for msg in messages)
            if total_length > 1000:
                score += 0.2
            elif total_length > 500:
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
        except Exception as e:
            print(f"Error calculating importance score: {e}")
            return 0.5
    
    def _learn_from_conversation(self, memory: ConversationMemory):
        """Learn user preferences from conversation."""
        try:
            # Extract potential preferences
            messages = memory.messages
            user_id = memory.user_id
            
            # Learn communication style preferences
            avg_message_length = sum(len(msg.get('content', '')) for msg in messages if msg.get('role') == 'user') / max(1, len([m for m in messages if m.get('role') == 'user']))
            
            if avg_message_length > 200:
                self.update_user_preference(user_id, 'communication_style', 'detailed', 0.6)
            elif avg_message_length < 50:
                self.update_user_preference(user_id, 'communication_style', 'brief', 0.6)
            
            # Learn topic interests from keywords
            if memory.keywords:
                for keyword in memory.keywords[:5]:  # Top 5 keywords
                    self.update_user_preference(user_id, f'topic_interest_{keyword}', True, 0.4)
            
            # Learn from sentiment patterns
            if memory.sentiment != 'neutral':
                self.update_user_preference(user_id, 'typical_sentiment', memory.sentiment, 0.3)
        except Exception as e:
            print(f"Error learning from conversation: {e}")
    
    def _extract_recent_topics(self, conversations: List[ConversationMemory]) -> List[str]:
        """Extract recent topics from conversations."""
        try:
            all_keywords = []
            for conv in conversations:
                all_keywords.extend(conv.keywords)
            
            # Count keyword frequency
            keyword_counts = defaultdict(int)
            for keyword in all_keywords:
                keyword_counts[keyword] += 1
            
            # Return top topics
            sorted_topics = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in sorted_topics[:10]]
        except Exception as e:
            print(f"Error extracting recent topics: {e}")
            return []
    
    def _get_user_context_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences relevant for conversation context."""
        try:
            all_prefs = self.get_user_preferences(user_id)
            
            # Filter for context-relevant preferences
            context_prefs = {}
            for pref_type, pref_data in all_prefs.items():
                if pref_type in ['communication_style', 'typical_sentiment'] or pref_type.startswith('topic_interest_'):
                    context_prefs[pref_type] = pref_data
            
            return context_prefs
        except Exception as e:
            print(f"Error getting context preferences: {e}")
            return {}
    
    def _get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """Get learning insights about the user."""
        try:
            conversations = self.database.get_user_conversations(user_id, limit=20)
            
            if not conversations:
                return {}
            
            # Calculate insights
            total_messages = sum(len(conv.messages) for conv in conversations)
            avg_conversation_length = total_messages / len(conversations)
            
            sentiments = [conv.sentiment for conv in conversations]
            most_common_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else 'neutral'
            
            return {
                'total_conversations': len(conversations),
                'avg_conversation_length': round(avg_conversation_length, 1),
                'most_common_sentiment': most_common_sentiment,
                'engagement_level': 'high' if avg_conversation_length > 10 else 'medium' if avg_conversation_length > 5 else 'low'
            }
        except Exception as e:
            print(f"Error getting learning insights: {e}")
            return {}


# Global memory manager instance
_memory_manager = None


def get_memory_manager(config=None) -> ConversationMemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = ConversationMemoryManager(config)
    return _memory_manager


def initialize_memory_system(config=None) -> bool:
    """Initialize the memory system."""
    try:
        global _memory_manager
        _memory_manager = ConversationMemoryManager(config)
        return True
    except Exception as e:
        print(f"Error initializing memory system: {e}")
        return False


def shutdown_memory_system():
    """Shutdown the memory system."""
    global _memory_manager
    if _memory_manager:
        # Perform cleanup if needed
        _memory_manager.cleanup_old_data()
        _memory_manager = None