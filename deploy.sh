#!/bin/bash

# Define paths
FRONTEND_PATH="/home/ubuntu/SRPC-2025/UWM_Event_Frontend"
BACKEND_PATH="$(pwd)"

# Deploy Frontend
echo "Deploying frontend..."
cd "$FRONTEND_PATH" || { echo "Failed to navigate to frontend path"; exit 1; }

git pull || { echo "Failed to pull frontend code"; exit 1; }

sudo cp -r build /var/www || { echo "Failed to copy build directory"; exit 1; }

sudo systemctl restart nginx || { echo "Failed to restart nginx"; exit 1; }

echo "Frontend deployed successfully. Now deploying backend."

# Deploy Backend
echo "Deploying backend..."
cd "$BACKEND_PATH" || { echo "Failed to navigate to backend path"; exit 1; }

git pull || { echo "Failed to pull backend code"; exit 1; }
pip install -r requirements.txt || { echo "Failed to install Python dependencies"; exit 1; }
sudo systemctl restart gunicorn-srpc || { echo "Failed to restart gunicorn-srpc"; exit 1; }

echo "Backend deployed successfully. Deployment complete."
