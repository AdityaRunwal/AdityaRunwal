import os
import sys
import math
from PIL import Image, ImageEnhance, ImageFilter

def find_source_image():
    search_paths = [
        "assets/profile-photo.png",
        "assets/profile.png",
        "assets/photo.png",
        "photo.jpg", "photo.png", "photo.jpeg", "photo.webp",
        "portrait.jpg", "portrait.png", "portrait.jpeg",
        "profile.jpg", "profile.png", "profile.jpeg",
        "avatar.jpg", "avatar.png", "avatar.jpeg",
        "data/photo.jpg", "data/photo.png", "data/portrait.jpg"
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    return None

def process_image(image_path, target_cols=60, target_rows=52):
    try:
        img = Image.open(image_path)
        w, h = img.size
        
        # Smart crop to center head and shoulders into a square aspect ratio
        crop_box = (int(w * 0.04), int(h * 0.02), int(w * 0.96), int(h * 0.88))
        img_cropped = img.crop(crop_box)
        
        cw, ch = img_cropped.size
        min_dim = min(cw, ch)
        left = (cw - min_dim) // 2
        top = (ch - min_dim) // 2
        img_sq = img_cropped.crop((left, top, left + min_dim, top + min_dim))
        
        # Resize to grid dimensions
        img_grid = img_sq.resize((target_cols, target_rows), Image.Resampling.LANCZOS)
        
        # Edge map for sharp facial feature contours (eyes, mustache, hair texture)
        img_gray = img_sq.convert("L")
        img_edges = img_gray.filter(ImageFilter.FIND_EDGES)
        img_edges = ImageEnhance.Contrast(img_edges).enhance(2.5)
        img_edges_grid = img_edges.resize((target_cols, target_rows), Image.Resampling.BILINEAR)
        
        grid = []
        for r in range(target_rows):
            row_data = []
            for c in range(target_cols):
                r_val, g_val, b_val = img_grid.getpixel((c, r))[:3]
                luma = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
                edge = img_edges_grid.getpixel((c, r))
                
                # Check for white photo background
                is_bg = (r_val > 230 and g_val > 230 and b_val > 230)
                
                row_data.append({
                    'r': r_val, 'g': g_val, 'b': b_val,
                    'luma': luma,
                    'edge': edge,
                    'is_bg': is_bg
                })
            grid.append(row_data)
        return grid
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def generate_default_face_pixels(cols=60, rows=52):
    """Generates a high-contrast dithered face matrix if no photo is provided."""
    grid = []
    cx, cy = cols / 2.0, rows / 2.1
    
    for r in range(rows):
        row_data = []
        for c in range(cols):
            dx = (c - cx) / (cols * 0.42)
            dy = (r - cy) / (rows * 0.46)
            dist_head = dx*dx + dy*dy
            
            intensity = 0
            is_bg = True
            
            if dist_head <= 1.0:
                is_bg = False
                intensity = 130 + int(70 * (1.0 - dist_head))
                if r < rows * 0.28:
                    intensity = 210
                elif r < rows * 0.38:
                    intensity = 170
                elif rows * 0.40 <= r <= rows * 0.47:
                    if (cols*0.28 <= c <= cols*0.42) or (cols*0.58 <= c <= cols*0.72):
                        intensity = 240 if (cols*0.33 <= c <= cols*0.37 or cols*0.63 <= c <= cols*0.67) else 60
                elif rows * 0.48 <= r <= rows * 0.60:
                    if cols * 0.45 <= c <= cols * 0.55:
                        intensity = 200
                elif rows * 0.65 <= r <= rows * 0.72:
                    if cols * 0.36 <= c <= cols * 0.64:
                        intensity = 220 if rows * 0.68 <= r <= rows * 0.70 else 80
            elif r >= rows * 0.76:
                dx_neck = (c - cx) / (cols * 0.6)
                if dx_neck*dx_neck + (r/rows - 0.9)**2 <= 0.25:
                    is_bg = False
                    intensity = 160
            
            row_data.append({
                'r': intensity, 'g': intensity, 'b': intensity,
                'luma': intensity,
                'edge': 0,
                'is_bg': is_bg
            })
        grid.append(row_data)
    return grid

def render_svg(grid):
    WIDTH = 370
    HEIGHT = 330
    OFFSET_X = 20
    OFFSET_Y = 48
    
    rows = len(grid)
    cols = len(grid[0])
    
    cell_w = (WIDTH - 2 * OFFSET_X) / cols
    cell_h = (HEIGHT - OFFSET_Y - 14) / rows
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    svg.append('<style>')
    svg.append('  .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1px; }')
    svg.append('  .header-bg { fill: #161b22; }')
    svg.append('  .header-title { font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, monospace; font-size: 11px; font-weight: 600; fill: #8b949e; }')
    svg.append('  .dot { transition: fill 0.15s ease, opacity 0.15s ease; }')
    svg.append('  .dot:hover { fill: #ffffff !important; opacity: 1.0 !important; }')
    svg.append('  .row-g { opacity: 0; animation: revealRow 0.12s ease-out forwards; }')
    svg.append('  @keyframes revealRow { from { opacity: 0; } to { opacity: 1; } }')
    svg.append('</style>')

    # Background Card
    svg.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" class="bg"/>')

    # Header Bar
    svg.append(f'<path d="M 0 10 A 10 10 0 0 1 10 0 L {WIDTH-10} 0 A 10 10 0 0 1 {WIDTH} 10 L {WIDTH} 36 L 0 36 Z" class="header-bg"/>')
    svg.append(f'<line x1="0" y1="36" x2="{WIDTH}" y2="36" stroke="#30363d" stroke-width="1"/>')

    # Window Control Buttons
    svg.append('<circle cx="18" cy="18" r="5" fill="#ff5f56"/>')
    svg.append('<circle cx="32" cy="18" r="5" fill="#ffbd2e"/>')
    svg.append('<circle cx="46" cy="18" r="5" fill="#27c93f"/>')

    svg.append(f'<text x="{WIDTH//2}" y="22" text-anchor="middle" class="header-title">aditya@github ~ (portrait.dither.svg)</text>')

    # Dither Dots & Terminal Scanline Elements (grouped by row for top-to-bottom reveal animation)
    for r in range(rows):
        row_dots = []
        for c in range(cols):
            cell = grid[r][c]
            if cell['is_bg']:
                continue  # Skip background
            
            cx = OFFSET_X + c * cell_w + cell_w / 2
            cy = OFFSET_Y + r * cell_h + cell_h / 2
            luma = cell['luma']
            edge = cell['edge']
            
            if edge > 75 and luma < 150:
                # High contrast features (eyes, mustache contour, hair strands, collar)
                w_seg = cell_w * 0.90
                h_seg = cell_h * 0.65
                row_dots.append(f'<rect class="dot" x="{(cx - w_seg/2):.2f}" y="{(cy - h_seg/2):.2f}" width="{w_seg:.2f}" height="{h_seg:.2f}" rx="1.5" fill="#79c0ff"/>')
            elif luma > 175:
                # Face highlights -> Light blue scanline pill
                w_seg = cell_w * 0.75
                h_seg = cell_h * 0.50
                row_dots.append(f'<rect class="dot" x="{(cx - w_seg/2):.2f}" y="{(cy - h_seg/2):.2f}" width="{w_seg:.2f}" height="{h_seg:.2f}" rx="1" fill="#58a6ff"/>')
            elif luma > 130:
                # Skin base -> Medium blue dot
                r_dot = min(cell_w, cell_h) * 0.38
                row_dots.append(f'<circle class="dot" cx="{cx:.2f}" cy="{cy:.2f}" r="{r_dot:.2f}" fill="#388bfd"/>')
            elif luma > 70:
                # Shadows / hair body -> Dark blue dot
                r_dot = min(cell_w, cell_h) * 0.30
                row_dots.append(f'<circle class="dot" cx="{cx:.2f}" cy="{cy:.2f}" r="{r_dot:.2f}" fill="#1f6feb"/>')
            else:
                # Shirt / dark hair base -> Small dark blue dot
                r_dot = min(cell_w, cell_h) * 0.22
                row_dots.append(f'<circle class="dot" cx="{cx:.2f}" cy="{cy:.2f}" r="{r_dot:.2f}" fill="#163866"/>')

        if row_dots:
            delay = r * 0.035
            svg.append(f'<g class="row-g" style="animation-delay: {delay:.3f}s;" opacity="0">')
            svg.append(f'  <animate attributeName="opacity" from="0" to="1" dur="0.12s" begin="{delay:.3f}s" fill="freeze" />')
            svg.extend(row_dots)
            svg.append('</g>')

    svg.append('</svg>')
    return "\n".join(svg) + "\n"

def main():
    img_path = find_source_image()
    grid = None
    
    if img_path:
        print(f"Found source photo: {img_path}")
        grid = process_image(img_path)
    else:
        print("No photo found. Generating default terminal portrait SVG.")

    if not grid:
        grid = generate_default_face_pixels()

    svg_content = render_svg(grid)
    
    output_path = "avi-ascii.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Dotted portrait SVG generated successfully at '{output_path}'!")

if __name__ == "__main__":
    main()
