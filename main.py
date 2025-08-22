import os
import json
import datetime
import gradio as gr
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyAlignmentFacilitator:
    def __init__(self):
        """Initialize the Company Alignment Facilitator"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=self.openai_api_key
        )
        
        # Session state
        self.current_topic = None
        self.session_active = False
        self.current_conversation = None
        self.conversation_turns = 0
        self.max_turns = 5
        
        # Create conversations directory if it doesn't exist
        os.makedirs("conversations", exist_ok=True)
        
        # Initialize the interviewer chain
        self.interviewer_chain = self._create_interviewer_chain()
    
    def _create_interviewer_chain(self) -> ConversationChain:
        """Create and configure the LangChain ConversationChain for the interviewer"""
        
        # Custom prompt template for the interviewer
        interviewer_prompt = PromptTemplate(
            input_variables=["history", "input", "topic"],
            template="""You are a professional, neutral, and curious researcher conducting an alignment interview. 
Your goal is to understand the employee's perspective on the topic: {topic}

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
    
    def start_new_session(self, topic: str) -> str:
        """Start a new alignment session with the given topic"""
        if not topic.strip():
            return "Please enter a valid alignment topic."
        
        self.current_topic = topic.strip()
        self.session_active = True
        self.current_conversation = []
        self.conversation_turns = 0
        
        # Initialize the conversation with the topic
        initial_question = f"Thank you for participating in our alignment session. We're focusing on: '{self.current_topic}'. To get started, could you share your initial thoughts on this topic? What does it mean to you, and what aspects are most important from your perspective?"
        
        self.current_conversation.append({
            "role": "assistant",
            "content": initial_question,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        logger.info(f"Started new alignment session with topic: {self.current_topic}")
        return f"Alignment session started! Topic: '{self.current_topic}'. The interview interface is now active."
    
    def conduct_interview(self, message: str, history: List[List[str]]) -> tuple:
        """Conduct the AI interview with the employee"""
        if not self.session_active:
            return "", history, "Please start an alignment session first."
        
        if self.conversation_turns >= self.max_turns:
            return "", history, "Interview complete! Thank you for your participation."
        
        # Add user message to conversation
        self.current_conversation.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        try:
            # Generate AI response using the interviewer chain
            response = self.interviewer_chain.predict(
                input=message,
                topic=self.current_topic
            )
            
            # Add AI response to conversation
            self.current_conversation.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            self.conversation_turns += 1
            
            # Check if interview is complete
            if self.conversation_turns >= self.max_turns:
                # Save the conversation
                self._save_conversation()
                return "", history, "Interview complete! Your responses have been saved. Thank you for your participation."
            
            return response, history, ""
            
        except Exception as e:
            logger.error(f"Error during interview: {e}")
            return "", history, f"An error occurred: {str(e)}"
    
    def _save_conversation(self) -> str:
        """Save the current conversation transcript to a JSON file"""
        if not self.current_conversation:
            return "No conversation to save."
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"conversations/interview_{timestamp}.json"
        
        # Prepare conversation data
        conversation_data = {
            "topic": self.current_topic,
            "timestamp": datetime.datetime.now().isoformat(),
            "turns": self.conversation_turns,
            "conversation": self.current_conversation
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Conversation saved to {filename}")
            return f"Conversation saved to {filename}"
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return f"Error saving conversation: {str(e)}"
    
    def generate_alignment_report(self) -> str:
        """Generate a comprehensive alignment report from all interview transcripts"""
        try:
            # Load all conversation files
            conversation_files = []
            for filename in os.listdir("conversations"):
                if filename.endswith(".json"):
                    conversation_files.append(os.path.join("conversations", filename))
            
            if not conversation_files:
                return "No interview transcripts found. Please conduct some interviews first."
            
            # Load and process all conversations
            documents = []
            for file_path in conversation_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Create a document from the conversation
                conversation_text = f"Topic: {data['topic']}\n\n"
                for turn in data['conversation']:
                    role = turn['role'].title()
                    content = turn['content']
                    conversation_text += f"{role}: {content}\n\n"
                
                documents.append(Document(
                    page_content=conversation_text,
                    metadata={"source": file_path, "topic": data['topic']}
                ))
            
            # Split documents for processing
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200
            )
            
            split_docs = text_splitter.split_documents(documents)
            
            # Create summarization chain
            summary_chain = load_summarize_chain(
                llm=self.llm,
                chain_type="map_reduce",
                verbose=False
            )
            
            # Generate the summary
            result = summary_chain.run(split_docs)
            
            # Format the final report
            report = f"""# Company Alignment Report

## Executive Summary
{result}

## Analysis Details
- **Total Interviews Analyzed**: {len(conversation_files)}
- **Alignment Topic**: {self.current_topic if self.current_topic else 'Various topics'}
- **Report Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Insights
This report synthesizes the perspectives shared during the alignment interviews. The analysis reveals patterns, consensus areas, and potential misalignments that should be addressed to improve organizational alignment.

## Recommendations
Based on the interview analysis, consider the following actions:
1. Address any identified misalignments through targeted communication
2. Build on areas of consensus to strengthen team cohesion
3. Schedule follow-up discussions on specific themes that emerged
4. Consider additional interviews if new questions arise from this analysis

---
*Report generated by Company Alignment Facilitator*
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Error generating alignment report: {str(e)}"
    
    def end_session(self) -> str:
        """End the current alignment session"""
        if self.current_conversation and self.session_active:
            self._save_conversation()
        
        self.session_active = False
        self.current_topic = None
        self.current_conversation = None
        self.conversation_turns = 0
        
        return "Alignment session ended. All data has been saved."

# Initialize the facilitator
try:
    facilitator = CompanyAlignmentFacilitator()
except ValueError as e:
    print(f"Initialization error: {e}")
    facilitator = None

def start_session(topic):
    """Gradio function to start a new alignment session"""
    if facilitator:
        return facilitator.start_new_session(topic)
    return "Error: Facilitator not initialized. Please check your OPENAI_API_KEY."

def end_session():
    """Gradio function to end the current session"""
    if facilitator:
        return facilitator.end_session()
    return "Error: Facilitator not initialized."

def generate_report():
    """Gradio function to generate the alignment report"""
    if facilitator:
        return facilitator.generate_alignment_report()
    return "Error: Facilitator not initialized."

def interview_chat(message, history):
    """Gradio function for the interview chat interface"""
    if not facilitator:
        return "", history, "Error: Facilitator not initialized."
    
    if not facilitator.session_active:
        return "", history, "Please start an alignment session first."
    
    response, _, error_msg = facilitator.conduct_interview(message, history)
    return response, history, error_msg

def is_session_active():
    """Check if a session is currently active"""
    if facilitator:
        return facilitator.session_active
    return False

# Create the Gradio interface
with gr.Blocks(title="Company Alignment Facilitator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎯 Company Alignment Facilitator")
    gr.Markdown("An AI-powered tool for conducting alignment interviews and generating comprehensive reports.")
    
    with gr.Tabs():
        # Tab 1: Admin & Reporting
        with gr.Tab("Admin & Reporting"):
            gr.Markdown("## Session Management")
            
            with gr.Row():
                topic_input = gr.Textbox(
                    label="Alignment Topic",
                    placeholder="e.g., Our Q4 strategic priorities, Team communication processes, etc.",
                    lines=2
                )
            
            with gr.Row():
                start_btn = gr.Button("🚀 Start New Alignment Session", variant="primary")
                end_btn = gr.Button("⏹️ End Current Session", variant="stop")
            
            gr.Markdown("## Report Generation")
            
            with gr.Row():
                generate_report_btn = gr.Button("📊 Generate Alignment Report", variant="primary")
            
            report_output = gr.Textbox(
                label="Alignment Report",
                lines=20,
                max_lines=30,
                interactive=False
            )
            
            # Event handlers
            start_btn.click(
                fn=start_session,
                inputs=[topic_input],
                outputs=[report_output]
            )
            
            end_btn.click(
                fn=end_session,
                outputs=[report_output]
            )
            
            generate_report_btn.click(
                fn=generate_report,
                outputs=[report_output]
            )
        
        # Tab 2: Employee Interview
        with gr.Tab("Employee Interview"):
            gr.Markdown("## AI Interview Interface")
            gr.Markdown("This interface will be enabled once an admin starts an alignment session.")
            
            # Chat interface
            chat_interface = gr.ChatInterface(
                fn=interview_chat,
                title="Alignment Interview",
                description="The AI interviewer will ask you questions about the alignment topic. Please provide thoughtful, detailed responses.",
                examples=[
                    ["I think our main priority should be improving customer satisfaction."],
                    ["We need better communication between departments."],
                    ["I'm concerned about our current project timeline."]
                ],
                retry_btn=None,
                undo_btn=None,
                clear_btn="Clear Chat"
            )

# Launch the application
if __name__ == "__main__":
    if facilitator:
        print("🚀 Starting Company Alignment Facilitator...")
        print("📝 Make sure to set your OPENAI_API_KEY environment variable")
        demo.launch(share=False, debug=True)
    else:
        print("❌ Failed to initialize. Please check your OPENAI_API_KEY environment variable.") 