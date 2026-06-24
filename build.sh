#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate

# (Optional) Seed the initial database if it is a fresh deployment
# python manage.py seed_data
