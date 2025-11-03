#!/bin/bash
# Script to initialize Next.js frontend

cd "$(dirname "$0")/.."

echo "Creating Next.js frontend..."

# Create frontend directory
mkdir -p frontend

cd frontend

# Initialize Next.js project
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*" --use-npm

# Install additional dependencies
npm install zustand date-fns

echo "Next.js frontend initialized!"
echo "Next steps:"
echo "1. cd frontend"
echo "2. npx shadcn-ui@latest init"
echo "3. Follow the prompts to configure shadcn/ui"
