import math, pygame, sys

pygame.init()
W, H = 1100, 820
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Hex Honeycomb")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 22)
SMALL = pygame.font.SysFont("consolas", 16)

BG = (252, 253, 255)
INK = (25, 28, 33)
PANEL = (245, 246, 249)
LINE = (220, 224, 231)
ACC = (120, 105, 240)
ERR = (205, 60, 80)

boxes = [
    {"rect": pygame.Rect(20, 20, 140, 42), "label": "Width (cols)", "text": "", "active": False},
    {"rect": pygame.Rect(180, 20, 140, 42), "label": "Height (rows)", "text": "", "active": False},
    {"rect": pygame.Rect(340, 20, 160, 42), "label": "Hex size px (r)", "text": "", "active": False},
]
btn = pygame.Rect(520, 20, 150, 42)

cols = rows = 0
radius_override = 0
ready = False
error = ""

def draw_hex(s, cx, cy, r, color):
    pts = []
    for i in range(6):
        a = math.radians(60 * i)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(s, color, pts, 2)

def auto_radius(c, r):
    if c <= 0 or r <= 0: return 0
    margin = 30
    w_need = 2 + 1.5 * (c - 1)
    h_need = r + 0.5 * (c > 1)
    by_w = (W - 2 * margin) / w_need
    by_h = (H - (90 + margin) - margin) / (math.sqrt(3) * h_need)
    return max(2, min(by_w, by_h))

def draw_ui():
    pygame.draw.rect(screen, PANEL, (0, 0, W, 86))
    for b in boxes:
        pygame.draw.rect(screen, (255, 255, 255), b["rect"], 0, border_radius=8)
        pygame.draw.rect(screen, ACC if b["active"] else LINE, b["rect"], 2, border_radius=8)
        lab = SMALL.render(b["label"], True, (110, 115, 125))
        screen.blit(lab, (b["rect"].x, b["rect"].y - 18))
        val = FONT.render(b["text"], True, INK)
        screen.blit(val, (b["rect"].x + 10, b["rect"].y + 8))
    pygame.draw.rect(screen, ACC, btn, 0, border_radius=8)
    screen.blit(FONT.render("Generate", True, (255, 255, 255)), (btn.x + 18, btn.y + 8))

def draw_grid(c, r, rad):
    w = 2 * rad
    h = math.sqrt(3) * rad
    sx = 30 + w / 2
    sy = 90 + 30 + h / 2
    for x in range(c):
        oy = (h / 2) if x % 2 else 0
        cx = sx + x * (1.5 * rad)
        for y in range(r):
            cy = sy + oy + y * h
            draw_hex(screen, cx, cy, rad, INK)

def parse_int(s):
    try: return int(s)
    except: return 0

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for b in boxes: b["active"] = b["rect"].collidepoint(e.pos)
            if btn.collidepoint(e.pos):
                c = parse_int(boxes[0]["text"])
                r = parse_int(boxes[1]["text"])
                rad = parse_int(boxes[2]["text"])
                cols, rows = max(0, c), max(0, r)
                radius_override = max(0, rad)
                ready = cols > 0 and rows > 0
                error = ""
                if ready:
                    if radius_override == 0:
                        rad_auto = auto_radius(cols, rows)
                        if rad_auto < 3:
                            ready = False
                            error = "Too big to fit. Lower counts."
                    else:
                        max_w = auto_radius(cols, rows) or 0
                        if radius_override > max_w:
                            error = "Hex size too large, some cells won’t fit."
        if e.type == pygame.KEYDOWN:
            active = next((b for b in boxes if b["active"]), None)
            if active:
                if e.key == pygame.K_BACKSPACE:
                    active["text"] = active["text"][:-1]
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    c = parse_int(boxes[0]["text"])
                    r = parse_int(boxes[1]["text"])
                    rad = parse_int(boxes[2]["text"])
                    cols, rows = max(0, c), max(0, r)
                    radius_override = max(0, rad)
                    ready = cols > 0 and rows > 0
                    error = ""
                else:
                    if e.unicode.isdigit():
                        if len(active["text"]) < 5:
                            active["text"] += e.unicode

    screen.fill(BG)
    draw_ui()
    if ready:
        rad = radius_override if radius_override > 0 else auto_radius(cols, rows)
        if rad and rad >= 2:
            draw_grid(cols, rows, rad)
    if error:
        screen.blit(SMALL.render(error, True, ERR), (20, 74))
    pygame.display.flip()
    clock.tick(60)
