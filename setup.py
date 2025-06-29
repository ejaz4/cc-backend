#!/usr/bin/env python3
"""
Setup script for the Multi-Platform Conversation Summarizer API
"""
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    Multi-Platform Conversation Summarizer API Setup         ║
║                                                              ║
║    🚀 Migrated to Supabase PostgreSQL                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment variables...")
    
    env_file = Path(".env")
    if env_file.exists():
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("📝 Skipping environment setup")
            return True
    
    print("\n📋 Please provide the following information:")
    
    # Supabase configuration
    print("\n🌐 Supabase Configuration:")
    SUPABASE_URI = input("Supabase URL (e.g., https://your-project.supabase.co): ").strip()
    SUPABASE_API_KEY = input("Supabase anon key: ").strip()
    
    # API Keys
    print("\n🔑 API Keys:")
    elevenlabs_key = input("ElevenLabs API key: ").strip()
    openai_key = input("OpenAI API key: ").strip()
    
    # Optional Google Calendar
    print("\n📅 Google Calendar (optional):")
    google_client_id = input("Google Client ID (press Enter to skip): ").strip()
    google_client_secret = input("Google Client Secret (press Enter to skip): ").strip()
    
    # Flask configuration
    print("\n⚙️  Flask Configuration:")
    flask_host = input("Flask host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    flask_port = input("Flask port (default: 5000): ").strip() or "5000"
    flask_debug = input("Debug mode (y/n, default: n): ").lower().strip() or "n"
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    # Create .env file
    env_content = f"""# Database Configuration (Supabase PostgreSQL)
SUPABASE_URI={SUPABASE_URI}
SUPABASE_API_KEY={SUPABASE_API_KEY}

# API Keys (Required)
ELEVENLABS_API_KEY={elevenlabs_key}
OPENAI_API_KEY={openai_key}

# Google Calendar Configuration (Optional)
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}
GOOGLE_REDIRECT_URI=http://localhost:{flask_port}/api/assistant/calendar/callback

# File Storage Configuration
UPLOAD_FOLDER=uploads
AUDIO_FOLDER=audio

# Flask Configuration
FLASK_HOST={flask_host}
FLASK_PORT={flask_port}
FLASK_DEBUG={'True' if flask_debug == 'y' else 'False'}
SECRET_KEY={secret_key}

# OpenAI Configuration
OPENAI_MODEL=gpt-4

# ElevenLabs Configuration
ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Environment file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def setup_supabase():
    """Guide user through Supabase setup"""
    print("\n🌐 Supabase Setup Guide:")
    print("""
1. Go to https://supabase.com and create a free account
2. Create a new project
3. Once created, go to Settings > API
4. Copy your Project URL and anon key
5. Update your .env file with these values

The database tables will be created automatically when you first run the application.
    """)
    
    continue_setup = input("Have you set up your Supabase project? (y/n): ").lower().strip()
    if continue_setup != 'y':
        print("⚠️  Please set up Supabase first, then run this script again")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    try:
        from database.connection import init_database, check_connection
        init_database()
        if check_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["uploads", "audio"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def run_migration():
    """Run database migration"""
    print("\n🚀 Running database migration...")
    try:
        from database.migrations import run_migration
        if run_migration():
            print("✅ Database migration completed")
            return True
        else:
            print("❌ Database migration failed")
            return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup Supabase
    if not setup_supabase():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("\n⚠️  Database connection failed. Please check your Supabase configuration.")
        print("   You can still continue with the setup and test the connection later.")
    
    # Run migration
    if not run_migration():
        print("\n⚠️  Database migration failed. You can run it manually later.")
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Verify your .env file has all required values")
    print("2. Test the application: python main.py")
    print("3. Check the API documentation in README.md")
    print("4. Start building your Android app!")
    print("\n🚀 Happy coding!")

if __name__ == "__main__":
    main() 