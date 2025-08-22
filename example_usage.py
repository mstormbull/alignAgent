#!/usr/bin/env python3
"""
Example usage of the Company Alignment Facilitator

This script demonstrates how to use the CompanyAlignmentFacilitator class
programmatically without the Gradio interface.
"""

import os
import sys
from facilitator import CompanyAlignmentFacilitator
from config import Config

def example_interview_workflow():
    """Example workflow showing how to conduct interviews and generate reports"""
    
    # Initialize the facilitator
    try:
        facilitator = CompanyAlignmentFacilitator()
        print("✅ Company Alignment Facilitator initialized successfully")
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        print("Please set your OPENAI_API_KEY environment variable")
        return
    
    # Start a new alignment session
    topic = "Our Q4 strategic priorities and team collaboration"
    print(f"\n🚀 Starting alignment session with topic: '{topic}'")
    result = facilitator.start_new_session(topic)
    print(f"Result: {result}")
    
    # Example interview responses (in a real scenario, these would come from actual users)
    example_responses = [
        "I think our main priority should be improving customer satisfaction and reducing response times.",
        "We need better communication between the development and sales teams to align on customer needs.",
        "I'm concerned about our current project timeline and resource allocation.",
        "I believe we should focus more on innovation and less on maintaining legacy systems.",
        "Team collaboration has been improving, but we still have silos between departments."
    ]
    
    # Conduct the interview
    print(f"\n📝 Conducting interview with {len(example_responses)} responses...")
    
    for i, response in enumerate(example_responses, 1):
        print(f"\n--- Turn {i} ---")
        print(f"Employee: {response}")
        
        # Get AI response
        ai_response, is_complete, error = facilitator.conduct_interview(response)
        
        if error:
            print(f"Error: {error}")
            break
        
        print(f"AI Interviewer: {ai_response}")
        
        if is_complete:
            print("\n✅ Interview completed!")
            break
    
    # Generate a report (this would normally be done after multiple interviews)
    print(f"\n📊 Generating alignment report...")
    report = facilitator.generate_alignment_report()
    print(f"\nReport generated successfully!")
    print("=" * 50)
    print("SAMPLE REPORT:")
    print("=" * 50)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    # End the session
    print(f"\n⏹️ Ending session...")
    result = facilitator.end_session()
    print(f"Result: {result}")

def example_multiple_interviews():
    """Example showing how to conduct multiple interviews for a comprehensive report"""
    
    try:
        facilitator = CompanyAlignmentFacilitator()
        print("✅ Facilitator initialized for multiple interviews example")
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Start session
    topic = "Remote work policies and team productivity"
    facilitator.start_new_session(topic)
    print(f"Started session: {topic}")
    
    # Multiple interview scenarios
    interview_scenarios = [
        # Interview 1: Manager perspective
        [
            "As a manager, I find remote work has improved productivity but made team building harder.",
            "We need more structured virtual team activities and better tools for collaboration.",
            "I'm concerned about new employees not getting proper onboarding in remote settings.",
            "The flexibility has been great for work-life balance, but some team members struggle with boundaries.",
            "I think we should have a hybrid model going forward."
        ],
        # Interview 2: Individual contributor perspective
        [
            "Remote work has been amazing for my productivity - fewer distractions and more focus time.",
            "I miss the spontaneous conversations and quick problem-solving sessions we had in the office.",
            "Sometimes I feel isolated and disconnected from the broader team culture.",
            "The technology tools we use are good, but there's still room for improvement.",
            "I'd prefer to work remotely 3-4 days a week and come in for important meetings."
        ],
        # Interview 3: HR perspective
        [
            "From an HR standpoint, remote work has reduced our office costs significantly.",
            "We've had to adapt our hiring and onboarding processes for remote-first work.",
            "Employee satisfaction scores have improved, but engagement metrics are mixed.",
            "We need better policies around work hours and availability expectations.",
            "Mental health support has become more important with remote work isolation."
        ]
    ]
    
    # Conduct multiple interviews
    for i, responses in enumerate(interview_scenarios, 1):
        print(f"\n--- Conducting Interview {i} ---")
        
        for j, response in enumerate(responses, 1):
            print(f"Turn {j}: {response[:50]}...")
            ai_response, is_complete, error = facilitator.conduct_interview(response)
            
            if error:
                print(f"Error: {error}")
                break
            
            if is_complete:
                break
        
        print(f"Interview {i} completed!")
        
        # End current session and start new one for next interview
        if i < len(interview_scenarios):
            facilitator.end_session()
            facilitator.start_new_session(topic)
    
    # Generate comprehensive report
    print(f"\n📊 Generating comprehensive alignment report...")
    report = facilitator.generate_alignment_report()
    print(f"\nComprehensive report generated!")
    print("=" * 60)
    print("COMPREHENSIVE ALIGNMENT REPORT:")
    print("=" * 60)
    print(report)
    
    # End session
    facilitator.end_session()
    print(f"\n✅ All interviews completed and session ended!")

def example_topic_specific_reports():
    """Example showing how to generate topic-specific and comparative reports"""
    
    try:
        facilitator = CompanyAlignmentFacilitator()
        print("✅ Facilitator initialized for topic-specific reports example")
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Generate topic-specific report
    print(f"\n📋 Generating topic-specific report for 'Remote work'...")
    try:
        topic_report = facilitator.generate_topic_specific_report("Remote work")
        print("Topic-specific report generated successfully!")
        print("=" * 40)
        print("TOPIC-SPECIFIC REPORT:")
        print("=" * 40)
        print(topic_report[:800] + "..." if len(topic_report) > 800 else topic_report)
    except Exception as e:
        print(f"No data found for topic-specific report: {e}")
    
    # Generate comparative report
    print(f"\n📈 Generating comparative report...")
    try:
        comparative_report = facilitator.generate_comparative_report([
            "Remote work", 
            "Team collaboration", 
            "Communication"
        ])
        print("Comparative report generated successfully!")
        print("=" * 40)
        print("COMPARATIVE REPORT:")
        print("=" * 40)
        print(comparative_report[:800] + "..." if len(comparative_report) > 800 else comparative_report)
    except Exception as e:
        print(f"No data found for comparative report: {e}")

def example_statistics():
    """Example showing how to get system statistics"""
    
    try:
        facilitator = CompanyAlignmentFacilitator()
        print("✅ Facilitator initialized for statistics example")
    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Get system statistics
    print(f"\n📊 Getting system statistics...")
    stats = facilitator.get_statistics()
    
    print("System Statistics:")
    print("=" * 30)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Check session status
    if facilitator.is_session_active():
        session = facilitator.get_current_session()
        print(f"\nCurrent session:")
        print(f"Topic: {session.topic}")
        print(f"Turns: {session.turns}/{session.max_turns}")
        print(f"Active: {session.is_active}")
    else:
        print(f"\nNo active session")

def main():
    """Main example function"""
    print("Company Alignment Facilitator - Example Usage")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running this example.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("Choose an example to run:")
    print("1. Single interview workflow")
    print("2. Multiple interviews for comprehensive report")
    print("3. Topic-specific and comparative reports")
    print("4. System statistics")
    print("5. Run all examples")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        example_interview_workflow()
    elif choice == "2":
        example_multiple_interviews()
    elif choice == "3":
        example_topic_specific_reports()
    elif choice == "4":
        example_statistics()
    elif choice == "5":
        print("\n" + "="*60)
        print("RUNNING ALL EXAMPLES")
        print("="*60)
        
        print("\n1. Single interview workflow:")
        example_interview_workflow()
        
        print("\n2. Multiple interviews:")
        example_multiple_interviews()
        
        print("\n3. Topic-specific reports:")
        example_topic_specific_reports()
        
        print("\n4. Statistics:")
        example_statistics()
        
        print("\n✅ All examples completed!")
    else:
        print("Invalid choice. Running single interview workflow...")
        example_interview_workflow()

if __name__ == "__main__":
    main() 