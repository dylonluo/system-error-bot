from typing import Dict, Any, Optional, List
from datetime import datetime


class ChatInterfaceClient:
    """Mock client for Chat Interface Context."""
    
    def __init__(self):
        # Mock conversations database
        self._conversations = {
            'conv-001': {
                'conversation_id': 'conv-001',
                'user_id': 'user-123',
                'created_at': datetime.now().isoformat(),
                'messages': [
                    {
                        'role': 'user',
                        'content': 'How do I reset my password?',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'role': 'assistant',
                        'content': 'To reset your password, go to Settings > Security > Reset Password.',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'role': 'user',
                        'content': 'I tried that but it\'s not working. Can someone help me?',
                        'timestamp': datetime.now().isoformat()
                    }
                ],
                'screenshots': []
            },
            'conv-002': {
                'conversation_id': 'conv-002',
                'user_id': 'user-123',
                'created_at': datetime.now().isoformat(),
                'messages': [
                    {
                        'role': 'user',
                        'content': 'What are the system requirements?',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'role': 'assistant',
                        'content': 'The system requires Windows 10 or later, 8GB RAM, and 50GB disk space.',
                        'timestamp': datetime.now().isoformat()
                    }
                ],
                'screenshots': []
            }
        }
    
    def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history by conversation ID."""
        return self._conversations.get(conversation_id)
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages from a conversation."""
        conversation = self._conversations.get(conversation_id)
        if conversation:
            return conversation.get('messages', [])
        return []
