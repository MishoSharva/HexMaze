import math, pygame, sys, time, random

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
OK = (50, 170, 80)

boxes = [
    {"rect": pygame.Rect(20, 20, 140, 42), "label": "Width (cols)", "text": "", "active": False, "ph": "20"},
    {"rect": pygame.Rect(180, 20, 140, 42), "label": "Height (rows)", "text": "", "active": False, "ph": "20"},
    {"rect": pygame.Rect(340, 20, 160, 42), "label": "Hex size px (r)", "text": "", "active": False, "ph": "auto"},
    {"rect": pygame.Rect(520, 20, 160, 42), "label": "Line width", "text": "", "active": False, "ph": "2"},
]

gen_rect = pygame.Rect(700, 20, 220, 42)
gen_options = ["None", "Recursive Backtracker", "Randomized Prim"]
gen_selected_idx, gen_open = 0, False

btn = pygame.Rect(940, 20, 140, 42)

cols = rows = 0
radius_override = 0
line_w = 2
generated = False
error = ""
blink_on = True
last_blink = time.time()


cells = {}       
centers = {}     
rad_cached = 0


EVENQ = [(+1,0),(0,+1),(-1,+1),(-1,0),(-1,-1),(0,-1)]
ODDQ  = [(+1,0),(+1,+1),(0,+1),(-1,0),(0,-1),(+1,-1)]
OPP   = {0:3,1:4,2:5,3:0,4:1,5:2}

def parse_int(s):
    try: return int(s)
    except: return 0

def auto_radius(c, r):
    if c <= 0 or r <= 0: return 0
    margin = 30
    w_need = 2 + 1.5 * (c - 1)
    h_need = r + 0.5 * (c > 1)
    by_w = (W - 2 * margin) / w_need
    by_h = (H - (90 + margin) - margin) / (math.sqrt(3) * h_need)
    return max(2, min(by_w, by_h))

def hex_points(cx, cy, r):
    return [(cx + r * math.cos(math.radians(60 * i)),
             cy + r * math.sin(math.radians(60 * i))) for i in range(6)]

def neighbors_of(x, y):
    dirs = EVENQ if (x % 2 == 0) else ODDQ
    for d,(dx,dy) in enumerate(dirs):
        yield d, x+dx, y+dy

def build_centers(c, r, rad):
    cs = {}
    w = 2 * rad
    h = math.sqrt(3) * rad
    sx = 30 + w/2
    sy = 90 + 30 + h/2
    for x in range(c):
        oy = (h/2) if (x % 2) else 0
        cx = sx + x * (1.5 * rad)
        for y in range(r):
            cy = sy + oy + y * h
            cs[(x,y)] = (cx, cy)
    return cs

def build_cells(c, r):
    return {(x,y): {"walls":[True]*6} for x in range(c) for y in range(r)}

def in_bounds(x,y):
    return 0 <= x < cols and 0 <= y < rows

def carve_between(a, b, d):
    ax, ay = a
    bx, by = b
    cells[(ax,ay)]["walls"][d] = False
    cells[(bx,by)]["walls"][OPP[d]] = False

def gen_recursive_backtracker():
    stack = []
    seen = set()
    sx, sy = random.randrange(cols), random.randrange(rows)
    stack.append((sx,sy))
    seen.add((sx,sy))
    while stack:
        x,y = stack[-1]
        nbrs = []
        for d,nx,ny in neighbors_of(x,y):
            if in_bounds(nx,ny) and (nx,ny) not in seen:
                nbrs.append((d,nx,ny))
        if not nbrs:
            stack.pop()
            continue
        d,nx,ny = random.choice(nbrs)
        carve_between((x,y),(nx,ny),d)
        seen.add((nx,ny))
        stack.append((nx,ny))

def gen_randomized_prim():
    start = (random.randrange(cols), random.randrange(rows))
    seen = {start}
    frontier = []
    def add_frontier(x,y):
        for d,nx,ny in neighbors_of(x,y):
            if in_bounds(nx,ny) and (nx,ny) not in seen:
                frontier.append(((x,y),d,(nx,ny)))
    add_frontier(*start)
    while frontier:
        i = random.randrange(len(frontier))
        (x,y), d, (nx,ny) = frontier.pop(i)
        if (nx,ny) in seen: 
            continue
        carve_between((x,y),(nx,ny),d)
        seen.add((nx,ny))
        add_frontier(nx,ny)

def draw_walls(rad, lw):
    for (x,y), data in cells.items():
        cx, cy = centers[(x,y)]
        pts = hex_points(cx, cy, rad)
        for d, keep in enumerate(data["walls"]):
            if not keep: 
                continue
            a = pts[d]
            b = pts[(d+1)%6]
            pygame.draw.line(screen, INK, a, b, lw)

def draw_ui():
    pygame.draw.rect(screen, PANEL, (0, 0, W, 86))
    for b in boxes:
        pygame.draw.rect(screen, (255, 255, 255), b["rect"], 0, border_radius=8)
        pygame.draw.rect(screen, ACC if b["active"] else LINE, b["rect"], 2, border_radius=8)
        lab = SMALL.render(b["label"], True, (110,115,125))
        screen.blit(lab, (b["rect"].x, b["rect"].y - 18))
        content = b["text"] if b["text"] else b["ph"]
        col = INK if b["text"] else (150,155,165)
        val = FONT.render(content, True, col)
        screen.blit(val, (b["rect"].x + 10, b["rect"].y + 8))
        if b["active"] and blink_on:
            caret_x = b["rect"].x + 10 + val.get_width()
            pygame.draw.line(screen, ACC, (caret_x, b["rect"].y + 8), (caret_x, b["rect"].y + b["rect"].height - 8), 2)

    pygame.draw.rect(screen, (255,255,255), gen_rect, 0, border_radius=8)
    pygame.draw.rect(screen, ACC if gen_open else LINE, gen_rect, 2, border_radius=8)
    lab = SMALL.render("Generator", True, (110,115,125))
    screen.blit(lab, (gen_rect.x, gen_rect.y - 18))
    screen.blit(FONT.render(gen_options[gen_selected_idx], True, INK), (gen_rect.x + 10, gen_rect.y + 8))

    if gen_open:
        item_h = 34
        total_h = item_h * len(gen_options)
        popup_rect = pygame.Rect(gen_rect.x, gen_rect.y - 6 - total_h, gen_rect.w, total_h)
        pygame.draw.rect(screen, (255,255,255), popup_rect, 0, border_radius=10)
        pygame.draw.rect(screen, ACC, popup_rect, 2, border_radius=10)
        for i,opt in enumerate(gen_options):
            r = pygame.Rect(popup_rect.x, popup_rect.y + i*item_h, popup_rect.w, item_h)
            if r.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (245,245,250), r, 0, border_radius=6)
            screen.blit(SMALL.render(opt, True, INK), (r.x + 10, r.y + 8))

    pygame.draw.rect(screen, ACC, btn, 0, border_radius=8)
    screen.blit(FONT.render("Generate", True, (255,255,255)), (btn.x + 14, btn.y + 8))

def handle_generate():
    global cols, rows, radius_override, line_w, generated, error, centers, cells, rad_cached
    c = parse_int(boxes[0]["text"])
    r = parse_int(boxes[1]["text"])
    rad_in = parse_int(boxes[2]["text"])
    lw = max(1, parse_int(boxes[3]["text"]) or 2)

    cols, rows = max(0,c), max(0,r)
    radius_override = max(0, rad_in)
    line_w = lw
    generated, error = (cols>0 and rows>0), ""

    if not generated: 
        return

    rad = radius_override if radius_override>0 else auto_radius(cols, rows)
    if rad < 3:
        generated = False
        error = "Too big to fit. Lower counts."
        return
    centers = build_centers(cols, rows, rad)
    cells = build_cells(cols, rows)
    rad_cached = rad

    if gen_selected_idx == 1:
        gen_recursive_backtracker()
    elif gen_selected_idx == 2:
        gen_randomized_prim()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx,my = e.pos
            # dropdown click handling
            if gen_open:
                item_h = 34
                total_h = item_h * len(gen_options)
                popup_rect = pygame.Rect(gen_rect.x, gen_rect.y - 6 - total_h, gen_rect.w, total_h)
                if popup_rect.collidepoint((mx,my)):
                    rel = my - popup_rect.y
                    idx = max(0, min(len(gen_options)-1, rel // item_h))
                    gen_selected_idx = int(idx)
                    gen_open = False
                elif gen_rect.collidepoint((mx,my)):
                    gen_open = False
                else:
                    gen_open = False
            else:
                if gen_rect.collidepoint((mx,my)):
                    gen_open = True

            any_active = False
            for b in boxes:
                b["active"] = b["rect"].collidepoint(e.pos)
                any_active |= b["active"]

            if btn.collidepoint(e.pos):
                handle_generate()

        if e.type == pygame.KEYDOWN:
            active = next((b for b in boxes if b["active"]), None)
            if active:
                if e.key == pygame.K_BACKSPACE:
                    active["text"] = active["text"][:-1]
                elif e.key in (pygame.K_RETURN, pygame.K_TAB):
                    pass
                else:
                    if e.unicode.isdigit():
                        if len(active["text"]) < 6:
                            active["text"] += e.unicode

    now = time.time()
    if now - last_blink > 0.5:
        blink_on = not blink_on
        last_blink = now

    screen.fill(BG)
    draw_ui()

    if generated:
        if rad_cached and rad_cached >= 2:
            draw_walls(rad_cached, line_w)
            if not error:
                screen.blit(SMALL.render(f"{cols} x {rows}, r={int(rad_cached)}, lw={line_w}, gen={gen_options[gen_selected_idx]}", True, OK), (20, 74))

    if error:
        screen.blit(SMALL.render(error, True, ERR), (20, 74))

    pygame.display.flip()
    clock.tick(60)
