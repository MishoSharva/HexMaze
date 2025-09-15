import sys, math
import pygame

pygame.init()
pygame.display.set_caption("Hex Grid Generator — maze.py")
W, H = 1200, 900
TOP_H = 100
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

BG    = (248, 249, 251)
INK   = (25, 28, 33)
PANEL = (255, 255, 255)
STROKE= (228, 232, 238)
ACCENT= (120, 105, 240)

FONT = pygame.font.SysFont("consolas", 18)
BIG  = pygame.font.SysFont("consolas", 22, bold=True)

class InputBox:
    def __init__(self, x, y, w, h, label, value=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = str(value)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_TAB):
                self.active = False
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode
    def update(self, dt_ms):
        if self.active:
            self.cursor_timer += dt_ms
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False
    def draw(self, surf):
        label_surf = FONT.render(self.label, True, (120,126,137))
        surf.blit(label_surf, (self.rect.x, self.rect.y - 20))
        pygame.draw.rect(surf, PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surf, ACCENT if self.active else STROKE, self.rect, 2, border_radius=6)
        txt_surf = FONT.render(self.text or "", True, INK)
        tx = self.rect.x + 10
        ty = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        surf.blit(txt_surf, (tx, ty))
        if self.active and self.cursor_visible:
            cx = tx + txt_surf.get_width() + 2
            cy = self.rect.y + 8
            pygame.draw.line(surf, INK, (cx, cy), (cx, self.rect.y + self.rect.height - 8), 2)
    def get_int(self, default=0, minv=None, maxv=None):
        try:
            v = int(self.text)
        except:
            v = default
        if minv is not None: v = max(minv, v)
        if maxv is not None: v = min(maxv, v)
        return v

class Button:
    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.hover = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
    def draw(self, surf):
        bg = (245, 243, 255) if self.hover else PANEL
        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, ACCENT, self.rect, 2, border_radius=10)
        label_surf = BIG.render(self.label, True, ACCENT)
        x = self.rect.centerx - label_surf.get_width() // 2
        y = self.rect.centery - label_surf.get_height() // 2
        surf.blit(label_surf, (x, y))

def pointy_hex_corners(cx, cy, r):
    pts = []
    for i in range(6):
        a = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def hex_layout_positions_with_idx(rows, cols, r, start_x, start_y):
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    centers = []
    for rr in range(rows):
        row_offset = (dx / 2) if (rr % 2 == 1) else 0
        for cc in range(cols):
            x = start_x + cc * dx + row_offset
            y = start_y + rr * dy
            centers.append((x, y, rr, cc))
    return centers

def grid_pixel_size(rows, cols, r):
    if rows <= 0 or cols <= 0 or r <= 0:
        return 0, 0
    dx = math.sqrt(3) * r
    dy = 1.5 * r
    width = dx * (cols - 1) + 2 * r
    height = dy * (rows - 1) + 2 * r
    return int(math.ceil(width)), int(math.ceil(height))

rows_val = 20
cols_val = 20
hex_r = 10
border_w = 2

pad = 16
box_w = 140
box_h = 40
x0 = 20
y0 = 20

ib_rows = InputBox(x0, y0, box_w, box_h, "Height", rows_val)
ib_cols = InputBox(x0 + (box_w + pad), y0, box_w, box_h, "Width", cols_val)
ib_size = InputBox(x0 + 2*(box_w + pad), y0, box_w, box_h, "Hex size", hex_r)
ib_bord = InputBox(x0 + 3*(box_w + pad), y0, box_w, box_h, "Border", border_w)
btn = Button(x0 + 4*(box_w + pad) + 20, y0, 160, box_h, "Generate")

centers_cache = []
cache_params = None

def recompute_grid():
    global centers_cache, cache_params
    rows = ib_rows.get_int(default=rows_val, minv=1, maxv=9999)
    cols = ib_cols.get_int(default=cols_val, minv=1, maxv=9999)
    r    = ib_size.get_int(default=hex_r, minv=2, maxv=200)
    bw   = ib_bord.get_int(default=border_w, minv=1, maxv=20)
    avail_w = W
    avail_h = H - TOP_H - 20
    req_w, req_h = grid_pixel_size(rows, cols, r)
    ox = max(10, (avail_w - req_w) // 2)
    oy = TOP_H + 10 + max(0, (avail_h - req_h) // 2)
    centers_cache = hex_layout_positions_with_idx(rows, cols, r, ox + r, oy + r)
    cache_params = (rows, cols, r, ox, oy, bw)

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ib_rows.handle_event(event)
        ib_cols.handle_event(event)
        ib_size.handle_event(event)
        ib_bord.handle_event(event)
        btn.handle_event(event)
        if btn.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
            recompute_grid()

    ib_rows.update(dt)
    ib_cols.update(dt)
    ib_size.update(dt)
    ib_bord.update(dt)

    screen.fill(BG)

    bar = pygame.Rect(10, 10, W - 20, TOP_H - 20)
    pygame.draw.rect(screen, PANEL, bar, border_radius=14)
    pygame.draw.rect(screen, STROKE, bar, 2, border_radius=14)

    ib_rows.draw(screen)
    ib_cols.draw(screen)
    ib_size.draw(screen)
    ib_bord.draw(screen)
    btn.draw(screen)

    draw_area = pygame.Rect(10, TOP_H, W - 20, H - TOP_H - 10)
    pygame.draw.rect(screen, PANEL, draw_area, border_radius=12)
    pygame.draw.rect(screen, STROKE, draw_area, 2, border_radius=12)

    if cache_params:
        rows, cols, r, ox, oy, bw = cache_params
        for (cx, cy, rr, cc) in centers_cache:
            if rr == 0 or rr == rows - 1 or cc == 0 or cc == cols - 1:
                pygame.draw.polygon(screen, INK, pointy_hex_corners(cx, cy, r), bw)

    pygame.display.flip()

pygame.quit()
sys.exit()
