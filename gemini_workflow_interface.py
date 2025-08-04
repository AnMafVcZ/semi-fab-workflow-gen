#!/usr/bin/env python3
"""
Gemini Workflow Interface
Realistic semiconductor fabrication functions for layer-by-layer wafer image generation
"""

import os
import json
import numpy as np
import cv2
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from color_mapping import MATERIAL_COLORS, MATERIAL_COLOR_INFO

@dataclass
class FabricationStep:
    """Represents a single fabrication step from Gemini workflow"""
    step_number: int
    process_name: str
    tool_name: str
    materials: List[str]
    purpose: str
    layer_being_fabricated: str

class WaferFabricationEngine:
    """
    Realistic semiconductor fabrication engine for layer-by-layer wafer generation
    """
    
    def __init__(self, wafer_width: int = 800, wafer_height: int = 600):
        self.wafer_width = wafer_width
        self.wafer_height = wafer_height
        self.material_colors = MATERIAL_COLORS
        self.current_wafer = None
        self.layer_stack = []  # Track layer history
        self.feature_sizes = {}  # Track feature dimensions
        
    def create_silicon_substrate(self) -> np.ndarray:
        """Create initial silicon substrate wafer"""
        wafer = np.full((self.wafer_height, self.wafer_width, 3), 
                       self.material_colors['silicon'], dtype=np.uint8)
        
        # Add some realistic silicon texture
        noise = np.random.normal(0, 10, (self.wafer_height, self.wafer_width, 3))
        wafer = np.clip(wafer.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        self.current_wafer = wafer.copy()
        self.layer_stack.append({
            'name': 'silicon_substrate',
            'material': 'silicon',
            'thickness': self.wafer_height,
            'position': 0
        })
        
        return wafer
    
    def deposit_layer(self, material: str, thickness: int = 50, 
                     deposition_type: str = 'uniform') -> np.ndarray:
        """
        Deposit a new material layer on top of current wafer
        
        Args:
            material: Material to deposit (sio2, si3n4, titanium, copper, etc.)
            thickness: Layer thickness in pixels
            deposition_type: 'uniform', 'patterned', 'selective'
        """
        if self.current_wafer is None:
            raise ValueError("No wafer exists. Create silicon substrate first.")
        
        new_wafer = np.zeros((self.wafer_height + thickness, self.wafer_width, 3), dtype=np.uint8)
        
        # Copy existing wafer to bottom
        new_wafer[:self.wafer_height, :] = self.current_wafer
        
        # Add new layer on top
        material_color = self.material_colors.get(material, (128, 128, 128))
        
        if deposition_type == 'uniform':
            # Uniform deposition across entire wafer
            new_wafer[self.wafer_height:, :] = material_color
            
        elif deposition_type == 'patterned':
            # Patterned deposition (stripes, dots, etc.)
            pattern = self._create_deposition_pattern(material_color, thickness)
            new_wafer[self.wafer_height:, :] = pattern
            
        elif deposition_type == 'selective':
            # Selective deposition (only in certain areas)
            mask = self._create_selective_mask()
            new_wafer[self.wafer_height:, :] = np.where(
                mask, material_color, self.material_colors['empty']
            )
        
        # Add realistic material texture
        new_wafer = self._add_material_texture(new_wafer, material, self.wafer_height)
        
        self.current_wafer = new_wafer.copy()
        self.wafer_height += thickness
        
        self.layer_stack.append({
            'name': f'{material}_layer',
            'material': material,
            'thickness': thickness,
            'position': len(self.layer_stack),
            'deposition_type': deposition_type
        })
        
        return new_wafer
    
    def etch_layer(self, material: str, etch_depth: int = 30, 
                  etch_pattern: str = 'stripes', etch_ratio: float = 0.5) -> np.ndarray:
        """
        Etch material from the wafer
        
        Args:
            material: Material to etch
            etch_depth: How deep to etch (pixels)
            etch_pattern: 'stripes', 'dots', 'holes', 'trenches'
            etch_ratio: Fraction of material to remove (0.0-1.0)
        """
        if self.current_wafer is None:
            raise ValueError("No wafer exists.")
        
        new_wafer = self.current_wafer.copy()
        material_color = self.material_colors.get(material, (128, 128, 128))
        empty_color = self.material_colors['empty']
        
        # Find material pixels
        material_mask = np.all(new_wafer == material_color, axis=2)
        
        if etch_pattern == 'stripes':
            # Create vertical stripes
            stripe_width = max(10, int(self.wafer_width * 0.05))
            for x in range(0, self.wafer_width, stripe_width * 2):
                material_mask[:, x:x+stripe_width] = False
                
        elif etch_pattern == 'dots':
            # Create dot pattern
            dot_size = max(5, int(min(self.wafer_width, self.wafer_height) * 0.02))
            for y in range(0, self.wafer_height, dot_size * 3):
                for x in range(0, self.wafer_width, dot_size * 3):
                    material_mask[y:y+dot_size, x:x+dot_size] = False
                    
        elif etch_pattern == 'holes':
            # Create circular holes
            hole_radius = max(8, int(min(self.wafer_width, self.wafer_height) * 0.015))
            for y in range(hole_radius, self.wafer_height, hole_radius * 4):
                for x in range(hole_radius, self.wafer_width, hole_radius * 4):
                    cv2.circle(material_mask, (x, y), hole_radius, False, -1)
                    
        elif etch_pattern == 'trenches':
            # Create deep trenches
            trench_width = max(15, int(self.wafer_width * 0.03))
            for x in range(0, self.wafer_width, trench_width * 3):
                material_mask[:, x:x+trench_width] = False
        
        # Apply etching
        new_wafer[material_mask] = empty_color
        
        # Apply etch depth (remove from top layers)
        if etch_depth > 0:
            top_layers = new_wafer[-etch_depth:, :]
            # Create depth variation
            depth_mask = np.random.random((etch_depth, self.wafer_width)) < etch_ratio
            top_layers[depth_mask] = empty_color
            new_wafer[-etch_depth:, :] = top_layers
        
        self.current_wafer = new_wafer.copy()
        
        # Update layer stack
        self.layer_stack.append({
            'name': f'etch_{material}',
            'material': material,
            'etch_depth': etch_depth,
            'etch_pattern': etch_pattern,
            'etch_ratio': etch_ratio
        })
        
        return new_wafer
    
    def apply_lithography(self, resist_type: str = 'positive', 
                         pattern_type: str = 'stripes', 
                         feature_size: int = 20) -> np.ndarray:
        """
        Apply photolithography to create patterns
        
        Args:
            resist_type: 'positive' or 'negative'
            pattern_type: 'stripes', 'dots', 'lines', 'custom'
            feature_size: Size of features in pixels
        """
        if self.current_wafer is None:
            raise ValueError("No wafer exists.")
        
        new_wafer = self.current_wafer.copy()
        
        # Create photoresist layer (temporary)
        resist_color = (200, 150, 100)  # Photoresist color
        resist_thickness = 30
        
        # Add resist layer
        resist_layer = np.full((resist_thickness, self.wafer_width, 3), resist_color, dtype=np.uint8)
        new_wafer = np.vstack([new_wafer, resist_layer])
        
        # Create pattern in resist
        pattern_mask = np.ones((resist_thickness, self.wafer_width), dtype=bool)
        
        if pattern_type == 'stripes':
            # Vertical stripes
            stripe_width = feature_size
            for x in range(0, self.wafer_width, stripe_width * 2):
                pattern_mask[:, x:x+stripe_width] = False
                
        elif pattern_type == 'dots':
            # Dot pattern
            dot_size = max(3, feature_size // 2)
            for y in range(0, resist_thickness, dot_size * 3):
                for x in range(0, self.wafer_width, dot_size * 3):
                    pattern_mask[y:y+dot_size, x:x+dot_size] = False
                    
        elif pattern_type == 'lines':
            # Horizontal lines
            line_height = max(2, feature_size // 4)
            for y in range(0, resist_thickness, line_height * 3):
                pattern_mask[y:y+line_height, :] = False
        
        # Apply pattern (remove resist where pattern is)
        if resist_type == 'positive':
            new_wafer[-resist_thickness:, :][~pattern_mask] = self.material_colors['empty']
        else:  # negative resist
            new_wafer[-resist_thickness:, :][pattern_mask] = self.material_colors['empty']
        
        self.current_wafer = new_wafer.copy()
        self.wafer_height += resist_thickness
        
        self.layer_stack.append({
            'name': f'lithography_{pattern_type}',
            'resist_type': resist_type,
            'pattern_type': pattern_type,
            'feature_size': feature_size
        })
        
        return new_wafer
    
    def thermal_processing(self, process_type: str = 'oxidation', 
                          temperature: int = 1000, duration: int = 60) -> np.ndarray:
        """
        Apply thermal processing (oxidation, annealing, etc.)
        
        Args:
            process_type: 'oxidation', 'annealing', 'diffusion'
            temperature: Process temperature (affects growth rate)
            duration: Process duration (affects layer thickness)
        """
        if self.current_wafer is None:
            raise ValueError("No wafer exists.")
        
        new_wafer = self.current_wafer.copy()
        
        if process_type == 'oxidation':
            # Grow oxide layer on silicon
            growth_rate = min(temperature / 1000.0, 2.0)  # Temperature effect
            growth_time = duration / 60.0  # Duration effect
            oxide_thickness = int(20 * growth_rate * growth_time)
            
            if oxide_thickness > 0:
                new_wafer = self.deposit_layer('sio2', oxide_thickness, 'uniform')
                
        elif process_type == 'annealing':
            # Annealing changes material properties (color/texture)
            # Add some color variation to simulate annealing effects
            noise = np.random.normal(0, 15, new_wafer.shape)
            new_wafer = np.clip(new_wafer.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            
        elif process_type == 'diffusion':
            # Diffusion creates gradual material transitions
            # Create gradient effect
            gradient = np.linspace(0, 1, new_wafer.shape[0])[:, np.newaxis, np.newaxis]
            diffusion_effect = (gradient * 20).astype(np.uint8)
            new_wafer = np.clip(new_wafer.astype(np.float32) + diffusion_effect, 0, 255).astype(np.uint8)
        
        self.current_wafer = new_wafer.copy()
        
        self.layer_stack.append({
            'name': f'thermal_{process_type}',
            'process_type': process_type,
            'temperature': temperature,
            'duration': duration
        })
        
        return new_wafer
    
    def metal_deposition(self, metal_type: str = 'titanium', 
                        thickness: int = 40, 
                        deposition_method: str = 'pvd') -> np.ndarray:
        """
        Deposit metal layers
        
        Args:
            metal_type: 'titanium', 'copper', 'gold', 'aluminum'
            thickness: Metal layer thickness
            deposition_method: 'pvd', 'cvd', 'evaporation'
        """
        if self.current_wafer is None:
            raise ValueError("No wafer exists.")
        
        # Metal deposition is similar to regular deposition but with metal-specific properties
        new_wafer = self.deposit_layer(metal_type, thickness, 'uniform')
        
        # Add metal-specific texture
        if deposition_method == 'pvd':
            # Physical vapor deposition - more uniform
            pass
        elif deposition_method == 'evaporation':
            # Evaporation - may have some non-uniformity
            noise = np.random.normal(0, 8, new_wafer.shape)
            new_wafer = np.clip(new_wafer.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        self.layer_stack.append({
            'name': f'metal_{metal_type}',
            'material': metal_type,
            'thickness': thickness,
            'deposition_method': deposition_method
        })
        
        return new_wafer
    
    def _create_deposition_pattern(self, material_color: Tuple[int, int, int], 
                                 thickness: int) -> np.ndarray:
        """Create patterned deposition"""
        pattern = np.full((thickness, self.wafer_width, 3), material_color, dtype=np.uint8)
        
        # Add some pattern variation
        for i in range(0, self.wafer_width, 50):
            if np.random.random() < 0.3:  # 30% chance of gap
                pattern[:, i:i+20] = self.material_colors['empty']
        
        return pattern
    
    def _create_selective_mask(self) -> np.ndarray:
        """Create mask for selective deposition"""
        mask = np.random.random((self.wafer_height, self.wafer_width)) < 0.7
        return mask
    
    def _add_material_texture(self, wafer: np.ndarray, material: str, 
                            start_y: int) -> np.ndarray:
        """Add realistic material texture"""
        if material == 'sio2':
            # Oxide has some roughness
            noise = np.random.normal(0, 5, wafer[start_y:, :, :].shape)
        elif material in ['titanium', 'copper', 'gold', 'aluminum']:
            # Metals have grain structure
            noise = np.random.normal(0, 8, wafer[start_y:, :, :].shape)
        else:
            # Other materials
            noise = np.random.normal(0, 3, wafer[start_y:, :, :].shape)
        
        wafer[start_y:, :, :] = np.clip(
            wafer[start_y:, :, :].astype(np.float32) + noise, 0, 255
        ).astype(np.uint8)
        
        return wafer
    
    def get_wafer_cross_section(self) -> np.ndarray:
        """Get current wafer cross-section"""
        if self.current_wafer is None:
            return self.create_silicon_substrate()
        return self.current_wafer.copy()
    
    def get_layer_stack_info(self) -> List[Dict]:
        """Get information about the layer stack"""
        return self.layer_stack.copy()

class WorkflowParser:
    """Parse Gemini-generated text workflow into structured data"""
    
    def __init__(self, tools_csv_path: str = "Tools_list.csv"):
        self.tools_df = self.load_tools_list(tools_csv_path)
        self.available_tools = set(self.tools_df['Tool Name'].tolist()) if not self.tools_df.empty else set()
    
    def load_tools_list(self, csv_path: str) -> pd.DataFrame:
        """Load tools list from CSV file"""
        try:
            return pd.read_csv(csv_path)
        except FileNotFoundError:
            print(f"Warning: Tools list not found at {csv_path}")
            return pd.DataFrame()
    
    def parse_gemini_workflow(self, workflow_text: str) -> List[FabricationStep]:
        """Parse Gemini-generated workflow text into structured steps"""
        steps = []
        lines = workflow_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for step numbers (e.g., "1.", "2.", etc.)
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                step_num = int(step_match.group(1))
                step_desc = step_match.group(2)
                
                # Extract process name, tool, and materials
                process_name, tool_name, materials = self._extract_step_info(step_desc)
                
                step = FabricationStep(
                    step_number=step_num,
                    process_name=process_name,
                    tool_name=tool_name,
                    materials=materials,
                    purpose=step_desc,
                    layer_being_fabricated=self._identify_layer(step_desc)
                )
                steps.append(step)
        
        return steps
    
    def _extract_step_info(self, step_desc: str) -> Tuple[str, str, List[str]]:
        """Extract process name, tool name, and materials from step description"""
        process_name = "Unknown"
        tool_name = "Unknown"
        materials = []
        
        # Common process keywords
        process_keywords = {
            'lithography': ['lithography', 'photolithography', 'e-beam', 'laser writing'],
            'etching': ['etch', 'etching', 'rie', 'icp', 'xef2'],
            'deposition': ['deposition', 'deposit', 'cvd', 'pecvd', 'ald', 'pvd', 'evaporation'],
            'processing': ['strip', 'ashing', 'thermal', 'rtp', 'dicing', 'cleaning', 'annealing', 'oxidation']
        }
        
        # Identify process type
        step_lower = step_desc.lower()
        for process_type, keywords in process_keywords.items():
            if any(keyword in step_lower for keyword in keywords):
                process_name = process_type.title()
                break
        
        # Extract tool name (look for tool names from our list)
        for tool in self.available_tools:
            if tool.lower() in step_lower:
                tool_name = tool
                break
        
        # Extract materials
        material_keywords = list(MATERIAL_COLORS.keys())
        for material in material_keywords:
            if material in step_lower:
                materials.append(material)
        
        return process_name, tool_name, materials
    
    def _identify_layer(self, step_desc: str) -> str:
        """Identify which layer is being fabricated in this step"""
        step_lower = step_desc.lower()
        
        if 'substrate' in step_lower or 'silicon' in step_lower:
            return 'silicon_substrate'
        elif 'oxide' in step_lower or 'sio2' in step_lower:
            return 'oxide_layer'
        elif 'nitride' in step_lower or 'si3n4' in step_lower:
            return 'nitride_layer'
        elif 'metal' in step_lower or any(material in step_lower for material in ['titanium', 'copper', 'gold', 'aluminum']):
            return 'metal_layer'
        else:
            return 'unknown_layer'

class GeminiWorkflowInterface:
    """
    Main interface for Gemini to generate wafer workflow visualizations
    """
    
    def __init__(self, output_base_dir: str = "gemini_workflows"):
        self.output_base_dir = output_base_dir
        self.parser = WorkflowParser()
        self.fabrication_engine = WaferFabricationEngine()
        
    def generate_wafer_workflow_images(self, 
                                    workflow_text: str,
                                    input_image_path: str,
                                    workflow_name: str = "workflow_1") -> Dict[str, str]:
        """
        Main function for Gemini to call - generates step-by-step images from text workflow and input image
        
        Args:
            workflow_text: Text workflow from Gemini (numbered steps)
            input_image_path: Path to input wafer image (for scaling reference)
            workflow_name: Name for this workflow
            
        Returns:
            Dictionary with status and file paths
        """
        
        try:
            # Create output directory
            output_dir = os.path.join(self.output_base_dir, workflow_name)
            os.makedirs(output_dir, exist_ok=True)
            
            # Parse the workflow
            steps = self.parser.parse_gemini_workflow(workflow_text)
            
            # Analyze input image for scaling reference
            input_scaling = self._analyze_input_image(input_image_path)
            
            # Generate step-by-step images using fabrication engine
            wafer_images = self._generate_step_by_step_images(steps, input_scaling)
            
            # Save all outputs
            output_files = self._save_workflow_outputs(wafer_images, steps, input_scaling, output_dir)
            
            # Create summary
            summary = self._create_workflow_summary(steps, input_scaling, output_files)
            
            return summary
            
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e),
                'workflow_name': workflow_name
            }
    
    def _analyze_input_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze input image for scaling reference"""
        if not os.path.exists(image_path):
            return {}
        
        image = cv2.imread(image_path)
        if image is None:
            return {}
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Basic analysis - could be enhanced
        height, width = image.shape[:2]
        return {
            'input_dimensions': {'width': width, 'height': height},
            'scaling_factor': min(width / 800, height / 600)  # Normalize to our standard size
        }
    
    def _generate_step_by_step_images(self, 
                                    steps: List[FabricationStep], 
                                    input_scaling: Dict) -> List[np.ndarray]:
        """Generate step-by-step images using fabrication engine"""
        
        images = []
        
        # Start with silicon substrate
        current_wafer = self.fabrication_engine.create_silicon_substrate()
        images.append(current_wafer.copy())
        
        # Apply each fabrication step
        for step in steps:
            current_wafer = self._apply_fabrication_step(current_wafer, step, input_scaling)
            images.append(current_wafer.copy())
        
        return images
    
    def _apply_fabrication_step(self, 
                              wafer: np.ndarray, 
                              step: FabricationStep, 
                              scaling: Dict) -> np.ndarray:
        """Apply a fabrication step using the fabrication engine"""
        
        if step.process_name.lower() == 'deposition':
            if step.materials:
                material = step.materials[0]
                thickness = int(50 * scaling.get('scaling_factor', 1.0))
                return self.fabrication_engine.deposit_layer(material, thickness, 'uniform')
        
        elif step.process_name.lower() == 'etching':
            if step.materials:
                material = step.materials[0]
                etch_depth = int(30 * scaling.get('scaling_factor', 1.0))
                return self.fabrication_engine.etch_layer(material, etch_depth, 'stripes')
        
        elif step.process_name.lower() == 'lithography':
            feature_size = int(20 * scaling.get('scaling_factor', 1.0))
            return self.fabrication_engine.apply_lithography('positive', 'stripes', feature_size)
        
        elif step.process_name.lower() == 'processing':
            if 'oxidation' in step.purpose.lower():
                return self.fabrication_engine.thermal_processing('oxidation', 1000, 60)
            elif 'annealing' in step.purpose.lower():
                return self.fabrication_engine.thermal_processing('annealing', 800, 30)
            else:
                return self.fabrication_engine.thermal_processing('oxidation', 1000, 60)
        
        # Default: return current wafer unchanged
        return wafer
    
    def _save_workflow_outputs(self, 
                             images: List[np.ndarray], 
                             steps: List[FabricationStep], 
                             scaling: Dict, 
                             output_dir: str) -> Dict[str, str]:
        """Save all workflow outputs"""
        
        output_files = {}
        
        # Save step-by-step images
        for i, image in enumerate(images):
            step_name = f"step_{i:03d}"
            if i > 0 and i-1 < len(steps):
                step_name = f"step_{i:03d}_{steps[i-1].process_name.lower()}"
            
            image_path = os.path.join(output_dir, f"{step_name}.png")
            cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            output_files[f"step_{i}"] = image_path
        
        # Save final image
        final_path = os.path.join(output_dir, "final_wafer.png")
        cv2.imwrite(final_path, cv2.cvtColor(images[-1], cv2.COLOR_RGB2BGR))
        output_files['final'] = final_path
        
        # Save layer stack information
        layer_info = self.fabrication_engine.get_layer_stack_info()
        layer_path = os.path.join(output_dir, "layer_stack.json")
        with open(layer_path, 'w') as f:
            json.dump(layer_info, f, indent=2)
        output_files['layer_stack'] = layer_path
        
        # Save workflow summary
        workflow_summary = {
            'steps': [
                {
                    'step_number': step.step_number,
                    'process_name': step.process_name,
                    'tool_name': step.tool_name,
                    'materials': step.materials,
                    'purpose': step.purpose
                }
                for step in steps
            ],
            'total_steps': len(steps),
            'materials_used': list(set([material for step in steps for material in step.materials])),
            'scaling_info': scaling
        }
        
        summary_path = os.path.join(output_dir, "workflow_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(workflow_summary, f, indent=2)
        output_files['summary'] = summary_path
        
        return output_files
    
    def _create_workflow_summary(self, 
                               steps: List[FabricationStep], 
                               scaling: Dict, 
                               output_files: Dict[str, str]) -> Dict[str, str]:
        """Create summary for Gemini"""
        
        return {
            'status': 'success',
            'workflow_name': os.path.basename(os.path.dirname(list(output_files.values())[0])),
            'total_steps': len(steps),
            'materials_used': list(set([material for step in steps for material in step.materials])),
            'output_directory': os.path.dirname(list(output_files.values())[0]),
            'files_generated': list(output_files.keys()),
            'final_image': output_files.get('final', ''),
            'layer_stack': output_files.get('layer_stack', ''),
            'workflow_summary': output_files.get('summary', ''),
            'message': f"Successfully generated {len(steps)} fabrication steps with realistic layer-by-layer wafer images"
        }

# Simplified function for Gemini to call
def generate_wafer_workflow_images(workflow_text: str, 
                                 input_image_path: str, 
                                 workflow_name: str = "workflow_1") -> Dict[str, str]:
    """
    Main function for Gemini to call - generates step-by-step wafer images
    
    Args:
        workflow_text: Text workflow from Gemini (numbered steps like "1. Step description")
        input_image_path: Path to input wafer image (for scaling reference)
        workflow_name: Name for this workflow
        
    Returns:
        Dictionary with status and file paths
    """
    
    interface = GeminiWorkflowInterface()
    return interface.generate_wafer_workflow_images(workflow_text, input_image_path, workflow_name)

# Example usage for testing
if __name__ == "__main__":
    # Test with example workflow
    example_workflow = """
    1. Silicon substrate preparation using standard cleaning procedures
    2. Thermal oxidation using AccuThermo AW 610M RTP to grow SiO2 layer
    3. Photolithography using MJB3 Mask Aligner (A) with positive photoresist
    4. Oxide etching using Oxford Pro 80 RIE with CHF3 gas
    5. Metal deposition using Lesker PVD 75 for titanium layer
    """
    
    # Test with a sample image
    test_image_path = "input_images/"
    
    if os.path.exists(test_image_path):
        result = generate_wafer_workflow_images(
            workflow_text=example_workflow,
            input_image_path=test_image_path,
            workflow_name="test_workflow"
        )
        print("Workflow generation result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Test image not found: {test_image_path}")
        print("Please provide a valid input image path for testing")

def validate_workflow_steps(steps):
    """Ensure step ordering is physically valid (e.g., etch before clean)."""
    required_order = ["deposition", "lithography", "etch", "clean"]
    positions = {s: next((i for i, step in enumerate(steps) if s in step.lower()), -1)
                 for s in required_order}
    return all(positions[required_order[i]] < positions[required_order[i+1]]
               for i in range(len(required_order)-1)
               if positions[required_order[i]] != -1 and positions[required_order[i+1]] != -1)
