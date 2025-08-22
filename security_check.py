#!/usr/bin/env python3
"""
Security Check for Company Alignment Facilitator

This script performs security validation to ensure no sensitive data
is exposed in the codebase.
"""

import os
import re
import sys
from pathlib import Path

def check_for_hardcoded_credentials():
    """Check for hardcoded API keys, passwords, or other credentials"""
    print("🔍 Checking for hardcoded credentials...")
    
    # Patterns to look for
    patterns = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
        r'pk_[a-zA-Z0-9]{48}',  # OpenAI public key pattern
        r'[a-zA-Z0-9]{32,}',    # Generic long strings that might be keys
        r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
        r'secret\s*=\s*["\'][^"\']+["\']',    # Hardcoded secrets
        r'api_key\s*=\s*["\'][^"\']+["\']',   # Hardcoded API keys
    ]
    
    # Files to check (Python files only)
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    issues_found = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if re.search(pattern, line):
                            # Skip legitimate patterns (like in tests or examples)
                            if any(skip in line.lower() for skip in ['test-key', 'your-api-key', 'example', 'placeholder']):
                                continue
                            
                            issues_found.append({
                                'file': file_path,
                                'line': line_num,
                                'line_content': line.strip(),
                                'pattern': pattern
                            })
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
    
    if issues_found:
        print("❌ Potential security issues found:")
        for issue in issues_found:
            print(f"   File: {issue['file']}:{issue['line']}")
            print(f"   Content: {issue['line_content']}")
            print()
        return False
    else:
        print("✅ No hardcoded credentials found")
        return True

def check_environment_variables():
    """Check if environment variables are properly used"""
    print("\n🔍 Checking environment variable usage...")
    
    # Check if OPENAI_API_KEY is properly handled
    config_file = Path('config.py')
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()
            if 'os.getenv("OPENAI_API_KEY")' in content:
                print("✅ OPENAI_API_KEY properly loaded from environment")
            else:
                print("❌ OPENAI_API_KEY not properly handled in config.py")
                return False
    else:
        print("❌ config.py not found")
        return False
    
    return True

def check_sensitive_files():
    """Check for sensitive files that shouldn't be committed"""
    print("\n🔍 Checking for sensitive files...")
    
    sensitive_files = [
        '.env', '.env.local', '.env.production', '.env.staging',
        'secrets.json', 'config.json', 'api_keys.txt',
        'credentials.txt', 'openai_api_key.txt'
    ]
    
    found_sensitive = []
    for file in sensitive_files:
        if os.path.exists(file):
            found_sensitive.append(file)
    
    if found_sensitive:
        print("⚠️  Found potentially sensitive files:")
        for file in found_sensitive:
            print(f"   - {file}")
        print("   Make sure these files are in .gitignore")
    else:
        print("✅ No sensitive files found")
    
    return len(found_sensitive) == 0

def check_gitignore():
    """Check if .gitignore properly excludes sensitive files"""
    print("\n🔍 Checking .gitignore configuration...")
    
    if not os.path.exists('.gitignore'):
        print("❌ No .gitignore file found")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    required_patterns = [
        '.env',
        '*.key',
        'secrets.json',
        'conversations/',
        '__pycache__/'
    ]
    
    missing_patterns = []
    for pattern in required_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print("❌ Missing patterns in .gitignore:")
        for pattern in missing_patterns:
            print(f"   - {pattern}")
        return False
    else:
        print("✅ .gitignore properly configured")
        return True

def check_file_permissions():
    """Check file permissions for security"""
    print("\n🔍 Checking file permissions...")
    
    # Check if conversations directory exists and has proper permissions
    if os.path.exists('conversations'):
        stat = os.stat('conversations')
        mode = stat.st_mode & 0o777
        
        if mode == 0o755 or mode == 0o750:
            print("✅ conversations/ directory has secure permissions")
        else:
            print(f"⚠️  conversations/ directory has permissions: {oct(mode)}")
            print("   Consider setting to 755 or 750")
    else:
        print("ℹ️  conversations/ directory doesn't exist yet")
    
    return True

def main():
    """Run all security checks"""
    print("🔒 Company Alignment Facilitator - Security Check")
    print("=" * 50)
    
    checks = [
        ("Hardcoded Credentials", check_for_hardcoded_credentials),
        ("Environment Variables", check_environment_variables),
        ("Sensitive Files", check_sensitive_files),
        ("Git Ignore", check_gitignore),
        ("File Permissions", check_file_permissions)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name} check: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 50)
    print("SECURITY CHECK SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All security checks passed!")
        print("Your codebase appears to be secure.")
    else:
        print("⚠️  Some security issues were found.")
        print("Please address the issues above before deployment.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 