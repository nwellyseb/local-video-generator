"""
Procedural, fully-local renderer. Draws each frame with Pillow:
  - black title bar (only shown briefly at the start, matching the reference)
  - gray body background with a ground line
  - a simple flat-shape "scene" icon (stick figure, tree, laptop, etc.)
  - a black rounded caption box with wrapped white text at the bottom

No external images/AI generation - everything is basic shape drawing,
so it's fast and fully offline.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

from . import config


def _font(size):
    """
    Try a list of common bold-font locations across macOS/Linux/Windows and
    use the first one that exists. Falls back to PIL's built-in font only as
    an absolute last resort (and prints a warning, since that font is tiny
    and looks broken at video resolution).
    """
    candidates = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Windows
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    print(
        "WARNING: no bold TTF font found on this system - falling back to "
        "PIL's tiny built-in font, which will look broken. Set FONT_TITLE / "
        "FONT_CAPTION in config.py to a real .ttf path on your machine."
    )
    return ImageFont.load_default()


TITLE_FONT = _font(config.TITLE_FONT_SIZE)
CAPTION_FONT = _font(config.CAPTION_FONT_SIZE)


# ---------- scene icon drawers ----------
# Each takes (draw, cx, cy) - a center point on the ground line - and
# draws a simple flat-shape icon there. Keep everything basic
# rectangles/ellipses/lines so it matches the flat vector reference style.

def draw_stick_figure(draw, cx, cy, scale=1.0):
    s = scale
    head_r = 45 * s
    body_top = cy - 160 * s
    body_bottom = cy - 40 * s
    # head
    draw.ellipse(
        [cx - head_r, body_top - head_r * 2, cx + head_r, body_top],
        fill=config.COLOR_SKIN, outline=config.COLOR_FIGURE, width=int(6 * s),
    )
    # simple face
    eye_y = body_top - head_r * 1.1
    draw.ellipse([cx - 15 * s, eye_y - 5 * s, cx - 5 * s, eye_y + 5 * s], fill=config.COLOR_FIGURE)
    draw.ellipse([cx + 5 * s, eye_y - 5 * s, cx + 15 * s, eye_y + 5 * s], fill=config.COLOR_FIGURE)
    draw.arc([cx - 18 * s, eye_y + 5 * s, cx + 18 * s, eye_y + 30 * s], 200, 340,
              fill=config.COLOR_FIGURE, width=int(4 * s))
    # body line
    draw.line([cx, body_top, cx, body_bottom], fill=config.COLOR_FIGURE, width=int(8 * s))
    # arms
    draw.line([cx, body_top + 40 * s, cx - 60 * s, body_top + 90 * s], fill=config.COLOR_FIGURE, width=int(6 * s))
    draw.line([cx, body_top + 40 * s, cx + 60 * s, body_top + 90 * s], fill=config.COLOR_FIGURE, width=int(6 * s))
    # legs
    draw.line([cx, body_bottom, cx - 55 * s, cy], fill=config.COLOR_FIGURE, width=int(8 * s))
    draw.line([cx, body_bottom, cx + 55 * s, cy], fill=config.COLOR_FIGURE, width=int(8 * s))


def draw_tree(draw, cx, cy, scale=1.0):
    s = scale
    trunk_w = 40 * s
    trunk_h = 220 * s
    draw.rectangle(
        [cx - trunk_w / 2, cy - trunk_h, cx + trunk_w / 2, cy],
        fill=(93, 64, 39), outline=config.COLOR_FIGURE, width=int(4 * s),
    )
    r = 95 * s
    green = (67, 133, 76)
    draw.ellipse([cx - r * 1.6, cy - trunk_h - r * 1.0, cx - r * 0.2, cy - trunk_h + r * 0.9],
                 fill=green, outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.ellipse([cx - r * 0.6, cy - trunk_h - r * 1.8, cx + r * 0.9, cy - trunk_h - r * 0.1],
                 fill=green, outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.ellipse([cx + r * 0.1, cy - trunk_h - r * 1.0, cx + r * 1.5, cy - trunk_h + r * 0.9],
                 fill=green, outline=config.COLOR_FIGURE, width=int(4 * s))


def draw_laptop(draw, cx, cy, scale=1.0):
    s = scale
    w, h = 220 * s, 140 * s
    draw.polygon(
        [(cx - w / 2, cy), (cx + w / 2, cy), (cx + w / 2 - 20 * s, cy + 25 * s), (cx - w / 2 + 20 * s, cy + 25 * s)],
        fill=(120, 120, 120), outline=config.COLOR_FIGURE,
    )
    draw.rectangle([cx - w / 2 + 15 * s, cy - h, cx + w / 2 - 15 * s, cy],
                    fill=(50, 50, 50), outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.rectangle([cx - w / 2 + 25 * s, cy - h + 15 * s, cx + w / 2 - 25 * s, cy - 15 * s],
                    fill=(140, 190, 230))


def draw_book(draw, cx, cy, scale=1.0):
    s = scale
    w, h = 200 * s, 140 * s
    draw.polygon([(cx - w / 2, cy - h * 0.3), (cx, cy - h * 0.55), (cx + w / 2, cy - h * 0.3),
                  (cx + w / 2, cy), (cx, cy - h * 0.25), (cx - w / 2, cy)],
                 fill=(190, 60, 60), outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.line([cx, cy - h * 0.55, cx, cy - h * 0.25], fill=config.COLOR_FIGURE, width=int(3 * s))


def draw_brain(draw, cx, cy, scale=1.0):
    s = scale
    r = 90 * s
    draw.ellipse([cx - r, cy - r * 2, cx + r, cy], fill=(230, 170, 170), outline=config.COLOR_FIGURE, width=int(5 * s))
    for i in range(3):
        yy = cy - r * 1.7 + i * r * 0.6
        draw.arc([cx - r * 0.8, yy, cx + r * 0.1, yy + r * 0.6], 20, 200, fill=config.COLOR_FIGURE, width=int(3 * s))
        draw.arc([cx - r * 0.1, yy, cx + r * 0.8, yy + r * 0.6], -20, 160, fill=config.COLOR_FIGURE, width=int(3 * s))


def draw_clock(draw, cx, cy, scale=1.0):
    s = scale
    r = 100 * s
    draw.ellipse([cx - r, cy - r * 2, cx + r, cy], fill=(240, 240, 235), outline=config.COLOR_FIGURE, width=int(6 * s))
    ccy = cy - r
    draw.line([cx, ccy, cx, ccy - r * 0.55], fill=config.COLOR_FIGURE, width=int(5 * s))
    draw.line([cx, ccy, cx + r * 0.4, ccy], fill=config.COLOR_FIGURE, width=int(5 * s))


def draw_heart(draw, cx, cy, scale=1.0):
    s = scale
    r = 60 * s
    draw.ellipse([cx - r * 1.6, cy - r * 2.3, cx, cy - r * 0.6], fill=(200, 60, 70), outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.ellipse([cx, cy - r * 2.3, cx + r * 1.6, cy - r * 0.6], fill=(200, 60, 70), outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.polygon([(cx - r * 1.5, cy - r * 1.1), (cx + r * 1.5, cy - r * 1.1), (cx, cy)], fill=(200, 60, 70))


def draw_lightbulb(draw, cx, cy, scale=1.0):
    s = scale
    r = 80 * s
    draw.ellipse([cx - r, cy - r * 3, cx + r, cy - r], fill=(250, 220, 120), outline=config.COLOR_FIGURE, width=int(5 * s))
    draw.rectangle([cx - r * 0.4, cy - r, cx + r * 0.4, cy - r * 0.6], fill=(150, 150, 150), outline=config.COLOR_FIGURE)


def draw_phone(draw, cx, cy, scale=1.0):
    s = scale
    w, h = 130 * s, 250 * s
    draw.rounded_rectangle([cx - w / 2, cy - h, cx + w / 2, cy], radius=18 * s,
                            fill=(40, 40, 40), outline=config.COLOR_FIGURE, width=int(4 * s))
    draw.rectangle([cx - w / 2 + 10 * s, cy - h + 25 * s, cx + w / 2 - 10 * s, cy - 20 * s], fill=(170, 210, 235))


def draw_chessboard(draw, cx, cy, scale=1.0):
    s = scale
    n, cell = 4, 40 * s
    total = n * cell
    x0, y0 = cx - total / 2, cy - total
    for row in range(n):
        for col in range(n):
            color = (235, 235, 225) if (row + col) % 2 == 0 else (60, 60, 60)
            draw.rectangle([x0 + col * cell, y0 + row * cell, x0 + (col + 1) * cell, y0 + (row + 1) * cell], fill=color)
    draw.rectangle([x0, y0, x0 + total, y0 + total], outline=config.COLOR_FIGURE, width=int(4 * s))


def draw_money(draw, cx, cy, scale=1.0):
    s = scale
    r = 80 * s
    draw.ellipse([cx - r, cy - r * 2, cx + r, cy], fill=(90, 170, 100), outline=config.COLOR_FIGURE, width=int(5 * s))
    bbox = [cx - r, cy - r * 2, cx + r, cy]
    draw.text(((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2), "$", font=CAPTION_FONT,
               fill=config.COLOR_FIGURE, anchor="mm")


def draw_generic(draw, cx, cy, scale=1.0):
    s = scale
    r = 90 * s
    draw.ellipse([cx - r, cy - r * 2, cx + r, cy], fill=(180, 180, 190), outline=config.COLOR_FIGURE, width=int(5 * s))


SCENE_DRAWERS = {
    "figure": draw_stick_figure,
    "tree": draw_tree,
    "laptop": draw_laptop,
    "book": draw_book,
    "brain": draw_brain,
    "clock": draw_clock,
    "heart": draw_heart,
    "lightbulb": draw_lightbulb,
    "phone": draw_phone,
    "chessboard": draw_chessboard,
    "money": draw_money,
    "generic": draw_generic,
}


def _wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_frame(title: str, caption: str, scene, show_title: bool) -> Image.Image:
    """
    `scene` may be a single keyword (str) or a list of keywords - a list
    composes multiple icons together, spaced and scaled automatically.
    """
    if isinstance(scene, str):
        scene = [scene]
    scene = scene or ["generic"]

    img = Image.new("RGB", (config.WIDTH, config.HEIGHT), config.COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Title bar
    if show_title:
        draw.rectangle([0, 0, config.WIDTH, config.TITLE_BAR_HEIGHT], fill=config.COLOR_TITLE_BG)
        lines = textwrap.wrap(title, width=22)
        total_h = len(lines) * (config.TITLE_FONT_SIZE + 10)
        y = (config.TITLE_BAR_HEIGHT - total_h) / 2
        for line in lines:
            draw.text((config.WIDTH / 2, y), line, font=TITLE_FONT,
                       fill=config.COLOR_TITLE_TEXT, anchor="ma", align="center")
            y += config.TITLE_FONT_SIZE + 10

    # Ground line
    draw.line([(0, config.GROUND_Y), (config.WIDTH, config.GROUND_Y)],
               fill=config.COLOR_FIGURE, width=3)

    # Scene icon(s) - dynamically spaced across a band on the right two-thirds
    # of the frame, like the reference. More icons = smaller scale + tighter
    # spacing so they never overlap or run off-screen.
    n = len(scene)
    band_left = config.WIDTH * 0.40
    band_right = config.WIDTH * 0.92
    band_width = band_right - band_left

    if n == 1:
        positions = [config.WIDTH * 0.62]
        scale = 1.4
    else:
        # even spacing across the band
        positions = [band_left + band_width * (i + 0.5) / n for i in range(n)]
        # shrink scale as icons get denser so neighbors don't collide
        scale = max(0.55, 1.3 - 0.16 * (n - 1))

    for keyword, cx in zip(scene, positions):
        drawer = SCENE_DRAWERS.get(keyword, draw_generic)
        drawer(draw, cx=cx, cy=config.GROUND_Y, scale=scale)

    # Caption box
    box_top = config.HEIGHT - config.CAPTION_BOX_HEIGHT - config.CAPTION_BOX_MARGIN
    box_bottom = config.HEIGHT - config.CAPTION_BOX_MARGIN
    draw.rounded_rectangle(
        [config.CAPTION_BOX_MARGIN, box_top, config.WIDTH - config.CAPTION_BOX_MARGIN, box_bottom],
        radius=24, fill=config.COLOR_CAPTION_BG,
    )
    max_text_w = config.WIDTH - config.CAPTION_BOX_MARGIN * 2 - 60
    lines = _wrap_text(caption, CAPTION_FONT, max_text_w, draw)
    total_h = len(lines) * (config.CAPTION_FONT_SIZE + 12)
    y = (box_top + box_bottom) / 2 - total_h / 2
    for line in lines:
        draw.text((config.WIDTH / 2, y), line, font=CAPTION_FONT,
                   fill=config.COLOR_CAPTION_TEXT, anchor="ma", align="center")
        y += config.CAPTION_FONT_SIZE + 12

    return img