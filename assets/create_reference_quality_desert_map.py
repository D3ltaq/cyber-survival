import pygame
import random
import math

def create_reference_quality_desert_map():
    """Create a desert map that matches the quality of the reference images"""
    MAP_WIDTH = 4800
    MAP_HEIGHT = 3200
    
    pygame.init()
    surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    
    # Desert color palette
    DESERT_COLORS = {
        'sand': (220, 190, 140),
        'dark_sand': (200, 170, 120),
        'rocky': (180, 160, 130),
        'hard_ground': (160, 140, 110),
        'bush_area': (190, 180, 120),
    }
    
    print("Creating reference-quality desert map...")
    
    # Generate base terrain
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            height = simple_noise(x, y, 300.0) * 0.5
            height += simple_noise(x, y, 150.0) * 0.3
            height += simple_noise(x, y, 75.0) * 0.2
            
            if height < -0.2:
                terrain = 'hard_ground'
            elif height < 0.0:
                terrain = 'dark_sand'
            elif height < 0.2:
                terrain = 'sand'
            elif height < 0.4:
                terrain = 'bush_area'
            else:
                terrain = 'rocky'
            
            base_color = DESERT_COLORS[terrain]
            pixel_variation = random.randint(-8, 8)
            final_color = tuple(max(0, min(255, c + pixel_variation)) for c in base_color)
            surface.set_at((x, y), final_color)
        
        if y % 400 == 0:
            print(f"Progress: {y/MAP_HEIGHT*100:.1f}%")
    
    print("Adding reference-quality features...")
    add_reference_quality_features(surface)
    
    return surface

def simple_noise(x, y, scale=100.0):
    return (math.sin(x / scale) + math.sin(y / scale) + 
            math.sin((x + y) / scale) + math.sin((x - y) / scale)) / 4.0

def add_reference_quality_features(surface):
    """Add features that match the reference image quality"""
    width, height = surface.get_size()
    grid_size = 120  # Even larger spacing for detailed features
    
    for y in range(0, height, grid_size):
        for x in range(0, width, grid_size):
            actual_x = x + random.randint(-40, 40)
            actual_y = y + random.randint(-40, 40)
            
            rand = random.random()
            
            if rand < 0.15:  # 15% chance for rock clusters
                draw_reference_rock_cluster(surface, actual_x, actual_y)
            elif rand < 0.25:  # 10% chance for bushes
                draw_reference_bush(surface, actual_x, actual_y)
            elif rand < 0.30:  # 5% chance for cacti
                draw_reference_cactus(surface, actual_x, actual_y)

def draw_reference_rock_cluster(surface, x, y):
    """Draw rock clusters that match the reference images - multiple rounded rocks together"""
    width, height = surface.get_size()
    
    # Rock colors with more detailed shading (like reference)
    rock_colors = {
        'highlight': (200, 180, 160),    # Brightest highlight
        'light': (170, 150, 130),        # Light areas
        'medium': (140, 120, 100),       # Medium tone
        'dark': (110, 90, 70),           # Shadow areas
        'deep_shadow': (80, 60, 40)      # Deepest shadows
    }
    
    # Create cluster of 2-5 rocks like in reference
    num_rocks = random.randint(2, 5)
    cluster_size = random.randint(25, 40)
    
    for rock_idx in range(num_rocks):
        # Position rocks within cluster
        angle = (rock_idx * 2 * math.pi / num_rocks) + random.uniform(-0.5, 0.5)
        distance = random.randint(0, cluster_size // 3)
        rock_x = x + int(distance * math.cos(angle))
        rock_y = y + int(distance * math.sin(angle))
        
        # Individual rock size
        rock_w = random.randint(12, 20)
        rock_h = random.randint(10, 16)
        
        # Draw individual rock with proper shading
        draw_individual_rock(surface, rock_x, rock_y, rock_w, rock_h, rock_colors)

def draw_individual_rock(surface, x, y, rock_w, rock_h, colors):
    """Draw a single rock with reference-quality shading"""
    width, height = surface.get_size()
    
    center_x = rock_w / 2
    center_y = rock_h / 2
    
    for dy in range(rock_h):
        for dx in range(rock_w):
            px, py = x + dx, y + dy
            if 0 <= px < width and 0 <= py < height:
                # Calculate distance from center for roundness
                distance = math.sqrt((dx - center_x)**2 + (dy - center_y)**2)
                max_distance = min(rock_w, rock_h) / 2
                
                if distance < max_distance:
                    # Calculate lighting (top-left light source)
                    light_factor = (dx / rock_w) + (dy / rock_h)  # 0 = top-left, 2 = bottom-right
                    edge_factor = distance / max_distance  # 0 = center, 1 = edge
                    
                    # Determine color based on lighting and position
                    if light_factor < 0.4 and edge_factor < 0.7:
                        color = colors['highlight']
                    elif light_factor < 0.8 and edge_factor < 0.8:
                        color = colors['light']
                    elif light_factor < 1.2:
                        color = colors['medium']
                    elif light_factor < 1.6:
                        color = colors['dark']
                    else:
                        color = colors['deep_shadow']
                    
                    # Add texture noise
                    variation = random.randint(-8, 8)
                    final_color = tuple(max(0, min(255, c + variation)) for c in color)
                    surface.set_at((px, py), final_color)

def draw_reference_bush(surface, x, y):
    """Draw bushes that match the reference complexity"""
    width, height = surface.get_size()
    
    bush_type = random.choice(['thorny_scrub', 'desert_sage', 'prickly_bush'])
    
    if bush_type == 'thorny_scrub':
        # Brown/red thorny bush like in reference
        colors = {
            'branch': (80, 50, 30),
            'foliage_dark': (100, 60, 40),
            'foliage_med': (120, 80, 60),
            'foliage_light': (140, 100, 80),
            'highlight': (160, 120, 100)
        }
        bush_size = random.randint(16, 24)
    elif bush_type == 'desert_sage':
        # Green-gray sage bush
        colors = {
            'branch': (60, 70, 50),
            'foliage_dark': (80, 100, 70),
            'foliage_med': (100, 120, 90),
            'foliage_light': (120, 140, 110),
            'highlight': (140, 160, 130)
        }
        bush_size = random.randint(14, 20)
    else:  # prickly_bush
        # Yellow-green prickly bush
        colors = {
            'branch': (70, 60, 40),
            'foliage_dark': (120, 120, 60),
            'foliage_med': (140, 140, 80),
            'foliage_light': (160, 160, 100),
            'highlight': (180, 180, 120)
        }
        bush_size = random.randint(12, 18)
    
    # Draw complex bush structure
    draw_complex_bush_structure(surface, x, y, bush_size, colors)

def draw_complex_bush_structure(surface, x, y, bush_size, colors):
    """Draw a bush with branching structure like the reference"""
    width, height = surface.get_size()
    
    # Create main bush body
    center_x = bush_size // 2
    center_y = bush_size // 2
    
    # Draw base structure
    for dy in range(bush_size):
        for dx in range(bush_size):
            px, py = x + dx, y + dy
            if 0 <= px < width and 0 <= py < height:
                distance = math.sqrt((dx - center_x)**2 + (dy - center_y)**2)
                
                # Create irregular bush shape with noise
                noise_val = simple_noise(px * 0.3, py * 0.3, 8)
                max_distance = (bush_size / 2) + noise_val * 3
                
                if distance < max_distance and random.random() < 0.7:
                    # Determine foliage density and color
                    density_factor = 1 - (distance / max_distance)
                    
                    if density_factor > 0.8:
                        color = colors['highlight']
                    elif density_factor > 0.6:
                        color = colors['foliage_light']
                    elif density_factor > 0.4:
                        color = colors['foliage_med']
                    else:
                        color = colors['foliage_dark']
                    
                    surface.set_at((px, py), color)
    
    # Add branch structure
    num_branches = random.randint(3, 6)
    for i in range(num_branches):
        angle = random.uniform(0, 2 * math.pi)
        branch_length = random.randint(bush_size // 3, bush_size // 2)
        
        for j in range(branch_length):
            branch_x = x + center_x + int(j * math.cos(angle))
            branch_y = y + center_y + int(j * math.sin(angle))
            
            if 0 <= branch_x < width and 0 <= branch_y < height:
                if random.random() < 0.8:  # Some gaps in branches
                    surface.set_at((branch_x, branch_y), colors['branch'])

def draw_reference_cactus(surface, x, y):
    """Draw cacti that match the reference detail level"""
    width, height = surface.get_size()
    
    cactus_type = random.choice(['detailed_saguaro', 'barrel_with_ribs', 'prickly_pear_cluster'])
    
    # Cactus colors with proper green tones
    cactus_colors = {
        'highlight': (160, 200, 140),
        'light': (120, 160, 100),
        'medium': (90, 130, 70),
        'dark': (60, 100, 40),
        'deep_shadow': (40, 80, 20),
        'spine': (220, 200, 160),
        'flower': (200, 100, 120)  # For flowering cacti
    }
    
    if cactus_type == 'detailed_saguaro':
        draw_detailed_saguaro(surface, x, y, cactus_colors)
    elif cactus_type == 'barrel_with_ribs':
        draw_barrel_with_ribs(surface, x, y, cactus_colors)
    else:
        draw_prickly_pear_cluster(surface, x, y, cactus_colors)

def draw_detailed_saguaro(surface, x, y, colors):
    """Draw a saguaro with ribs and proper detail"""
    width, height = surface.get_size()
    
    trunk_width = random.randint(6, 10)
    trunk_height = random.randint(25, 35)
    
    # Draw main trunk with vertical ribs
    for dy in range(trunk_height):
        for dx in range(trunk_width):
            px, py = x + dx, y + dy
            if 0 <= px < width and 0 <= py < height:
                # Create ribbed effect
                rib_position = dx % 3  # 3-pixel rib pattern
                
                # Base shading (left light, right dark)
                if dx < trunk_width * 0.3:
                    base_color = colors['light']
                elif dx > trunk_width * 0.7:
                    base_color = colors['dark']
                else:
                    base_color = colors['medium']
                
                # Modify for ribs
                if rib_position == 0:  # Rib highlight
                    color = colors['highlight'] if base_color == colors['light'] else colors['light']
                elif rib_position == 2:  # Rib shadow
                    color = colors['dark'] if base_color == colors['medium'] else colors['deep_shadow']
                else:
                    color = base_color
                
                surface.set_at((px, py), color)
    
    # Add arms with proper attachment
    if trunk_height > 20 and random.random() < 0.8:
        arm_y = random.randint(trunk_height // 3, 2 * trunk_height // 3)
        
        # Left arm
        if random.random() < 0.7:
            draw_cactus_arm(surface, x - 1, y + arm_y, 'left', colors)
        
        # Right arm
        if random.random() < 0.7:
            draw_cactus_arm(surface, x + trunk_width, y + arm_y, 'right', colors)
    
    # Add spines along ribs
    add_detailed_spines(surface, x, y, trunk_width, trunk_height, colors['spine'])

def draw_cactus_arm(surface, x, y, direction, colors):
    """Draw a cactus arm with proper connection"""
    width, height = surface.get_size()
    
    arm_length = random.randint(8, 15)
    arm_width = random.randint(4, 6)
    arm_height = random.randint(10, 18)
    
    # Horizontal part
    for dx in range(arm_length):
        for dy in range(arm_width):
            if direction == 'left':
                px, py = x - dx, y + dy
            else:
                px, py = x + dx, y + dy
            
            if 0 <= px < width and 0 <= py < height:
                # Shading for horizontal arm
                if dy < arm_width // 2:
                    color = colors['light']
                else:
                    color = colors['dark']
                surface.set_at((px, py), color)
    
    # Vertical part
    arm_base_x = x - arm_length if direction == 'left' else x + arm_length
    for dy in range(arm_height):
        for dx in range(arm_width):
            px, py = arm_base_x + dx, y + dy - arm_height
            if 0 <= px < width and 0 <= py < height:
                # Vertical arm shading
                if dx < arm_width * 0.4:
                    color = colors['light']
                elif dx > arm_width * 0.6:
                    color = colors['dark']
                else:
                    color = colors['medium']
                surface.set_at((px, py), color)

def draw_barrel_with_ribs(surface, x, y, colors):
    """Draw a barrel cactus with prominent ribs"""
    width, height = surface.get_size()
    
    cactus_size = random.randint(12, 18)
    center_x = cactus_size // 2
    center_y = cactus_size // 2
    
    for dy in range(cactus_size):
        for dx in range(cactus_size):
            px, py = x + dx, y + dy
            if 0 <= px < width and 0 <= py < height:
                distance = math.sqrt((dx - center_x)**2 + (dy - center_y)**2)
                
                if distance < cactus_size // 2:
                    # Calculate angle for ribs
                    angle = math.atan2(dy - center_y, dx - center_x)
                    rib_number = int((angle + math.pi) / (math.pi / 4))  # 8 ribs
                    
                    # Base color from lighting
                    if dx < cactus_size * 0.3:
                        base_color = colors['light']
                    elif dx > cactus_size * 0.7:
                        base_color = colors['dark']
                    else:
                        base_color = colors['medium']
                    
                    # Modify for ribs
                    if rib_number % 2 == 0:  # Rib peaks
                        color = colors['highlight'] if base_color == colors['light'] else colors['light']
                    else:  # Rib valleys
                        color = colors['dark'] if base_color == colors['medium'] else colors['deep_shadow']
                    
                    surface.set_at((px, py), color)
    
    # Add flower on top sometimes
    if random.random() < 0.3:
        flower_x = x + center_x
        flower_y = y + 2
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) < 3:
                    px, py = flower_x + dx, flower_y + dy
                    if 0 <= px < width and 0 <= py < height:
                        surface.set_at((px, py), colors['flower'])

def draw_prickly_pear_cluster(surface, x, y, colors):
    """Draw a cluster of prickly pear segments"""
    width, height = surface.get_size()
    
    segments = random.randint(3, 6)
    
    for i in range(segments):
        seg_x = x + i * 8 + random.randint(-3, 3)
        seg_y = y + random.randint(-4, 4)
        seg_width = random.randint(10, 14)
        seg_height = random.randint(8, 12)
        
        # Draw oval segment with proper shading
        center_x = seg_width / 2
        center_y = seg_height / 2
        
        for dy in range(seg_height):
            for dx in range(seg_width):
                px, py = seg_x + dx, seg_y + dy
                if 0 <= px < width and 0 <= py < height:
                    # Oval shape
                    ellipse_dist = ((dx - center_x) / center_x)**2 + ((dy - center_y) / center_y)**2
                    
                    if ellipse_dist < 1:
                        # Shading for flat cactus pad
                        if dx < seg_width * 0.3:
                            color = colors['light']
                        elif dx > seg_width * 0.7:
                            color = colors['dark']
                        else:
                            color = colors['medium']
                        
                        surface.set_at((px, py), color)
        
        # Add spines to segment
        add_segment_spines(surface, seg_x, seg_y, seg_width, seg_height, colors['spine'])

def add_detailed_spines(surface, x, y, cactus_width, cactus_height, spine_color):
    """Add detailed spines along cactus ribs"""
    width, height = surface.get_size()
    
    # Add spines in vertical lines (following ribs)
    for rib in range(0, cactus_width, 3):  # Every 3 pixels (rib spacing)
        for spine_y in range(0, cactus_height, 4):  # Every 4 pixels vertically
            spine_x = x + rib
            spine_py = y + spine_y
            
            if 0 <= spine_x < width and 0 <= spine_py < height:
                # Small spine cluster
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        px, py = spine_x + dx, spine_py + dy
                        if 0 <= px < width and 0 <= py < height and random.random() < 0.6:
                            surface.set_at((px, py), spine_color)

def add_segment_spines(surface, x, y, seg_width, seg_height, spine_color):
    """Add spines to prickly pear segments"""
    width, height = surface.get_size()
    
    # Add spine clusters across the segment
    for spine_x in range(3, seg_width - 3, 4):
        for spine_y in range(3, seg_height - 3, 4):
            px, py = x + spine_x, y + spine_y
            if 0 <= px < width and 0 <= py < height:
                # Small spine cluster
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        spx, spy = px + dx, py + dy
                        if 0 <= spx < width and 0 <= spy < height and random.random() < 0.5:
                            surface.set_at((spx, spy), spine_color)

def main():
    print("Creating reference-quality desert map...")
    print("Implementing detailed features from reference images:")
    print("- Multi-rock clusters with proper shading")
    print("- Complex bush structures with branching")
    print("- Detailed cacti with ribs, spines, and flowers")
    print("- Professional pixel art techniques")
    
    desert_map = create_reference_quality_desert_map()
    
    filename = "pixel_art_map_desert_reference_quality.png"
    pygame.image.save(desert_map, filename)
    
    print(f"\nReference-quality desert map saved as: {filename}")
    print("This version matches the complexity and detail of your reference images!")
    print("\nTo use it, run: mv pixel_art_map_desert_reference_quality.png pixel_art_map.png")

if __name__ == "__main__":
    main() 