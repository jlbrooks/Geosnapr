#!bin/bash

# Change to the frebapps directory
cd /opt/Team177/frebapps/

# Copy settings
cp frebapps/settings.prod.py frebapps/settings.py

# Collect static

# Restart gunicorn
service gunicorn restart