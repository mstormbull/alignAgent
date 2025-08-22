"""
AI Interviewer module for Company Alignment Facilitator

This module handles the conversational AI logic, interview management,
and interaction with the language model.
"""

import logging
from typing import Tuple, List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from config import Config
from models import InterviewSession, ConversationRole

logger = logging.getLogger(__name__)

class AIInterviewer:
    """Handles AI-powered interview conversations"""
    
    def __init__(self):
        """Initialize the AI interviewer with LangChain components"""
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        self.conversation_chain = self._create_conversation_chain()
        self.current_session: Optional[InterviewSession] = None
    
    def _create_conversation_chain(self) -> ConversationChain:
        """Create and configure the LangChain ConversationChain for the interviewer"""
        
        # Custom prompt template for the interviewer
        interviewer_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""You are a professional, neutral, and curious researcher conducting an alignment interview. 

Guidelines:
- Be professional, warm, and genuinely curious
- Ask open-ended questions that encourage deeper thinking
- Don't be leading or judgmental
- If the employee gives a brief answer, gently probe for more details
- Focus on understanding their perspective, concerns, and ideas
- Keep responses concise but engaging

Current conversation:
{history}
Human: {input}
Assistant:"""
        )
        
        # Create memory for conversation context
        memory = ConversationBufferMemory(human_prefix="Human", ai_prefix="Assistant")
        
        # Create the conversation chain
        chain = ConversationChain(
            llm=self.llm,
            memory=memory,
            prompt=interviewer_prompt,
            verbose=False
        )
        
        return chain
    
    def start_session(self, topic: str) -> InterviewSession:
        """Start a new interview session with the given topic"""
        if not topic.strip():
            raise ValueError("Topic cannot be empty")
        
        # Create new session
        self.current_session = InterviewSession(
            topic=topic.strip(),
            max_turns=Config.MAX_INTERVIEW_TURNS,
            is_active=True
        )
        
        # Generate initial question
        initial_question = self._generate_initial_question(topic)
        self.current_session.add_turn(ConversationRole.ASSISTANT, initial_question)
        
        logger.info(f"Started new interview session with topic: {topic}")
        return self.current_session
    
    def _generate_initial_question(self, topic: str) -> str:
        """Generate the initial question for the interview"""
        return f"""Thank you for participating in our alignment session. We're focusing on: '{topic}'. 

To get started, could you share your initial thoughts on this topic? What does it mean to you, and what aspects are most important from your perspective?"""
    
    def conduct_interview(self, user_message: str) -> Tuple[str, bool, Optional[str]]:
        """
        Conduct the interview with the given user message
        
        Returns:
            Tuple of (ai_response, is_complete, error_message)
        """
        if not self.current_session or not self.current_session.is_active:
            return "", False, "No active interview session"
        
        if self.current_session.is_complete():
            return "", True, "Interview is already complete"
        
        try:
            # Add user message to session
            self.current_session.add_turn(ConversationRole.USER, user_message)
            
            # Generate AI response
            ai_response = self.conversation_chain.predict(
                input=user_message
            )
            
            # Add AI response to session
            self.current_session.add_turn(ConversationRole.ASSISTANT, ai_response)
            
            # Check if interview is complete
            is_complete = self.current_session.is_complete()
            
            if is_complete:
                logger.info("Interview completed")
            
            return ai_response, is_complete, None
            
        except Exception as e:
            logger.error(f"Error during interview: {e}")
            return "", False, f"An error occurred: {str(e)}"
    
    def end_session(self) -> Optional[InterviewSession]:
        """End the current interview session"""
        if not self.current_session:
            return None
        
        self.current_session.is_active = False
        session = self.current_session
        self.current_session = None
        
        # Clear conversation memory
        self.conversation_chain.memory.clear()
        
        logger.info(f"Ended interview session for topic: {session.topic}")
        return session
    
    def get_current_session(self) -> Optional[InterviewSession]:
        """Get the current interview session"""
        return self.current_session
    
    def is_session_active(self) -> bool:
        """Check if there's an active interview session"""
        return self.current_session is not None and self.current_session.is_active 