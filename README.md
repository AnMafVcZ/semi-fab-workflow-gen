# Semiconductor Fabrication Workflow Generator

Generate realistic semiconductor fabrication workflows and step-by-step wafer images using AI.

## 🚀 Quick Start

```bash
./gemini_cli_workflow.sh
```

Then follow the prompts to describe your device and generate the workflow!

## 📋 What It Does

1. **Generates fabrication workflows** for any semiconductor device
2. **Creates step-by-step wafer images** showing the fabrication process
3. **Uses realistic tools and materials** from actual semiconductor fabrication
4. **Provides comprehensive output** with both text and visual results

## 🎯 Examples

### Simple Device
**Input**: "Semiconductor device with metal contacts and oxide layer"

**Output**:
- 5-step fabrication workflow using simpler tools
- Step-by-step wafer images showing layer evolution
- Final device structure visualization

### Complex Device  
**Input**: "High-resolution semiconductor device with sub-100nm features"

**Output**:
- 5-step fabrication workflow using advanced tools
- Step-by-step wafer images showing layer evolution
- Final device structure visualization

## 📁 Files

- `gemini_cli_workflow.sh` - Main script (run this!)
- `gemini_workflow_interface.py` - Image generation engine
- `color_mapping.py` - Material definitions
- `Tools_list.csv` - Available fabrication tools
- `GEMINI.md` - Technical documentation for AI

## 🔧 Setup

1. **Install Gemini CLI**:
   ```bash
   brew install google-gemini-cli
   ```

2. **Install Python dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Make script executable**:
   ```bash
   chmod +x gemini_cli_workflow.sh
   ```

## 🎓 Usage

### Interactive Mode
```bash
./gemini_cli_workflow.sh
```

### Command Line Mode
```bash
# Simple device - uses simpler tools
./gemini_cli_workflow.sh -d "Semiconductor device with metal contacts and oxide layer"

# Complex device - uses advanced tools  
./gemini_cli_workflow.sh -d "High-resolution semiconductor device with sub-100nm features"
```

### With Custom Options
```bash
./gemini_cli_workflow.sh -d "Optoelectronic device with transparent electrode" -n opto_device -i my_wafer.png
```

## 📊 Output

```
generated_workflows/
└── device_workflow.txt          # Your fabrication workflow

gemini_workflows/
└── device_name/                 # Step-by-step images
    ├── step_001_substrate.png
    ├── step_002_deposition.png
    ├── ...
    ├── final_wafer.png
    └── workflow_summary.json
```

## 🔍 Troubleshooting

- **Permission denied**: `chmod +x gemini_cli_workflow.sh`
- **Gemini CLI not found**: `brew install google-gemini-cli`
- **Python errors**: Activate virtual environment with `source venv/bin/activate`

## 🚀 Ready to Use!

Just run `./gemini_cli_workflow.sh` and describe your semiconductor device!

---

**Note**: This system solves the original JSON generation loop errors by using a two-step approach that separates workflow generation from image creation.
## Limitations

- YOLO model accuracy degrades on novel device geometries not in training set
- Workflow ordering heuristics assume standard CMOS flow; III-V and MEMS may need manual review
- Image generation works best on cross-sectional views; top-down SEM images need preprocessing
