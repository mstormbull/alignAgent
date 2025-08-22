#!/usr/bin/env python3
"""
Main entry point for Company Alignment Facilitator

This module serves as the main entry point for the application,
initializing all components and launching the user interface.
"""

import logging
import sys
from typing import Optional

from config import Config
from facilitator import CompanyAlignmentFacilitator
from ui_interface import UIManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_facilitator() -> Optional[CompanyAlignmentFacilitator]:
    """
    Initialize the Company Alignment Facilitator
    
    Returns:
        Initialized facilitator or None if initialization fails
    """
    try:
        logger.info("Initializing Company Alignment Facilitator...")
        facilitator = CompanyAlignmentFacilitator()
        
        if facilitator.is_demo_mode:
            logger.info("✅ Company Alignment Facilitator initialized in DEMO MODE")
            print("🔑 Demo Mode: Running without OpenAI API key")
            print("   You can explore the interface and see example functionality")
            print("   Set OPENAI_API_KEY environment variable for full features")
        else:
            logger.info("✅ Company Alignment Facilitator initialized successfully")
        
        return facilitator
    except Exception as e:
        logger.error(f"❌ Initialization error: {e}")
        print(f"Initialization error: {e}")
        return None

def create_ui_manager(facilitator: CompanyAlignmentFacilitator) -> UIManager:
    """
    Create the UI manager
    
    Args:
        facilitator: The initialized facilitator
        
    Returns:
        UI manager instance
    """
    try:
        logger.info("Creating UI manager...")
        ui_manager = UIManager(facilitator)
        ui_manager.create_interface()
        logger.info("✅ UI manager created successfully")
        return ui_manager
    except Exception as e:
        logger.error(f"❌ UI creation error: {e}")
        raise

def main():
    """Main application entry point"""
    print("🎯 Company Alignment Facilitator")
    print("=" * 50)
    
    # Initialize the facilitator
    facilitator = initialize_facilitator()
    if not facilitator:
        print("❌ Failed to initialize application")
        sys.exit(1)
    
    try:
        # Create UI manager
        ui_manager = create_ui_manager(facilitator)
        
        print("🚀 Starting Company Alignment Facilitator...")
        print("📝 Make sure to set your OPENAI_API_KEY environment variable")
        print("🌐 The application will be available at http://localhost:7860")
        print("=" * 50)
        
        # Launch the interface
        ui_manager.launch(share=False, debug=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Application interrupted by user")
        if facilitator:
            facilitator.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        print(f"Application error: {e}")
        if facilitator:
            facilitator.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main() 