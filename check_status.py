#!/usr/bin/env python3
"""
Simple status check for FastAPI application
"""

import sys

def check_imports():
    """Check if all imports work correctly"""
    try:
        print("Checking imports...")
        
        # Test basic imports
        from api.models import SummaryRequest, PlatformType
        print("✓ Pydantic models imported successfully")
        
        # Test creating a model
        request = SummaryRequest(summary_length="medium")
        print("✓ Model creation successful")
        
        # Test enum
        print(f"✓ Platform enum: {PlatformType.WHATSAPP}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main function"""
    print("🔍 FastAPI Application Status Check")
    print("=" * 40)
    
    if check_imports():
        print("\n✅ All imports successful!")
        print("🎉 FastAPI application should be ready to run!")
        print("\nTo start the application:")
        print("   python main.py")
        print("\nTo test the API:")
        print("   curl http://localhost:8000/api/health")
        return True
    else:
        print("\n❌ There are import issues to resolve.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 