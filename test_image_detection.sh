#!/bin/bash

# Test script to demonstrate automatic image detection

echo "🧪 Testing Automatic Image Detection"
echo "===================================="

# Check what images are available
echo "📁 Images in input_images/ directory:"
ls -la input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null || echo "No images found"

echo
echo "🔍 Testing automatic image detection logic:"

# Test the same logic as the main script
if [[ -d "input_images" ]] && [[ -n "$(ls -A input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null)" ]]; then
    # Use the first image found
    detected_image="$(ls input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null | head -n 1)"
    echo "✅ Found image: $detected_image"
else
    echo "⚠️  No images found in input_images directory"
fi

echo
echo "📋 To add more images:"
echo "1. Copy your wafer images to input_images/ directory"
echo "2. Supported formats: .png, .jpg, .jpeg"
echo "3. The system will automatically use the first image found"
echo "4. Or specify a specific image with -i option"

echo
echo "🎯 Example:"
echo "cp my_wafer.png input_images/"
echo "./gemini_cli_workflow.sh -d \"Semiconductor device with metal contacts\""
