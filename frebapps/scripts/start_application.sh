#!/bin/bash

# Change to the frebapps directory
cd /opt/Team177/frebapps/

# Use pip to install dependencies
pip install -r requirements.txt

# Copy settings
cp frebapps/settings.prod.py frebapps/settings.py

# Collect static
python manage.py collectstatic

# Restart gunicorn
service gunicorn restart