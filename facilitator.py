"""
Main Facilitator module for Company Alignment Facilitator

This module orchestrates all components and provides the high-level interface
for the alignment facilitation system.
"""

import logging
from typing import Optional, Tuple

from config import Config
from models import InterviewSession, AlignmentReport
from ai_interviewer import AIInterviewer
from data_manager import DataManager
from report_generator import ReportGenerator

logger = logging.getLogger(__name__)

class CompanyAlignmentFacilitator:
    """Main orchestrator for the Company Alignment Facilitator system"""
    
    def __init__(self):
        """Initialize the facilitator with all components"""
        # Validate configuration
        Config.validate()
        Config.create_directories()
        
        # Initialize components
        self.data_manager = DataManager()
        self.ai_interviewer = AIInterviewer()
        self.report_generator = ReportGenerator(self.data_manager)
        
        logger.info("Company Alignment Facilitator initialized successfully")
    
    def start_new_session(self, topic: str) -> str:
        """
        Start a new alignment session with the given topic
        
        Args:
            topic: The alignment topic for the session
            
        Returns:
            Success message
        """
        try:
            if not topic.strip():
                return "Please enter a valid alignment topic."
            
            # Start the AI interview session
            session = self.ai_interviewer.start_session(topic.strip())
            
            logger.info(f"Started new alignment session: {topic}")
            return f"Alignment session started! Topic: '{topic}'. The interview interface is now active."
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return f"Error starting session: {str(e)}"
    
    def conduct_interview(self, message: str) -> Tuple[str, bool, Optional[str]]:
        """
        Conduct an interview with the given message
        
        Args:
            message: The user's message
            
        Returns:
            Tuple of (ai_response, is_complete, error_message)
        """
        try:
            # Conduct the interview
            ai_response, is_complete, error = self.ai_interviewer.conduct_interview(message)
            
            # If interview is complete, save the session
            if is_complete:
                self._save_current_session()
            
            return ai_response, is_complete, error
            
        except Exception as e:
            logger.error(f"Error conducting interview: {e}")
            return "", False, f"An error occurred: {str(e)}"
    
    def end_session(self) -> str:
        """
        End the current alignment session
        
        Returns:
            Success message
        """
        try:
            # End the AI interview session
            session = self.ai_interviewer.end_session()
            
            # Save the session if it exists
            if session:
                self._save_current_session()
            
            logger.info("Alignment session ended")
            return "Alignment session ended. All data has been saved."
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return f"Error ending session: {str(e)}"
    
    def generate_alignment_report(self, topic: Optional[str] = None) -> str:
        """
        Generate an alignment report
        
        Args:
            topic: Optional topic filter for the report
            
        Returns:
            Generated report as markdown text
        """
        try:
            # Generate the report
            report = self.report_generator.generate_alignment_report(topic)
            
            # Convert to markdown
            markdown_report = report.to_markdown()
            
            logger.info(f"Generated alignment report for topic: {topic or 'all topics'}")
            return markdown_report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Error generating alignment report: {str(e)}"
    
    def generate_topic_specific_report(self, topic: str) -> str:
        """
        Generate a report focused on a specific topic
        
        Args:
            topic: The specific topic to analyze
            
        Returns:
            Generated report as markdown text
        """
        try:
            report = self.report_generator.generate_topic_specific_report(topic)
            markdown_report = report.to_markdown()
            
            logger.info(f"Generated topic-specific report for: {topic}")
            return markdown_report
            
        except Exception as e:
            logger.error(f"Error generating topic-specific report: {e}")
            return f"Error generating topic-specific report: {str(e)}"
    
    def generate_comparative_report(self, topics: list) -> str:
        """
        Generate a comparative report between different topics
        
        Args:
            topics: List of topics to compare
            
        Returns:
            Generated comparative report as markdown text
        """
        try:
            report = self.report_generator.generate_comparative_report(topics)
            markdown_report = report.to_markdown()
            
            logger.info(f"Generated comparative report for topics: {topics}")
            return markdown_report
            
        except Exception as e:
            logger.error(f"Error generating comparative report: {e}")
            return f"Error generating comparative report: {str(e)}"
    
    def get_current_session(self) -> Optional[InterviewSession]:
        """
        Get the current interview session
        
        Returns:
            Current session or None if no active session
        """
        return self.ai_interviewer.get_current_session()
    
    def is_session_active(self) -> bool:
        """
        Check if there's an active interview session
        
        Returns:
            True if session is active, False otherwise
        """
        return self.ai_interviewer.is_session_active()
    
    def get_statistics(self) -> dict:
        """
        Get system statistics
        
        Returns:
            Dictionary with system statistics
        """
        try:
            stats = self.data_manager.get_statistics()
            report_stats = self.report_generator.get_report_statistics()
            
            # Combine statistics
            combined_stats = {**stats, **report_stats}
            
            # Add session status
            combined_stats["session_active"] = self.is_session_active()
            if self.is_session_active():
                session = self.get_current_session()
                combined_stats["current_topic"] = session.topic if session else None
                combined_stats["current_turns"] = session.turns if session else 0
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "total_interviews": 0,
                "session_active": False,
                "error": str(e)
            }
    
    def _save_current_session(self) -> Optional[str]:
        """
        Save the current interview session
        
        Returns:
            Path to saved file or None if no session to save
        """
        try:
            session = self.ai_interviewer.get_current_session()
            if session and session.conversation:
                filepath = self.data_manager.save_interview_session(session)
                logger.info(f"Saved current session to {filepath}")
                return filepath
            return None
            
        except Exception as e:
            logger.error(f"Error saving current session: {e}")
            return None
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # End any active session
            if self.is_session_active():
                self.end_session()
            
            logger.info("Facilitator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 