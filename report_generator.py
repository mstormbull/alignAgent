"""
Report Generator module for Company Alignment Facilitator

This module handles AI-powered analysis and report generation using LangChain
summarization chains.
"""

import logging
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config import Config
from models import InterviewSession, AlignmentReport
from data_manager import DataManager

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Handles AI-powered report generation from interview data"""
    
    def __init__(self, data_manager: DataManager):
        """Initialize the report generator"""
        self.data_manager = data_manager
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
    
    def generate_alignment_report(self, topic: Optional[str] = None) -> AlignmentReport:
        """
        Generate a comprehensive alignment report from all interview transcripts
        
        Args:
            topic: Optional topic filter for the report
            
        Returns:
            Generated alignment report
        """
        try:
            # Load all interview sessions
            sessions = self.data_manager.load_all_interview_sessions()
            
            if not sessions:
                raise ValueError("No interview transcripts found. Please conduct some interviews first.")
            
            # Filter by topic if specified
            if topic:
                sessions = [s for s in sessions if topic.lower() in s.topic.lower()]
                if not sessions:
                    raise ValueError(f"No interviews found for topic: {topic}")
            
            # Convert sessions to documents for processing
            documents = self._sessions_to_documents(sessions)
            
            if not documents:
                raise ValueError("No valid conversation data found")
            
            # Split documents for processing
            split_docs = self.text_splitter.split_documents(documents)
            
            # Create summarization chain
            summary_chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                verbose=False
            )
            
            # Generate the summary
            summary = summary_chain.run(split_docs)
            
            # Create the report
            report = AlignmentReport(
                summary=summary,
                total_interviews=len(sessions),
                topic=topic or "Various topics"
            )
            
            logger.info(f"Generated alignment report for {len(sessions)} interviews")
            return report
            
        except Exception as e:
            logger.error(f"Error generating alignment report: {e}")
            raise
    
    def _sessions_to_documents(self, sessions: List[InterviewSession]) -> List[Document]:
        """
        Convert interview sessions to LangChain documents
        
        Args:
            sessions: List of interview sessions
            
        Returns:
            List of LangChain documents
        """
        documents = []
        
        for session in sessions:
            try:
                # Convert session to text
                conversation_text = self.data_manager.get_conversation_text(session)
                
                # Create document with metadata
                document = Document(
                    page_content=conversation_text,
                    metadata={
                        "topic": session.topic,
                        "turns": session.turns,
                        "created_at": session.created_at.isoformat()
                    }
                )
                
                documents.append(document)
                
            except Exception as e:
                logger.warning(f"Skipping session due to error: {e}")
                continue
        
        return documents
    
    def generate_topic_specific_report(self, topic: str) -> AlignmentReport:
        """
        Generate a report focused on a specific topic
        
        Args:
            topic: The specific topic to analyze
            
        Returns:
            Topic-specific alignment report
        """
        return self.generate_alignment_report(topic=topic)
    
    def generate_comparative_report(self, topics: List[str]) -> AlignmentReport:
        """
        Generate a comparative report between different topics
        
        Args:
            topics: List of topics to compare
            
        Returns:
            Comparative alignment report
        """
        try:
            # Load all sessions
            all_sessions = self.data_manager.load_all_interview_sessions()
            
            if not all_sessions:
                raise ValueError("No interview data available for comparison")
            
            # Group sessions by topic
            topic_sessions = {}
            for session in all_sessions:
                for topic in topics:
                    if topic.lower() in session.topic.lower():
                        if topic not in topic_sessions:
                            topic_sessions[topic] = []
                        topic_sessions[topic].append(session)
            
            if not topic_sessions:
                raise ValueError(f"No interviews found for the specified topics: {topics}")
            
            # Generate comparative analysis
            comparative_summary = self._generate_comparative_summary(topic_sessions)
            
            # Create report
            total_interviews = sum(len(sessions) for sessions in topic_sessions.values())
            report = AlignmentReport(
                summary=comparative_summary,
                total_interviews=total_interviews,
                topic=f"Comparative analysis: {', '.join(topics)}"
            )
            
            logger.info(f"Generated comparative report for {len(topics)} topics")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comparative report: {e}")
            raise
    
    def _generate_comparative_summary(self, topic_sessions: dict) -> str:
        """
        Generate a comparative summary between different topics
        
        Args:
            topic_sessions: Dictionary mapping topics to their sessions
            
        Returns:
            Comparative summary text
        """
        try:
            # Create documents for each topic
            topic_documents = {}
            for topic, sessions in topic_sessions.items():
                documents = self._sessions_to_documents(sessions)
                if documents:
                    topic_documents[topic] = documents
            
            # Generate individual summaries for each topic
            topic_summaries = {}
            for topic, documents in topic_documents.items():
                split_docs = self.text_splitter.split_documents(documents)
                summary_chain = load_summarize_chain(
                    llm=self.llm,
                    chain_type="map_reduce",
                    verbose=False
                )
                topic_summaries[topic] = summary_chain.run(split_docs)
            
            # Generate comparative analysis
            comparative_prompt = f"""
            Analyze the following topic summaries and provide a comparative analysis:
            
            {chr(10).join(f"Topic '{topic}': {summary}" for topic, summary in topic_summaries.items())}
            
            Please provide a comprehensive comparative analysis that identifies:
            1. Common themes across topics
            2. Key differences between topics
            3. Areas of alignment and misalignment
            4. Strategic implications and recommendations
            """
            
            comparative_summary = self.llm.predict(comparative_prompt)
            return comparative_summary
            
        except Exception as e:
            logger.error(f"Error generating comparative summary: {e}")
            raise
    
    def get_report_statistics(self) -> dict:
        """
        Get statistics for report generation
        
        Returns:
            Dictionary with report statistics
        """
        try:
            stats = self.data_manager.get_statistics()
            
            # Add report-specific statistics
            sessions = self.data_manager.load_all_interview_sessions()
            if sessions:
                topics = list(set(s.topic for s in sessions))
                stats["unique_topics"] = len(topics)
                stats["topics"] = topics
            else:
                stats["unique_topics"] = 0
                stats["topics"] = []
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting report statistics: {e}")
            return {
                "total_interviews": 0,
                "unique_topics": 0,
                "topics": []
            } 