"""
Utility functions for color manipulation - CW Transportadora
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color (#RRGGBB or #RGB) to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def adjust_color_brightness(hex_color: str, factor: float) -> str:
    """
    Adjust color brightness.
    factor > 1.0: Lighter
    factor < 1.0: Darker
    """
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return rgb_to_hex(r, g, b)


def blend_colors(hex_color1: str, hex_color2: str, ratio: float = 0.5) -> str:
    """
    Blend two colors.
    ratio: 0.0 = color1, 1.0 = color2, 0.5 = 50/50
    """
    r1, g1, b1 = hex_to_rgb(hex_color1)
    r2, g2, b2 = hex_to_rgb(hex_color2)
    
    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)
    
    return rgb_to_hex(r, g, b)
