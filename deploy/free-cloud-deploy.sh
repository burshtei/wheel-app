#!/bin/bash

# Free Cloud Deployment Helper Script
# This script helps you deploy to free cloud platforms

set -e

echo "🎉 Free Cloud Deployment for Wheel Strategy Analyzer"
echo "===================================================="
echo ""
echo "This script will guide you through deploying to FREE cloud platforms."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Available FREE cloud platforms:"
echo ""
echo "1. Render.com - Easy setup, 750 free hours/month"
echo "2. Fly.io - 3 shared-cpu VMs free, auto-sleep when idle"
echo "3. Railway.app - $5 free credits monthly"
echo ""
echo "Choose a platform (1-3):"
read -r choice

case $choice in
    1)
        echo ""
        echo "🚀 Deploying to Render.com"
        echo "========================="
        echo ""
        echo "Prerequisites:"
        echo "  1. Create a free account at https://render.com"
        echo "  2. Connect your GitHub account"
        echo ""
        echo "Steps to deploy:"
        echo "  1. Go to https://dashboard.render.com"
        echo "  2. Click 'New +' → 'Blueprint'"
        echo "  3. Connect this repository"
        echo "  4. Render will automatically detect render.yaml and deploy!"
        echo ""
        echo "Your app will be live at: https://wheel-analyzer.onrender.com"
        echo ""
        echo "📝 Note: Free tier spins down after 15 mins of inactivity"
        echo "   First request after sleep takes ~30 seconds"
        ;;
    2)
        echo ""
        echo "🚀 Deploying to Fly.io"
        echo "====================="
        echo ""

        if ! command_exists flyctl; then
            echo "Installing Fly CLI..."
            curl -L https://fly.io/install.sh | sh
            echo ""
            echo "⚠️  Please restart your terminal and run this script again"
            exit 0
        fi

        echo "Fly CLI detected!"
        echo ""
        echo "Step 1: Login to Fly.io (creates free account if needed)"
        flyctl auth login

        echo ""
        echo "Step 2: Launching your app..."
        flyctl launch --config fly.toml --now

        echo ""
        echo "✅ Deployment complete!"
        echo "Your app is now live!"
        echo ""
        echo "Useful commands:"
        echo "  flyctl status          - Check app status"
        echo "  flyctl logs            - View logs"
        echo "  flyctl open            - Open app in browser"
        ;;
    3)
        echo ""
        echo "🚀 Deploying to Railway.app"
        echo "==========================="
        echo ""
        echo "Prerequisites:"
        echo "  1. Create a free account at https://railway.app"
        echo "  2. Connect your GitHub account"
        echo ""
        echo "Steps to deploy:"
        echo "  1. Go to https://railway.app/new"
        echo "  2. Click 'Deploy from GitHub repo'"
        echo "  3. Select this repository (burshtei/wheel-app)"
        echo "  4. Railway will auto-detect the Dockerfile and deploy!"
        echo "  5. Click 'Generate Domain' to get a public URL"
        echo ""
        echo "Your app will be live at: https://wheel-analyzer.up.railway.app"
        echo ""
        echo "📝 Note: Free tier includes $5 credit monthly"
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 For more details, see FREE-DEPLOYMENT.md"
