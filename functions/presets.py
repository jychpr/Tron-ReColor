# functions/presets.py

presets = {
    "ares": {
        "white_balance": {
            "temperature": 7500,  # Shift toward warm
            "tint": 40            # Extra magenta push
        },
        "tone": {
            # Keep it fairly dark/contrasty
            "exposure": -0.2,    
            "contrast": 70,      
            "highlights": 0,
            "shadows": 0,
            "whites": 0,
            "blacks": 0
        },
        "presence": {
            "texture": 30,
            "clarity": 50,       # Sharp details for neon look
            "dehaze": 0
        },
        "vibrance": 15,          # Mild vibrance
        "saturation": 20,        # Overall saturation boost
        "hsl": {
            "hue": {
                # Slight shifts: push everything more toward red
                "red": 0,
                "orange": -20,
                "yellow": -40,
                "green": -60,
                "aqua": -60,
                "blue": -60,
                "purple": -60,
                "magenta": -40
            },
            "saturation": {
                # Intensify reds, drain other colors
                "red": 80,
                "orange": -40,
                "yellow": -90,
                "green": -100,
                "aqua": -100,
                "blue": -100,
                "purple": -70,
                "magenta": -70
            },
            "luminance": {
                # Brighten reds slightly, keep other channels dark
                "red": 20,
                "orange": 0,
                "yellow": -30,
                "green": 0,
                "aqua": 0,
                "blue": -30,
                "purple": -30,
                "magenta": 0
            }
        },
        "tone_curves": {
            # A high-contrast S-curve
            "rgb": [
                [0, 0], [32, 10], [128, 128], [220, 245], [255, 255]
            ],
            # Extra midtone lift in red, while protecting shadows/highlights
            "red": [
                [0, 0], [60, 50], [128, 180], [255, 255]
            ],
            # Keep green/blue near default or slightly lowered
            "green": [
                [0, 0], [128, 128], [255, 255]
            ],
            "blue": [
                [0, 0], [128, 128], [255, 255]
            ]
        },
        "color_grading": {
            # Push shadows/midtones/highlights toward hue=0 (pure red).
            # Strong shadow saturation intensifies the red in dark areas.
            "shadows": {
                "hue": 0,
                "saturation": 60,
                "luminance": -20
            },
            "midtones": {
                "hue": 0,
                "saturation": 40,
                "luminance": 0
            },
            "highlights": {
                "hue": 0,
                "saturation": 20,
                "luminance": 0
            },
            "global": {
                "hue": 0,
                "saturation": 10,
                "luminance": 0
            },
            "blending": 0,
            "balance": 0
        },
        "grain": {
            # Slight grain can add some film-like grit
            "amount": 5,
            "size": 20,
            "roughness": 50
        },
        "calibration": {
            # Tilt overall color toward red by reducing green/blue
            "shadows_tint": -5,
            "red_primary": {
                "hue": 0,
                "saturation": 40  # Boost red primary
            },
            "green_primary": {
                "hue": 0,
                "saturation": -40
            },
            "blue_primary": {
                "hue": 0,
                "saturation": -40
            }
        }
    },

    "legacy": {
        "white_balance": {
            "temperature": 4000,  # Cooler color temperature
            "tint": -10           # Slight green cast
        },
        "tone": {
            "exposure": -0.1,     # Darken slightly for moody look
            "contrast": 50,       # Boost contrast
            "highlights": 0, 
            "shadows": 0, 
            "whites": 0, 
            "blacks": 0
        },
        "presence": {
            "texture": 30,
            "clarity": 40,        # Increase clarity for sharpness
            "dehaze": 0
        },
        "vibrance": 15,           # Boost color vibrance
        "saturation": 10,         # Mild overall saturation
        "hsl": {
            "hue": {
                # Slightly shift warm hues to be more cool or neutral
                "red": -20,
                "orange": -30,
                "yellow": -50,
                # Shift green & aqua more toward teal
                "green": -80,    
                "aqua": -20,
                # Shift blue closer to teal
                "blue": -40,
                "purple": -20,
                "magenta": -20
            },
            "saturation": {
                # Heavily reduce warm colors so teal stands out
                "red": -80,
                "orange": -90,
                "yellow": -90,
                "green": -60,
                "aqua": 50,    # Boost aqua
                "blue": 60,    # Boost blue
                "purple": -50,
                "magenta": -50
            },
            "luminance": {
                # Brighten aquas/blues so they pop
                "red": 0,
                "orange": 0,
                "yellow": 0,
                "green": 0,
                "aqua": 20,
                "blue": 20,
                "purple": 0,
                "magenta": 0
            }
        },
        "tone_curves": {
            "rgb": [
                # A gentle S-curve for contrast
                [0, 0], [50, 30], [128, 128], [205, 230], [255, 255]
            ],
            "red": [
                # Slightly lift shadows, keep highlights
                [0, 0], [128, 115], [255, 255]
            ],
            "green": [
                # Subtle adjustments to green
                [0, 0], [128, 128], [255, 255]
            ],
            "blue": [
                # Lift the shadows in blue for a cooler cast
                [0, 10], [128, 140], [255, 255]
            ]
        },
        "color_grading": {
            # Push shadows, midtones, and highlights into teal
            "shadows": {
                "hue": 180,       # Hue ~180° is cyan/teal
                "saturation": 40,
                "luminance": 0
            },
            "midtones": {
                "hue": 180,
                "saturation": 30,
                "luminance": 0
            },
            "highlights": {
                "hue": 180,
                "saturation": 20,
                "luminance": 0
            },
            "global": {
                "hue": 180,
                "saturation": 10,
                "luminance": 0
            },
            "blending": 0,
            "balance": 0
        },
        "grain": {
            "amount": 5,
            "size": 25,
            "roughness": 50
        },
        "calibration": {
            # Slightly shift green/blue primaries for a cooler feel
            "shadows_tint": -5,
            "red_primary": {
                "hue": 0,
                "saturation": -20
            },
            "green_primary": {
                "hue": 10,
                "saturation": -20
            },
            "blue_primary": {
                "hue": 30,
                "saturation": 20
            }
        }
    }

}
