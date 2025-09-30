#!/bin/bash
# Database setup script for Render deployment
# Run this in Render's console to create missing database tables

echo "🚀 Crooks Command Center - Database Setup"
echo "=========================================="

# Navigate to the setup directory
cd "$(dirname "$0")"

# Check if we're in the right place
if [ ! -f "create_database_tables.py" ]; then
    echo "❌ Error: create_database_tables.py not found"
    echo "Make sure you're running this from the backend/setup/ directory"
    exit 1
fi

# Check for database URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable not found"
    echo "This script should be run on Render where DATABASE_URL is available"
    exit 1
fi

echo "✅ Found DATABASE_URL environment variable"
echo "🔗 Database: ${DATABASE_URL%%@*}@***"

# Install dependencies and run setup
echo "📦 Installing dependencies..."
pip install sqlalchemy psycopg2-binary

echo "🛠️  Running database setup..."
python create_database_tables.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Database setup completed successfully!"
    echo ""
    echo "✅ What was created:"
    echo "   - intelligence_files table"
    echo "   - Performance indexes"
    echo "   - Automatic timestamp updates"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Your Intelligence module should now work"
    echo "   2. Try uploading files - no more PostgreSQL errors"
    echo "   3. Check your database to see the new table"
else
    echo ""
    echo "💥 Database setup failed!"
    echo "Check the error messages above and try again."
    exit 1
fi
