#!/usr/bin/env python3
"""Test runner for MCP endpoint n8n compatibility tests."""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_mcp_tests():
    """Run the MCP endpoint tests."""
    print("🧪 Running MCP endpoint n8n compatibility tests...")
    print("=" * 60)
    
    # Run pytest for the MCP endpoint tests
    test_file = project_root / "tests" / "http_server" / "test_mcp_endpoint.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("📋 Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All MCP endpoint tests passed!")
            return True
        else:
            print(f"❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_n8n_tests():
    """Run only the n8n compatibility tests."""
    print("🔧 Running n8n-specific compatibility tests...")
    print("=" * 60)
    
    test_file = project_root / "tests" / "http_server" / "test_mcp_endpoint.py"
    
    try:
        # Run only the n8n compatibility test class
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            str(test_file) + "::TestMCPEndpointN8NCompatibility",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("📋 n8n Compatibility Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All n8n compatibility tests passed!")
            return True
        else:
            print(f"❌ n8n compatibility tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running n8n compatibility tests: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "pytest",
        "fastapi",
        "httpx"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    # Check pytest-asyncio separately as it might not be importable directly
    try:
        import pytest_asyncio
        print("✅ pytest-asyncio")
    except ImportError:
        try:
            # Try alternative import
            import pytest
            # Check if asyncio support is available
            if hasattr(pytest, 'asyncio'):
                print("✅ pytest-asyncio (via pytest)")
            else:
                print("❌ pytest-asyncio - missing")
                missing_packages.append("pytest-asyncio")
        except ImportError:
            print("❌ pytest-asyncio - missing")
            missing_packages.append("pytest-asyncio")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements-dev.txt")
        return False
    
    print("✅ All dependencies are available")
    return True

def main():
    """Main test runner function."""
    print("🚀 MCP Endpoint n8n Compatibility Test Runner")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--n8n-only":
            success = run_specific_n8n_tests()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python test_mcp_runner.py          # Run all MCP tests")
            print("  python test_mcp_runner.py --n8n-only  # Run only n8n compatibility tests")
            print("  python test_mcp_runner.py --help   # Show this help")
            return
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        success = run_mcp_tests()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ MCP endpoint is compatible with n8n")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        print("❌ MCP endpoint may not be fully compatible with n8n")
        sys.exit(1)

if __name__ == "__main__":
    main() 