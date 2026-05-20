from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size=81, color="#999999", bg_color=None, icon_type="home"):
    """
    Create WeChat Mini Program icon
    
    Args:
        size: Icon size
        color: Icon color
        bg_color: Background color (None for transparent)
        icon_type: Icon type (home/camera)
    """
    # Create image (RGBA mode supports transparent background)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate center and radius
    center = size // 2
    radius = size // 3
    
    if icon_type == "home":
        # Draw house icon
        # Roof triangle
        roof_points = [
            (center - radius, center - radius // 2),
            (center, center - radius),
            (center + radius, center - radius // 2)
        ]
        draw.polygon(roof_points, fill=color)
        
        # House body
        house_left = center - radius + 5
        house_top = center - radius // 2
        house_width = 2 * radius - 10
        house_height = radius + 5
        
        draw.rectangle([house_left, house_top, house_left + house_width, house_top + house_height], fill=color)
        
        # Door
        door_width = house_width // 3
        door_height = house_height // 2
        door_left = center - door_width // 2
        door_top = house_top + house_height - door_height
        draw.rectangle([door_left, door_top, door_left + door_width, door_top + door_height], fill=(255,255,255,255))
        
    elif icon_type == "camera":
        # Draw camera icon
        # Camera body
        cam_width = radius * 2
        cam_height = radius * 1.5
        cam_left = center - cam_width // 2
        cam_top = center - cam_height // 2
        
        draw.rectangle([cam_left, cam_top, cam_left + cam_width, cam_top + cam_height], fill=color)
        
        # Lens outer circle
        lens_radius = radius // 1.5
        draw.ellipse([center - lens_radius, center - lens_radius, center + lens_radius, center + lens_radius], 
                     fill=(255, 255, 255, 255))
        
        # Lens inner circle
        inner_radius = lens_radius * 0.6
        draw.ellipse([center - inner_radius, center - inner_radius, center + inner_radius, center + inner_radius], 
                     fill=color)
        
        # Flash
        flash_size = 8
        flash_left = cam_left + cam_width - flash_size - 5
        flash_top = cam_top + 5
        draw.rectangle([flash_left, flash_top, flash_left + flash_size, flash_top + flash_size], 
                     fill=(255, 255, 255, 255))
    
    return img

def main():
    # Icon directory
    icons_dir = os.path.join(os.path.dirname(__file__), 'miniprogram', 'images')
    os.makedirs(icons_dir, exist_ok=True)
    
    # Color configuration
    inactive_color = "#999999"  # Inactive state
    active_color = "#4F81FE"    # Active state
    
    # Generate 4 icons
    icons = [
        ("home.png", inactive_color, "home"),
        ("home-active.png", active_color, "home"),
        ("camera.png", inactive_color, "camera"),
        ("camera-active.png", active_color, "camera")
    ]
    
    for filename, color, icon_type in icons:
        icon = create_icon(size=81, color=color, icon_type=icon_type)
        filepath = os.path.join(icons_dir, filename)
        icon.save(filepath, 'PNG')
        print(f"[OK] Generated: {filepath}")
    
    print("\n[SUCCESS] All icons generated successfully!")

if __name__ == "__main__":
    main()