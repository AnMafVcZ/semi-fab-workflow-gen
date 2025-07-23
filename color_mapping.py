# Semiconductor Material Color Mapping
# RGB values for different materials in wafer cross-sections

# Basic RGB color mapping
MATERIAL_COLORS = {
    'silicon': (128, 128, 128),     # Gray (silicon substrate)
    'sio2': (0, 100, 200),          # Blue (oxide layer)
    'si3n4': (0, 150, 0),           # Green (nitride layer)
    'titanium': (255, 140, 0),      # Orange (titanium)
    'copper': (139, 69, 19),        # Brown (copper)
    'gold': (255, 215, 0),          # Yellow (gold)
    'aluminum': (169, 169, 169),    # Dark gray (aluminum)
    'empty': (255, 255, 255)        # White (empty space)
}

# Enhanced color information with names and hex values
MATERIAL_COLOR_INFO = {
    'silicon': {
        'rgb': (128, 128, 128),
        'name': 'Gray',
        'hex': '#808080',
        'description': 'Silicon substrate - appears as gray'
    },
    'sio2': {
        'rgb': (0, 100, 200),
        'name': 'Blue',
        'hex': '#0064C8',
        'description': 'Silicon dioxide (oxide) - appears as blue'
    },
    'si3n4': {
        'rgb': (0, 150, 0),
        'name': 'Green',
        'hex': '#009600',
        'description': 'Silicon nitride - appears as green'
    },
    'titanium': {
        'rgb': (255, 140, 0),
        'name': 'Orange',
        'hex': '#FF8C00',
        'description': 'Titanium - appears as orange'
    },
    'copper': {
        'rgb': (139, 69, 19),
        'name': 'Brown',
        'hex': '#8B4513',
        'description': 'Copper - appears as brown'
    },
    'gold': {
        'rgb': (255, 215, 0),
        'name': 'Yellow',
        'hex': '#FFD700',
        'description': 'Gold - appears as yellow'
    },
    'aluminum': {
        'rgb': (169, 169, 169),
        'name': 'Dark Gray',
        'hex': '#A9A9A9',
        'description': 'Aluminum - appears as dark gray'
    },
    'empty': {
        'rgb': (255, 255, 255),
        'name': 'White',
        'hex': '#FFFFFF',
        'description': 'Empty space/etched areas - appears as white'
    }
}

# Material IDs for labeling
MATERIAL_IDS = {
    'silicon': 1,
    'sio2': 2,
    'si3n4': 3,
    'titanium': 4,
    'copper': 5,
    'gold': 6,
    'aluminum': 7,
    'empty': 0  # Background/empty space
} 
# Extended material palette for high-res devices
ADVANCED_MATERIALS = {
    "tungsten": (100, 100, 120),
    "tungsten_silicide": (90, 90, 110),
    "silicon_nitride": (210, 230, 255),
    "low_k_dielectric": (195, 215, 245),
    "copper": (184, 115, 51),
}
