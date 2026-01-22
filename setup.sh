#!/bin/bash
# Quick setup script for ImageOptimizer

set -e

echo "ImageOptimizer Quick Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Generate secret keys
echo ""
echo "Generating secret keys..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Create .env file
echo ""
echo "Creating .env file..."
cat > .env << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth (you need to fill these in)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Storage Encryption Key
STORAGE_ENCRYPTION_KEY=$ENCRYPTION_KEY
EOF

echo ""
echo ".env file created with generated keys"
echo "Please update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file"

# Run migrations
echo ""
echo "Running migrations..."
python manage.py migrate

# Ask if user wants to create superuser
echo ""
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py createsuperuser
fi

echo ""
echo "=================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file"
echo "2. Run: source venv/bin/activate (if not already activated)"
echo "3. Run: python manage.py runserver"
echo "4. Visit: http://localhost:8000"
echo ""
echo "For more information, see README.md"
echo "=================================="
