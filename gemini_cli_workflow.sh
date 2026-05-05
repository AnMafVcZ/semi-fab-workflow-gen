#!/bin/bash

# Semiconductor Fabrication Workflow Generator using Gemini CLI
# This script uses Gemini CLI directly to generate workflows

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Gemini CLI is installed
check_gemini() {
    if ! command -v gemini &> /dev/null; then
        print_error "Gemini CLI is not installed. Please install it first:"
        echo "brew install google-gemini-cli"
        exit 1
    fi
    print_success "Gemini CLI found"
}

# Create simplified prompt for workflow generation
create_workflow_prompt() {
    local device_description="$1"
    
    cat > workflow_prompt.txt << EOF
You are a semiconductor fabrication expert. Generate a realistic fabrication workflow for the following device:

DEVICE DESCRIPTION: $device_description

REQUIREMENTS:
1. Generate ONLY a numbered list of fabrication steps (e.g., "1. Step description")
2. Use tools from the provided Tools_list.csv
3. Include realistic materials (silicon, sio2, metals, etc.)
4. Follow semiconductor fabrication logic (substrate → oxide → lithography → etch → metal)
5. Keep each step concise but specific
6. Do NOT include process parameters (temperature, time, etc.)
7. Do NOT generate images or diagrams

TOOL SELECTION GUIDELINES:
- For SIMPLE devices (basic metal contacts, simple oxide layers): Use simpler tools
  * Use Lesker PVD 75 for basic metal deposition (no need for complex RTP)
  * Use Oxford Pro 80 RIE for basic etching
  * Use MJB3 Mask Aligner for basic lithography
- For COMPLEX devices (high-resolution features, special materials): Use advanced tools
  * Use Raith EBPG5150 E-beam for sub-100nm features
  * Use AccuThermo AW 610M RTP for thermal processing
  * Use Veeco Thermal ALD for atomic layer deposition
- Choose the SIMPLEST tool that meets the requirements
- Avoid over-engineering simple processes

AVAILABLE TOOLS: See Tools_list.csv for tool names and capabilities
AVAILABLE MATERIALS: silicon, sio2, si3n4, titanium, copper, gold, aluminum, photoresist

FORMAT YOUR RESPONSE AS:
1. [First fabrication step]
2. [Second fabrication step]
3. [Third fabrication step]
...and so on

Generate a realistic fabrication workflow for the described device.
EOF
}

# Extract workflow text from Gemini output
extract_workflow() {
    local output_file="$1"
    local workflow_file="$2"
    
    # Look for numbered steps in the output
    grep -E '^[0-9]+\.' "$output_file" > "$workflow_file" || {
        print_warning "No numbered steps found in Gemini output"
        print_status "Full Gemini output:"
        cat "$output_file"
        return 1
    }
    
    print_success "Workflow extracted successfully"
    return 0
}

# Main workflow generation function
generate_workflow() {
    local device_description="$1"
    local workflow_name="${2:-device_fabrication}"
    local input_image="${3:-}"
    if [[ -z "$input_image" ]]; then
        # Check if there are any images in input_images directory
        if [[ -d "input_images" ]] && [[ -n "$(ls -A input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null)" ]]; then
            # Use the first image found
            input_image="$(ls input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null | head -n 1)"
        else
            input_image="input_images/zooked.png"
            print_warning "No images found in input_images directory, using default"
        fi
    fi
    
    print_status "=== Semiconductor Fabrication Workflow Generator ==="
    print_status "Device: $device_description"
    print_status "Workflow Name: $workflow_name"
    print_status "Input Image: $input_image"
    echo
    
    # Check dependencies
    check_gemini
    
    # Check if input image exists
    if [[ ! -f "$input_image" ]]; then
        print_warning "Input image not found: $input_image"
        print_status "Using default wafer substrate..."
    fi
    
    # Create output directories
    mkdir -p generated_workflows
    mkdir -p gemini_workflows
    
    # Step 1: Generate workflow text using Gemini CLI
    print_status "Step 1: Generating fabrication workflow text..."
    
    # Create prompt file
    create_workflow_prompt "$device_description"
    
    # Run Gemini CLI
    print_status "Running Gemini CLI..."
    gemini \
        --model gemini-1.5-pro \
        --prompt "$(cat workflow_prompt.txt)" \
        --file workflow_prompt.txt \
        --file Tools_list.csv \
        --file "$input_image" \
        --max-tokens 2000 \
        --temperature 0.3 \
        > gemini_output.txt 2> gemini_error.txt
    
    # Check if Gemini CLI succeeded
    if [[ $? -ne 0 ]]; then
        print_error "Gemini CLI failed"
        print_status "Error output:"
        cat gemini_error.txt
        exit 1
    fi
    
    # Extract workflow text
    workflow_file="generated_workflows/${workflow_name}_workflow.txt"
    if extract_workflow "gemini_output.txt" "$workflow_file"; then
        print_success "Workflow text generated successfully!"
        print_status "Workflow saved to: $workflow_file"
        echo
        print_status "Generated workflow:"
        cat "$workflow_file"
        echo
    else
        print_error "Failed to extract workflow from Gemini output"
        exit 1
    fi
    
    # Step 2: Generate images using Python interface
    print_status "Step 2: Creating step-by-step wafer images..."
    
    # Activate virtual environment if it exists
    if [[ -d "venv" ]]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run Python image generation
    python3 -c "
import sys
sys.path.append('.')
from gemini_workflow_interface import generate_wafer_workflow_images

workflow_text = '''$(cat "$workflow_file")'''

result = generate_wafer_workflow_images(
    workflow_text=workflow_text,
    input_image_path='$input_image',
    workflow_name='$workflow_name'
)

if result['status'] == 'success':
    print('✅ Images created successfully!')
    print(f'📁 Output directory: {result[\"output_directory\"]}')
    print(f'📊 Total steps: {result[\"total_steps\"]}')
    print(f'📄 Files generated: {len(result[\"files_generated\"])}')
else:
    print(f'❌ Image generation failed: {result.get(\"error\", \"Unknown error\")}')
    sys.exit(1)
"
    
    if [[ $? -eq 0 ]]; then
        print_success "Images created successfully!"
    else
        print_error "Image generation failed"
        exit 1
    fi
    
    # Clean up temporary files
    rm -f workflow_prompt.txt gemini_output.txt gemini_error.txt
    
    echo
    print_success "=== WORKFLOW GENERATION COMPLETE ==="
    print_status "Workflow text: $workflow_file"
    print_status "Images: gemini_workflows/$workflow_name/"
    print_status "Total steps: $(grep -c '^[0-9]\+\.' "$workflow_file")"
}

# Interactive mode
interactive_mode() {
    echo "🚀 Semiconductor Fabrication Workflow Generator"
    echo "================================================"
    echo
    
    echo "Please describe the semiconductor device you want to fabricate:"
    echo "Examples:"
    echo "- Semiconductor device with metal contacts and oxide layer"
    echo "- Optoelectronic device with transparent electrode"
    echo "- MEMS sensor with silicon nitride membrane"
    echo "- Semiconductor sensor with metal contacts"
    echo
    
    read -p "Device description: " device_description
    
    if [[ -z "$device_description" ]]; then
        print_error "No device description provided. Exiting."
        exit 1
    fi
    
    read -p "Workflow name (optional, press Enter for default): " workflow_name
    if [[ -z "$workflow_name" ]]; then
        workflow_name="device_fabrication"
    fi
    
    read -p "Input image path (optional, press Enter for default): " input_image
    if [[ -z "$input_image" ]]; then
        # Check if there are any images in input_images directory
        if [[ -d "input_images" ]] && [[ -n "$(ls -A input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null)" ]]; then
            # Use the first image found
            input_image="$(ls input_images/*.png input_images/*.jpg input_images/*.jpeg 2>/dev/null | head -n 1)"
            print_status "Using input image: $input_image"
        else
            input_image="input_images/zooked.png"
            print_warning "No images found in input_images directory, using default"
        fi
    fi
    
    echo
    print_status "Device: $device_description"
    print_status "Workflow Name: $workflow_name"
    print_status "Input Image: $input_image"
    echo
    
    read -p "Proceed with workflow generation? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_status "Workflow generation cancelled."
        exit 0
    fi
    
    generate_workflow "$device_description" "$workflow_name" "$input_image"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -d, --device DESCRIPTION    Device description"
    echo "  -n, --name NAME             Workflow name (default: device_fabrication)"
    echo "  -i, --image PATH            Input image path (default: first image in input_images/)"
    echo "  -h, --help                  Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -d \"Semiconductor device with metal contacts and oxide layer\"  # Simple device"
    echo "  $0 -d \"High-resolution semiconductor device with sub-100nm features\"  # Complex device"
    echo "  $0 -d \"Optoelectronic device with transparent electrode\" -n opto_device -i my_wafer.png"
    echo "  $0  # Interactive mode"
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    interactive_mode
else
    device_description=""
    workflow_name="device_fabrication"
    input_image=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--device)
                device_description="$2"
                shift 2
                ;;
            -n|--name)
                workflow_name="$2"
                shift 2
                ;;
            -i|--image)
                input_image="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [[ -z "$device_description" ]]; then
        print_error "Device description is required"
        show_usage
        exit 1
    fi
    
    generate_workflow "$device_description" "$workflow_name" "$input_image"
fi
