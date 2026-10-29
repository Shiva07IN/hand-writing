import os
import math
import random
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ----------------- CONFIGURATION -----------------
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Free realistic handwriting fonts from Google Fonts
FONT_URLS = {
    "Caveat": "https://github.com/google/fonts/raw/main/ofl/caveat/Caveat-Regular.ttf",
    "Cedarville": "https://github.com/google/fonts/raw/main/ofl/cedarvillecursive/Cedarville-Cursive.ttf",
    "IndieFlower": "https://github.com/google/fonts/raw/main/ofl/indieflower/IndieFlower-Regular.ttf"
}

def ensure_font(font_name="Caveat"):
    font_path = f"fonts/{font_name}.ttf"
    os.makedirs("fonts", exist_ok=True)
    if not os.path.exists(font_path):
        print(f"Downloading realistic handwriting font '{font_name}'...")
        res = requests.get(FONT_URLS.get(font_name, FONT_URLS["Caveat"]))
        with open(font_path, "wb") as f:
            f.write(res.content)
    return font_path

# ----------------- PAPER GENERATOR -----------------
def generate_spiral_ruled_paper(width=1654, height=2338):
    """
    Generates high-resolution spiral notebook ruled paper with paper texture and lighting.
    """
    # 1. Base off-white notebook paper color
    base_color = (250, 248, 243)
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # 2. Draw ruled lines (matching Indian notebook style)
    line_spacing = 64
    top_margin = 180
    bottom_margin = height - 120
    left_line_margin = 170

    # Draw horizontal blue ruled lines
    for y in range(top_margin, bottom_margin, line_spacing):
        draw.line([(left_line_margin - 30, y), (width - 60, y)], fill=(175, 195, 225), width=2)

    # 3. Spiral binding holes on the left
    spiral_x = 70
    hole_radius = 16
    for y in range(80, height - 60, 75):
        # Dark inner hole
        draw.ellipse([spiral_x - hole_radius, y - hole_radius, 
                      spiral_x + hole_radius, y + hole_radius], fill=(45, 45, 50))
        # Spiral wire shadow / highlight
        draw.arc([spiral_x - hole_radius - 2, y - hole_radius - 2, 
                  spiral_x + hole_radius + 2, y + hole_radius + 2], 
                 start=90, end=270, fill=(180, 180, 180), width=3)

    # 4. Add subtle paper grain & ambient room lighting gradient
    np_img = np.array(img, dtype=np.float32)

    # Grain noise
    noise = np.random.normal(0, 3.0, np_img.shape)
    np_img = np.clip(np_img + noise, 0, 255)

    # Soft ambient room light: slightly brighter in center, warmer on bottom-right
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    vignette = 1.0 - 0.12 * (((x_coords - width*0.4)**2 + (y_coords - height*0.4)**2) / (width**2 + height**2))
    vignette = np.dstack([vignette, vignette, vignette])
    np_img = np.clip(np_img * vignette, 0, 255).astype(np.uint8)

    return Image.fromarray(np_img), top_margin, line_spacing, left_line_margin

# ----------------- REALISTIC TEXT RENDERER -----------------
def get_ballpoint_color():
    """Returns realistic ballpoint blue with slight pressure shade variations."""
    r = random.randint(22, 35)
    g = random.randint(45, 65)
    b = random.randint(110, 145)
    alpha = random.randint(210, 245)
    return (r, g, b, alpha)

def render_realistic_handwriting(text, font_path, output_filename="handwritten_realistic.png"):
    paper_img, top_margin, line_spacing, left_margin = generate_spiral_ruled_paper()
    
    # Transparent layer for ink
    ink_layer = Image.new("RGBA", paper_img.size, (255, 255, 255, 0))
    
    base_font_size = 42
    font = ImageFont.truetype(font_path, base_font_size)
    
    cur_y = top_margin
    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        if not paragraph.strip():
            cur_y += int(line_spacing * 0.7)
            continue
            
        words = paragraph.split(" ")
        cur_x = left_margin + random.randint(5, 15)  # Slight margin unevenness

        for word in words:
            # Check for line wrap
            bbox = font.getbbox(word)
            word_w = bbox[2] - bbox[0]
            
            if cur_x + word_w > paper_img.width - 120:
                cur_x = left_margin + random.randint(5, 15)
                cur_y += line_spacing

            # Render word character-by-character for human jitter
            for char in word:
                # 1. Subtle baseline fluctuation (human hand tremor)
                jitter_y = random.uniform(-1.8, 1.8)
                
                # 2. Subtle rotation (-1.5 to +1.5 degrees)
                rot_angle = random.uniform(-1.8, 1.8)
                
                # 3. Dynamic pen ink color & pressure
                ink_color = get_ballpoint_color()
                
                # Character tile
                char_font = ImageFont.truetype(font_path, int(base_font_size + random.uniform(-1.0, 1.0)))
                c_bbox = char_font.getbbox(char)
                cw = max(1, c_bbox[2] - c_bbox[0])
                ch = max(1, c_bbox[3] - c_bbox[1])

                char_img = Image.new("RGBA", (cw + 20, ch + 20), (255, 255, 255, 0))
                c_draw = ImageDraw.Draw(char_img)
                c_draw.text((10 - c_bbox[0], 10 - c_bbox[1]), char, font=char_font, fill=ink_color)

                if abs(rot_angle) > 0.3:
                    char_img = char_img.rotate(rot_angle, resample=Image.BICUBIC, expand=True)

                # Paste onto ink layer aligned to ruled line
                paste_y = int(cur_y - ch + jitter_y - 8)
                ink_layer.paste(char_img, (int(cur_x), paste_y), char_img)

                cur_x += cw + random.uniform(0.5, 2.5)

            # Space between words with natural variation
            cur_x += random.uniform(18, 26)

        # Move to next line
        cur_y += line_spacing

    # 4. Apply subtle ink bleed / paper absorption filter
    ink_layer = ink_layer.filter(ImageFilter.GaussianBlur(radius=0.4))

    # 5. Composite ink onto paper
    final_img = paper_img.convert("RGBA")
    final_img.alpha_composite(ink_layer)
    final_img = final_img.convert("RGB")

    out_path = os.path.join(OUTPUT_DIR, output_filename)
    final_img.save(out_path, quality=95)
    print(f"Generated realistic assignment: {out_path}")
    return out_path

# ----------------- MAIN EXECUTION -----------------
if __name__ == "__main__":
    font_file = ensure_font("Caveat")

    sample_assignment_text = """Q1. Explain the differences between hot working and cold working processes. State their advantages and limitations.

Hot working and cold working are metal forming processes. In both, force changes the shape of metal by plastic deformation without removing material.

Hot working is done above the metal's recrystallization temperature. New grains form during deformation, so the metal remains ductile and does not build up much strain hardening. Large shape changes need less force. Hot working is useful for forging and hot rolling.

Its limitations are the energy needed for heating, oxidation or scale on the surface, poorer dimensional accuracy and finish, and faster die wear.

Cold working is done below the recrystallization temperature, usually near room temperature. It makes the metal stronger and harder through strain hardening. It gives a smooth finish, close dimensions and no heating scale. Cold rolling and wire drawing are examples.

Cold working needs higher forces and allows less deformation in one step. It can leave residual stresses, stretch grains in the working direction and reduce ductility, so annealing may be needed.

In short, hot working suits large shape changes and improved ductility; cold working suits accurate, strong parts with a smooth surface."""

    render_realistic_handwriting(sample_assignment_text, font_file, "assignment_output.png")