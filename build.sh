#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Ensure staticfiles directory exists
mkdir -p staticfiles

# Run Django commands
python manage.py collectstatic --no-input --clear
echo "--- collectstatic completed ---"
echo "Files in staticfiles/:"
ls staticfiles/ | head -20 || echo "WARNING: staticfiles is empty!"

python manage.py migrate

# (Optional) Seed the initial database if it is a fresh deployment
# python manage.py seed_data
