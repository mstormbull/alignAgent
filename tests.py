#!/usr/bin/env python3
"""
Test module for Company Alignment Facilitator

This module provides unit tests and integration tests for the key components
of the modular system.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from config import Config
from models import ConversationRole, ConversationTurn, InterviewSession, AlignmentReport
from data_manager import DataManager
from ai_interviewer import AIInterviewer
from report_generator import ReportGenerator
from facilitator import CompanyAlignmentFacilitator

class TestConfig(unittest.TestCase):
    """Test configuration module"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test with valid API key
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            self.assertTrue(Config.validate())
        
        # Test without API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                Config.validate()
    
    def test_create_directories(self):
        """Test directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = Config.CONVERSATIONS_DIR
            Config.CONVERSATIONS_DIR = os.path.join(temp_dir, "test_conversations")
            
            Config.create_directories()
            self.assertTrue(os.path.exists(Config.CONVERSATIONS_DIR))
            
            Config.CONVERSATIONS_DIR = original_dir

class TestModels(unittest.TestCase):
    """Test data models"""
    
    def test_conversation_turn(self):
        """Test ConversationTurn model"""
        turn = ConversationTurn(
            role=ConversationRole.USER,
            content="Test message"
        )
        
        self.assertEqual(turn.role, ConversationRole.USER)
        self.assertEqual(turn.content, "Test message")
        self.assertIsInstance(turn.timestamp, datetime)
        
        # Test serialization
        turn_dict = turn.to_dict()
        self.assertEqual(turn_dict["role"], "user")
        self.assertEqual(turn_dict["content"], "Test message")
        
        # Test deserialization
        turn_from_dict = ConversationTurn.from_dict(turn_dict)
        self.assertEqual(turn_from_dict.role, turn.role)
        self.assertEqual(turn_from_dict.content, turn.content)
    
    def test_interview_session(self):
        """Test InterviewSession model"""
        session = InterviewSession(
            topic="Test Topic",
            max_turns=3
        )
        
        self.assertEqual(session.topic, "Test Topic")
        self.assertEqual(session.max_turns, 3)
        self.assertEqual(session.turns, 0)
        self.assertFalse(session.is_active)
        
        # Test adding turns
        session.add_turn(ConversationRole.USER, "User message")
        session.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        self.assertEqual(len(session.conversation), 2)
        self.assertEqual(session.turns, 1)
        
        # Test completion
        self.assertFalse(session.is_complete())
        session.add_turn(ConversationRole.ASSISTANT, "Second AI response")
        session.add_turn(ConversationRole.ASSISTANT, "Third AI response")
        self.assertTrue(session.is_complete())
        
        # Test serialization
        session_dict = session.to_dict()
        self.assertEqual(session_dict["topic"], "Test Topic")
        self.assertEqual(session_dict["turns"], 3)
        
        # Test deserialization
        session_from_dict = InterviewSession.from_dict(session_dict)
        self.assertEqual(session_from_dict.topic, session.topic)
        self.assertEqual(session_from_dict.turns, session.turns)
    
    def test_alignment_report(self):
        """Test AlignmentReport model"""
        report = AlignmentReport(
            summary="Test summary",
            total_interviews=5,
            topic="Test Topic"
        )
        
        self.assertEqual(report.summary, "Test summary")
        self.assertEqual(report.total_interviews, 5)
        self.assertEqual(report.topic, "Test Topic")
        
        # Test markdown generation
        markdown = report.to_markdown()
        self.assertIn("Test summary", markdown)
        self.assertIn("Test Topic", markdown)
        self.assertIn("5", markdown)

class TestDataManager(unittest.TestCase):
    """Test data manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = Config.CONVERSATIONS_DIR
        Config.CONVERSATIONS_DIR = self.temp_dir
        self.data_manager = DataManager()
    
    def tearDown(self):
        """Clean up test environment"""
        Config.CONVERSATIONS_DIR = self.original_dir
    
    def test_save_and_load_session(self):
        """Test saving and loading interview sessions"""
        session = InterviewSession(
            topic="Test Topic",
            max_turns=3
        )
        session.add_turn(ConversationRole.USER, "User message")
        session.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        # Save session
        filepath = self.data_manager.save_interview_session(session)
        self.assertTrue(os.path.exists(filepath))
        
        # Load session
        loaded_session = self.data_manager.load_interview_session(filepath)
        self.assertEqual(loaded_session.topic, session.topic)
        self.assertEqual(len(loaded_session.conversation), 2)
    
    def test_get_conversation_text(self):
        """Test conversation text generation"""
        session = InterviewSession(topic="Test Topic")
        session.add_turn(ConversationRole.USER, "User message")
        session.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        text = self.data_manager.get_conversation_text(session)
        self.assertIn("Test Topic", text)
        self.assertIn("User: User message", text)
        self.assertIn("Assistant: AI response", text)
    
    def test_get_statistics(self):
        """Test statistics generation"""
        # Create test sessions
        session1 = InterviewSession(topic="Topic 1")
        session1.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        session2 = InterviewSession(topic="Topic 2")
        session2.add_turn(ConversationRole.ASSISTANT, "AI response")
        session2.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        # Save sessions
        self.data_manager.save_interview_session(session1)
        self.data_manager.save_interview_session(session2)
        
        # Get statistics
        stats = self.data_manager.get_statistics()
        self.assertEqual(stats["total_interviews"], 2)
        self.assertEqual(stats["average_turns"], 1.5)
        self.assertEqual(len(stats["topics"]), 2)

class TestAIInterviewer(unittest.TestCase):
    """Test AI interviewer"""
    
    @patch('ai_interviewer.ChatOpenAI')
    @patch('ai_interviewer.ConversationChain')
    def setUp(self, mock_chain, mock_llm):
        """Set up test environment"""
        # Mock the LLM and chain
        self.mock_llm = mock_llm.return_value
        self.mock_chain = mock_chain.return_value
        self.mock_chain.predict.return_value = "Mock AI response"
        
        # Set up config
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            self.interviewer = AIInterviewer()
    
    def test_start_session(self):
        """Test starting a new session"""
        session = self.interviewer.start_session("Test Topic")
        
        self.assertEqual(session.topic, "Test Topic")
        self.assertTrue(session.is_active)
        self.assertEqual(session.max_turns, Config.MAX_INTERVIEW_TURNS)
        self.assertEqual(len(session.conversation), 1)
    
    def test_conduct_interview(self):
        """Test conducting an interview"""
        # Start session
        self.interviewer.start_session("Test Topic")
        
        # Conduct interview
        response, is_complete, error = self.interviewer.conduct_interview("User message")
        
        self.assertEqual(response, "Mock AI response")
        self.assertFalse(is_complete)
        self.assertIsNone(error)
        self.assertEqual(self.interviewer.current_session.turns, 1)
    
    def test_session_completion(self):
        """Test interview completion"""
        # Start session
        self.interviewer.start_session("Test Topic")
        
        # Conduct interviews until completion
        for i in range(Config.MAX_INTERVIEW_TURNS):
            response, is_complete, error = self.interviewer.conduct_interview(f"Message {i}")
            
            if is_complete:
                break
        
        self.assertTrue(is_complete)
        self.assertEqual(self.interviewer.current_session.turns, Config.MAX_INTERVIEW_TURNS)

class TestReportGenerator(unittest.TestCase):
    """Test report generator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_dir = Config.CONVERSATIONS_DIR
        Config.CONVERSATIONS_DIR = self.temp_dir
        
        # Mock data manager
        self.mock_data_manager = Mock()
        self.report_generator = ReportGenerator(self.mock_data_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        Config.CONVERSATIONS_DIR = self.original_dir
    
    @patch('report_generator.ChatOpenAI')
    @patch('report_generator.load_summarize_chain')
    def test_generate_report(self, mock_summary_chain, mock_llm):
        """Test report generation"""
        # Mock the summary chain
        mock_chain = mock_summary_chain.return_value
        mock_chain.run.return_value = "Mock summary"
        
        # Mock sessions
        session = InterviewSession(topic="Test Topic")
        session.add_turn(ConversationRole.USER, "User message")
        session.add_turn(ConversationRole.ASSISTANT, "AI response")
        
        self.mock_data_manager.load_all_interview_sessions.return_value = [session]
        self.mock_data_manager.get_conversation_text.return_value = "Test conversation text"
        
        # Generate report
        report = self.report_generator.generate_alignment_report()
        
        self.assertEqual(report.summary, "Mock summary")
        self.assertEqual(report.total_interviews, 1)
        self.assertEqual(report.topic, "Various topics")

class TestFacilitator(unittest.TestCase):
    """Test main facilitator"""
    
    @patch('facilitator.DataManager')
    @patch('facilitator.AIInterviewer')
    @patch('facilitator.ReportGenerator')
    def setUp(self, mock_report_gen, mock_ai_interviewer, mock_data_manager):
        """Set up test environment"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            self.facilitator = CompanyAlignmentFacilitator()
    
    def test_start_session(self):
        """Test starting a session"""
        result = self.facilitator.start_new_session("Test Topic")
        self.assertIn("started", result.lower())
    
    def test_conduct_interview(self):
        """Test conducting an interview"""
        # Start session
        self.facilitator.start_new_session("Test Topic")
        
        # Mock AI interviewer response
        self.facilitator.ai_interviewer.conduct_interview.return_value = (
            "Mock response", False, None
        )
        
        response, is_complete, error = self.facilitator.conduct_interview("User message")
        
        self.assertEqual(response, "Mock response")
        self.assertFalse(is_complete)
        self.assertIsNone(error)

def run_tests():
    """Run all tests"""
    print("🧪 Running Company Alignment Facilitator Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestConfig,
        TestModels,
        TestDataManager,
        TestAIInterviewer,
        TestReportGenerator,
        TestFacilitator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests() 