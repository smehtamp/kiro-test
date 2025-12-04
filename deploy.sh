#!/bin/bash
set -e

echo "Building and deploying Events API..."

# Build the SAM application
sam build

# Deploy the application
sam deploy --guided --capabilities CAPABILITY_IAM

echo "Deployment complete!"
