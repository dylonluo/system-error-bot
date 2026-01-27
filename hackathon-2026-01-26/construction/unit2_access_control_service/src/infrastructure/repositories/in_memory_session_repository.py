"""In-Memory Session Repository - In-memory implementation for testing/demo."""
from datetime import datetime
from typing import Dict, List, Optional

from ...domain.aggregates import Session
from ...domain.value_objects import SessionId, UserId
from ...domain.repositories import ISessionRepository


class InMemorySessionRepository(ISessionRepository):
    """In-memory implementation of session repository."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._sessions: Dict[str, Session] = {}  # Key: session_id string
        self._user_sessions: Dict[str, List[str]] = {}  # Key: user_id, Value: list of session_ids
        self._token_index: Dict[str, str] = {}  # Key: access_token, Value: session_id
    
    def save(self, session: Session) -> None:
        """Save or update a session."""
        session_id_str = str(session.session_id)
        user_id_str = str(session.user_id)
        
        # Save session
        self._sessions[session_id_str] = session
        
        # Update user sessions index
        if user_id_str not in self._user_sessions:
            self._user_sessions[user_id_str] = []
        if session_id_str not in self._user_sessions[user_id_str]:
            self._user_sessions[user_id_str].append(session_id_str)
        
        # Update token index
        self._token_index[session.access_token.value] = session_id_str
    
    def find_by_id(self, session_id: SessionId) -> Optional[Session]:
        """Find session by ID."""
        return self._sessions.get(str(session_id))
    
    def find_by_user_id(self, user_id: UserId) -> List[Session]:
        """Find all sessions for a user."""
        user_id_str = str(user_id)
        session_ids = self._user_sessions.get(user_id_str, [])
        
        sessions = []
        for session_id in session_ids:
            session = self._sessions.get(session_id)
            if session is not None:
                sessions.append(session)
        
        return sessions
    
    def find_by_access_token(self, token: str) -> Optional[Session]:
        """Find session by access token."""
        session_id_str = self._token_index.get(token)
        if session_id_str is None:
            return None
        return self._sessions.get(session_id_str)
    
    def delete_expired(self) -> int:
        """Delete all expired sessions."""
        current_time = datetime.utcnow()
        expired_session_ids = []
        
        for session_id_str, session in self._sessions.items():
            if session.is_expired(current_time):
                expired_session_ids.append(session_id_str)
        
        # Delete expired sessions
        for session_id_str in expired_session_ids:
            session = self._sessions[session_id_str]
            self._delete_session(session_id_str, session)
        
        return len(expired_session_ids)
    
    def revoke_all_for_user(self, user_id: UserId) -> None:
        """Revoke all sessions for a user."""
        sessions = self.find_by_user_id(user_id)
        for session in sessions:
            if not session.is_revoked:
                session.revoke()
                self.save(session)
    
    def _delete_session(self, session_id_str: str, session: Session) -> None:
        """Delete a session and update indexes."""
        user_id_str = str(session.user_id)
        
        # Remove from user sessions index
        if user_id_str in self._user_sessions:
            self._user_sessions[user_id_str] = [
                sid for sid in self._user_sessions[user_id_str]
                if sid != session_id_str
            ]
            if not self._user_sessions[user_id_str]:
                del self._user_sessions[user_id_str]
        
        # Remove from token index
        self._token_index.pop(session.access_token.value, None)
        
        # Remove session
        del self._sessions[session_id_str]
    
    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._sessions.clear()
        self._user_sessions.clear()
        self._token_index.clear()
