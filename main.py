import os
import subprocess
import sys

def main():
    """Main entry point for Replit deployment"""
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Run Django migrations
    print("Running Django migrations...")
    subprocess.check_call([sys.executable, "manage.py", "migrate"])
    
    # Collect static files (if needed)
    print("Collecting static files...")
    subprocess.check_call([sys.executable, "manage.py", "collectstatic", "--noinput"])
    
    # Create superuser if it doesn't exist
    print("Creating superuser if needed...")
    try:
        subprocess.check_call([
            sys.executable, "manage.py", "shell", "-c",
            "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
        ])
    except:
        print("Superuser creation skipped or failed")
    
    # Start Django development server
    print("Starting Django server...")
    subprocess.check_call([sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])

if __name__ == "__main__":
    main()
