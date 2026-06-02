"""
GestureCam Design System - Polished Dark Theme
Clean, minimal, professional
"""

import dearpygui.dearpygui as dpg

# =============================================================================
# COLOR PALETTE - Deep Dark Theme
# =============================================================================

# Primary - Soft indigo
PRIMARY = (99, 102, 242)
PRIMARY_LIGHT = (130, 133, 255)
PRIMARY_DARK = (70, 73, 210)
PRIMARY_GLOW = (99, 102, 242, 80)

# Backgrounds - Very dark
BG_MAIN = (8, 8, 14)  # #08080E - Almost black
BG_ELEVATED = (14, 14, 22)  # #0E0E16 - Slightly lighter

# Video containers
VIDEO_BG = (0, 0, 0, 255)  # Pure black

# Text
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (120, 120, 140)
TEXT_DIM = (80, 80, 100)

# Accent
SUCCESS = (52, 211, 153)  # Emerald
WARNING = (251, 191, 36)  # Amber
ERROR = (248, 113, 113)  # Red

# Borders
BORDER_SUBTLE = (30, 30, 45)
BORDER_VISIBLE = (50, 50, 70)

# =============================================================================
# SPACING
# =============================================================================

RADIUS_SM = 6
RADIUS_MD = 10
RADIUS_LG = 14
RADIUS_XL = 18

# =============================================================================
# THEMES
# =============================================================================


def setup_main_theme():
    """Apply polished dark theme"""

    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            # Deep dark backgrounds
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BG_MAIN)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (0, 0, 0, 0))  # Transparent
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, BG_ELEVATED)

            # Text
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_WHITE)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, TEXT_DIM)

            # Clean buttons - subtle dark
            dpg.add_theme_color(dpg.mvThemeCol_Button, (25, 25, 38))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (35, 35, 52))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (45, 45, 65))

            # Frames
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (20, 20, 32))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (28, 28, 42))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (35, 35, 52))

            # Slider
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, PRIMARY)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, PRIMARY_LIGHT)

            # Checkbox
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, PRIMARY)

            # Headers
            dpg.add_theme_color(dpg.mvThemeCol_Header, (25, 25, 38))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (35, 35, 52))
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (45, 45, 65))

            # Borders - very subtle
            dpg.add_theme_color(dpg.mvThemeCol_Separator, BORDER_SUBTLE)
            dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))

            # Smooth rounded corners
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, RADIUS_MD)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, RADIUS_LG)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, RADIUS_LG)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, RADIUS_MD)

            # Comfortable padding
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 10)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 20)

    dpg.bind_theme(theme)
    return theme


def create_video_container_theme():
    """Theme for original video"""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, VIDEO_BG)
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SUBTLE)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, RADIUS_XL)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
    return theme


def create_processed_video_theme():
    """Theme for processed video - primary glow"""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, VIDEO_BG)
            dpg.add_theme_color(dpg.mvThemeCol_Border, PRIMARY)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 2)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, RADIUS_XL)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
    return theme


def create_mode_button_theme(active: bool = False):
    """Mode button - ghost style with purple border when active"""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvButton):
            if active:
                # Active: transparent bg with purple border
                dpg.add_theme_color(dpg.mvThemeCol_Button, (30, 25, 45))  # Slight purple tint
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (40, 35, 60))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (50, 45, 75))
                dpg.add_theme_color(dpg.mvThemeCol_Border, PRIMARY)  # Purple border!
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_WHITE)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)  # Visible border
            else:
                # Inactive: subtle ghost look
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (30, 30, 45))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (40, 40, 58))
                dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_VISIBLE)
                dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_MUTED)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, RADIUS_MD)
    return theme


def create_primary_button_theme():
    """Primary action button"""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, PRIMARY)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, PRIMARY_LIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, PRIMARY_DARK)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, RADIUS_MD)
    return theme


def create_ghost_button_theme():
    """Ghost/outline button"""
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (20, 20, 32))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (30, 30, 45))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (40, 40, 58))
            dpg.add_theme_color(dpg.mvThemeCol_Border, BORDER_SUBTLE)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, RADIUS_MD)
    return theme
