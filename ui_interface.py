"""
UI Interface module for Company Alignment Facilitator

This module handles all Gradio-related functionality and user interface components.
"""

import gradio as gr
from typing import List, Tuple, Optional

from facilitator import CompanyAlignmentFacilitator
from config import Config

class UIManager:
    """Manages the Gradio user interface"""
    
    def __init__(self, facilitator: CompanyAlignmentFacilitator):
        """Initialize the UI manager"""
        self.facilitator = facilitator
        self.demo = None
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        with gr.Blocks(title="Company Alignment Facilitator", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🎯 Company Alignment Facilitator")
            
            # Show demo mode warning if applicable
            if self.facilitator.is_demo_mode:
                gr.Markdown("""
                ## 🔑 Demo Mode Active
                
                **You're running in demo mode** - Set your `OPENAI_API_KEY` environment variable and restart to enable full AI features.
                
                You can still explore the interface and see example reports!
                """)
            else:
                gr.Markdown("An AI-powered tool for conducting alignment interviews and generating comprehensive reports.")
            
            with gr.Tabs():
                # Tab 1: Admin & Reporting
                with gr.Tab("Admin & Reporting"):
                    self._create_admin_tab()
                
                # Tab 2: Employee Interview
                with gr.Tab("Employee Interview"):
                    self._create_interview_tab()
                
                # Tab 3: Statistics & Analytics
                with gr.Tab("Statistics & Analytics"):
                    self._create_statistics_tab()
            
            self.demo = demo
            return demo
    
    def _create_admin_tab(self):
        """Create the admin and reporting tab"""
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
            generate_topic_report_btn = gr.Button("📋 Generate Topic-Specific Report", variant="secondary")
        
        with gr.Row():
            topic_filter_input = gr.Textbox(
                label="Topic Filter (for topic-specific reports)",
                placeholder="Enter specific topic to filter reports",
                lines=1
            )
        
        gr.Markdown("## Comparative Analysis")
        
        with gr.Row():
            topics_input = gr.Textbox(
                label="Topics to Compare (comma-separated)",
                placeholder="e.g., Remote work, Team collaboration, Communication",
                lines=1
            )
            generate_comparative_btn = gr.Button("📈 Generate Comparative Report", variant="secondary")
        
        report_output = gr.Textbox(
            label="Alignment Report",
            lines=20,
            max_lines=30
        )
        
        # Event handlers
        start_btn.click(
            fn=self._start_session,
            inputs=[topic_input],
            outputs=[report_output]
        )
        
        end_btn.click(
            fn=self._end_session,
            outputs=[report_output]
        )
        
        generate_report_btn.click(
            fn=self._generate_report,
            outputs=[report_output]
        )
        
        generate_topic_report_btn.click(
            fn=self._generate_topic_report,
            inputs=[topic_filter_input],
            outputs=[report_output]
        )
        
        generate_comparative_btn.click(
            fn=self._generate_comparative_report,
            inputs=[topics_input],
            outputs=[report_output]
        )
    
    def _create_interview_tab(self):
        """Create the employee interview tab"""
        gr.Markdown("## AI Interview Interface")
        gr.Markdown("This interface will be enabled once an admin starts an alignment session.")
        
        # Chat interface
        chat_interface = gr.ChatInterface(
            fn=self._interview_chat,
            title="Alignment Interview",
            description="The AI interviewer will ask you questions about the alignment topic. Please provide thoughtful, detailed responses.",
            examples=[
                ["I think our main priority should be improving customer satisfaction."],
                ["We need better communication between departments."],
                ["I'm concerned about our current project timeline."]
            ]
        )
    
    def _create_statistics_tab(self):
        """Create the statistics and analytics tab"""
        gr.Markdown("## System Statistics")
        
        with gr.Row():
            refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="primary")
        
        stats_output = gr.JSON(
            label="System Statistics"
        )
        
        gr.Markdown("## Session Status")
        
        status_output = gr.Textbox(
            label="Current Session Status",
            lines=3
        )
        
        # Event handlers
        refresh_stats_btn.click(
            fn=self._get_statistics,
            outputs=[stats_output, status_output]
        )
        
        # Initial load
        refresh_stats_btn.click(
            fn=self._get_statistics,
            outputs=[stats_output, status_output]
        )
    
    def _start_session(self, topic: str) -> str:
        """Start a new alignment session"""
        return self.facilitator.start_new_session(topic)
    
    def _end_session(self) -> str:
        """End the current alignment session"""
        return self.facilitator.end_session()
    
    def _generate_report(self) -> str:
        """Generate a general alignment report"""
        return self.facilitator.generate_alignment_report()
    
    def _generate_topic_report(self, topic: str) -> str:
        """Generate a topic-specific report"""
        if not topic.strip():
            return "Please enter a topic to filter the report."
        return self.facilitator.generate_topic_specific_report(topic.strip())
    
    def _generate_comparative_report(self, topics: str) -> str:
        """Generate a comparative report"""
        if not topics.strip():
            return "Please enter topics to compare (comma-separated)."
        
        topic_list = [t.strip() for t in topics.split(",") if t.strip()]
        if len(topic_list) < 2:
            return "Please enter at least 2 topics to compare."
        
        return self.facilitator.generate_comparative_report(topic_list)
    
    def _interview_chat(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]], str]:
        """Handle interview chat interface"""
        if not self.facilitator.is_session_active():
            return "", history, "Please start an alignment session first."
        
        ai_response, is_complete, error = self.facilitator.conduct_interview(message)
        
        if error:
            return "", history, error
        
        if is_complete:
            return "", history, "Interview complete! Thank you for your participation."
        
        return ai_response, history, ""
    
    def _get_statistics(self) -> Tuple[dict, str]:
        """Get system statistics and status"""
        stats = self.facilitator.get_statistics()
        
        # Create status message
        if stats.get("session_active"):
            session = self.facilitator.get_current_session()
            status_msg = f"✅ Session Active\nTopic: {stats.get('current_topic', 'Unknown')}\nTurns: {stats.get('current_turns', 0)}/{Config.MAX_INTERVIEW_TURNS}"
        else:
            status_msg = "⏸️ No Active Session\nStart a new alignment session to begin interviews."
        
        return stats, status_msg
    
    def launch(self, share: bool = False, debug: bool = True) -> None:
        """Launch the Gradio interface"""
        if self.demo:
            self.demo.launch(share=share, debug=debug)
        else:
            raise RuntimeError("Interface not created. Call create_interface() first.") 