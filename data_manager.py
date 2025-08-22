"""
Data Manager module for Company Alignment Facilitator

This module handles file operations, conversation storage, and data persistence.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from config import Config
from models import InterviewSession, AlignmentReport

logger = logging.getLogger(__name__)

class DataManager:
    """Handles data persistence and file operations"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.conversations_dir = Path(Config.CONVERSATIONS_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure necessary directories exist"""
        self.conversations_dir.mkdir(exist_ok=True)
        logger.info(f"Ensured directory exists: {self.conversations_dir}")
    
    def save_interview_session(self, session: InterviewSession) -> str:
        """
        Save an interview session to a JSON file
        
        Args:
            session: The interview session to save
            
        Returns:
            Path to the saved file
        """
        if not session.conversation:
            raise ValueError("Cannot save empty interview session")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"interview_{timestamp}.json"
        filepath = self.conversations_dir / filename
        
        try:
            # Convert session to dictionary
            session_data = session.to_dict()
            
            # Add metadata
            session_data["saved_at"] = datetime.now().isoformat()
            session_data["file_version"] = "1.0"
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved interview session to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving interview session: {e}")
            raise
    
    def load_interview_session(self, filepath: str) -> InterviewSession:
        """
        Load an interview session from a JSON file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Loaded interview session
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session = InterviewSession.from_dict(session_data)
            logger.info(f"Loaded interview session from {filepath}")
            return session
            
        except Exception as e:
            logger.error(f"Error loading interview session from {filepath}: {e}")
            raise
    
    def get_all_interview_files(self) -> List[str]:
        """
        Get all interview JSON files in the conversations directory
        
        Returns:
            List of file paths
        """
        try:
            json_files = list(self.conversations_dir.glob("*.json"))
            return [str(f) for f in json_files]
        except Exception as e:
            logger.error(f"Error getting interview files: {e}")
            return []
    
    def load_all_interview_sessions(self) -> List[InterviewSession]:
        """
        Load all interview sessions from the conversations directory
        
        Returns:
            List of interview sessions
        """
        sessions = []
        file_paths = self.get_all_interview_files()
        
        for filepath in file_paths:
            try:
                session = self.load_interview_session(filepath)
                sessions.append(session)
            except Exception as e:
                logger.warning(f"Skipping corrupted file {filepath}: {e}")
                continue
        
        logger.info(f"Loaded {len(sessions)} interview sessions")
        return sessions
    
    def delete_interview_file(self, filepath: str) -> bool:
        """
        Delete an interview file
        
        Args:
            filepath: Path to the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(filepath)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"Deleted interview file: {filepath}")
                return True
            else:
                logger.warning(f"File not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
            return False
    
    def get_conversation_text(self, session: InterviewSession) -> str:
        """
        Convert an interview session to text format for processing
        
        Args:
            session: The interview session
            
        Returns:
            Formatted conversation text
        """
        lines = [f"Topic: {session.topic}\n"]
        
        for turn in session.conversation:
            role = turn.role.value.title()
            content = turn.content
            lines.append(f"{role}: {content}\n")
        
        return "\n".join(lines)
    
    def get_statistics(self) -> dict:
        """
        Get statistics about stored interview data
        
        Returns:
            Dictionary with statistics
        """
        try:
            sessions = self.load_all_interview_sessions()
            
            if not sessions:
                return {
                    "total_interviews": 0,
                    "total_conversations": 0,
                    "average_turns": 0,
                    "topics": []
                }
            
            total_conversations = sum(len(s.conversation) for s in sessions)
            average_turns = sum(s.turns for s in sessions) / len(sessions)
            topics = list(set(s.topic for s in sessions))
            
            return {
                "total_interviews": len(sessions),
                "total_conversations": total_conversations,
                "average_turns": round(average_turns, 2),
                "topics": topics
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_interviews": 0,
                "total_conversations": 0,
                "average_turns": 0,
                "topics": []
            } 