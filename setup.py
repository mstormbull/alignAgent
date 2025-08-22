#!/usr/bin/env python3
"""
Setup script for Company Alignment Facilitator

This script helps users set up the application by:
1. Installing dependencies
2. Checking for required environment variables
3. Creating necessary directories
4. Providing setup instructions
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_openai_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is not set")
        print("\nTo set your API key, run one of the following:")
        print("1. Export as environment variable:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("2. Create a .env file in the project root:")
        print("   echo 'OPENAI_API_KEY=your-api-key-here' > .env")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return False
    else:
        # Check if it looks like a valid OpenAI API key format
        if api_key.startswith('sk-') and len(api_key) > 20:
            print("✅ OPENAI_API_KEY is set and appears to be valid")
        else:
            print("⚠️  OPENAI_API_KEY is set but may not be in the correct format")
            print("   Expected format: sk-... (starts with 'sk-' and is longer than 20 characters)")
        return True

def check_security_files():
    """Check for potential security issues"""
    print("\n🔒 Checking for security issues...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("⚠️  .env file found - make sure it's in .gitignore")
    else:
        print("✅ No .env file found")
    
    # Check for other potential credential files
    sensitive_files = [
        'secrets.json', 'config.json', 'api_keys.txt', 
        'credentials.txt', 'openai_api_key.txt'
    ]
    
    found_sensitive = False
    for file in sensitive_files:
        if os.path.exists(file):
            print(f"⚠️  Found potentially sensitive file: {file}")
            found_sensitive = True
    
    if not found_sensitive:
        print("✅ No sensitive files found")
    
    # Check .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            if '.env' in gitignore_content:
                print("✅ .env is in .gitignore")
            else:
                print("⚠️  .env not found in .gitignore")
    else:
        print("⚠️  No .gitignore file found")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    try:
        os.makedirs("conversations", exist_ok=True)
        print("✅ Created conversations/ directory")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("\n🧪 Testing imports...")
    required_packages = [
        "gradio",
        "langchain",
        "langchain_openai",
        "openai"
    ]
    
    failed_imports = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def main():
    """Main setup function"""
    print("🎯 Company Alignment Facilitator - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Check API key
    api_key_ok = check_openai_api_key()
    
    # Check security
    check_security_files()
    
    print("\n" + "=" * 50)
    if api_key_ok:
        print("🎉 Setup completed successfully!")
        print("\nTo start the application, run:")
        print("python main.py")
        print("\nTo run examples, run:")
        print("python example_usage.py")
    else:
        print("⚠️  Setup completed with warnings")
        print("Please set your OPENAI_API_KEY before running the application")
    
    print("\n📚 For more information, see README.md")
    print("🔒 For security best practices, see the Security Considerations section in README.md")

if __name__ == "__main__":
    main() 