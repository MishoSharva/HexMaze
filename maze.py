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
    {"rect": pygame.Rect(20, 20, 140, 42), "label": "Width (cols)", "text": "20", "active": False, "ph": "20"},
    {"rect": pygame.Rect(180, 20, 140, 42), "label": "Height (rows)", "text": "20", "active": False, "ph": "20"},
    {"rect": pygame.Rect(340, 20, 160, 42), "label": "Hex size px (r)", "text": "", "active": False, "ph": "auto"},
    {"rect": pygame.Rect(520, 20, 160, 42), "label": "Line width", "text": "2", "active": False, "ph": "2"},
]

btn = pygame.Rect(700, 20, 220, 42)

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

EVENQ = [(+1,0),(0,+1),(-1,+1),(-1,0),(0,-1),(+1,-1)]
ODDQ  = [(+1,0),(+1,+1),(0,+1),(-1,0),(0,-1),(+1,-1)]

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

def draw_outline(rad, lw):
    drawn = set()
    for (x, y), (cx, cy) in centers.items():
        pts = hex_points(cx, cy, rad)  # 6 corners of this hex
        dirs = EVENQ if (x % 2 == 0) else ODDQ
        for d, (dx, dy) in enumerate(dirs):
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny):  # neighbor missing → edge is on border
                a = pts[d]
                b = pts[(d + 1) % 6]
                # deduplicate line regardless of direction
                key  = (round(a[0],2), round(a[1],2), round(b[0],2), round(b[1],2))
                rkey = (key[2], key[3], key[0], key[1])
                if key not in drawn and rkey not in drawn:import math, pygame, sys, time

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
    {"rect": pygame.Rect(20, 20, 140, 42), "label": "Width (cols)", "text": "20", "active": False, "ph": "20"},
    {"rect": pygame.Rect(180, 20, 140, 42), "label": "Height (rows)", "text": "20", "active": False, "ph": "20"},
    {"rect": pygame.Rect(340, 20, 160, 42), "label": "Hex size px (r)", "text": "", "active": False, "ph": "auto"},
    {"rect": pygame.Rect(520, 20, 160, 42), "label": "Line width", "text": "2", "active": False, "ph": "2"},
]

btn = pygame.Rect(700, 20, 220, 42)

cols = rows = 0
radius_override = 0
line_w = 2
generated = False
error = ""
blink_on = True
last_blink = time.time()

centers = {}
rad_cached = 0

EVENQ = [(+1,0),(0,+1),(-1,+1),(-1,0),(0,-1),(+1,-1)]
ODDQ  = [(+1,0),(+1,+1),(0,+1),(-1,0),(0,-1),(+1,-1)]

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

def in_bounds(x,y):
    return 0 <= x < cols and 0 <= y < rows

def _edge_key(a, b):
    ax, ay = round(a[0], 3), round(a[1], 3)
    bx, by = round(b[0], 3), round(b[1], 3)
    return (ax, ay, bx, by) if (ax, ay) <= (bx, by) else (bx, by, ax, ay)

def draw_outer_border(rad, lw):
    if not centers: return
    edges = set()
    pts_cache = {}
    for (x, y), (cx, cy) in centers.items():
        pts = pts_cache.get((cx, cy))
        if pts is None:
            pts = hex_points(cx, cy, rad)
            pts_cache[(cx, cy)] = pts
        dirs = EVENQ if (x % 2 == 0) else ODDQ
        for d, (dx, dy) in enumerate(dirs):
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny):
                a = pts[d]
                b = pts[(d + 1) % 6]
                edges.add(_edge_key(a, b))
    if not edges: return
    adj = {}
    def add_adj(p, q):
        adj.setdefault(p, []).append(q)
        adj.setdefault(q, []).append(p)
    for ax, ay, bx, by in edges:
        p = (ax, ay)
        q = (bx, by)
        add_adj(p, q)
    start = min(adj.keys(), key=lambda p: (p[0], p[1]))
    def angle(c, p): return math.atan2(p[1]-c[1], p[0]-c[0])
    ordered = {v: sorted(n, key=lambda k: angle(v, k)) for v, n in adj.items()}
    def prev_idx(lst, i): return (i - 1) % len(lst)
    path = [start]
    curr = start
    if not ordered[curr]: return
    nxt = ordered[curr][0]
    used = {_edge_key(curr, nxt)}
    path.append(nxt)
    prev = start
    steps = 0
    limit = len(edges) + 8
    curr, prev = nxt, curr
    while (curr != start or prev == start) and steps < limit:
        nbrs = ordered[curr]
        try:
            ip = nbrs.index(prev)
        except ValueError:
            break
        cand = nbrs[prev_idx(nbrs, ip)]
        ek = _edge_key(curr, cand)
        if ek not in edges or ek in used:
            alt = nbrs[(ip + 1) % len(nbrs)]
            ek2 = _edge_key(curr, alt)
            if ek2 in edges and ek2 not in used:
                cand, ek = alt, ek2
            else:
                break
        used.add(ek)
        path.append(cand)
        prev, curr = curr, cand
        steps += 1
    poly = [(int(round(x)), int(round(y))) for (x, y) in path]
    if len(poly) >= 3:
        pygame.draw.lines(screen, INK, True, poly, lw)

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
    pygame.draw.rect(screen, ACC, btn, 0, border_radius=8)
    screen.blit(FONT.render("Generate", True, (255,255,255)), (btn.x + 18, btn.y + 8))

def handle_generate():
    global cols, rows, radius_override, line_w, generated, error, centers, rad_cached
    c = parse_int(boxes[0]["text"])
    r = parse_int(boxes[1]["text"])
    rin = parse_int(boxes[2]["text"])
    lw = max(1, parse_int(boxes[3]["text"]) or 2)
    cols, rows = max(0, c), max(0, r)
    radius_override = max(0, rin)
    line_w = lw
    generated, error = (cols > 0 and rows > 0), ""
    if not generated: return
    rad = radius_override if radius_override > 0 else auto_radius(cols, rows)
    if rad < 3:
        generated = False
        error = "Too big to fit. Lower counts."
        return
    centers = build_centers(cols, rows, rad)
    rad_cached = rad

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for b in boxes:
                b["active"] = b["rect"].collidepoint(e.pos)
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
                    if e.unicode.isdigit() and len(active["text"]) < 6:
                        active["text"] += e.unicode
    now = time.time()
    if now - last_blink > 0.5:
        blink_on = not blink_on
        last_blink = now
    screen.fill(BG)
    draw_ui()
    if generated and rad_cached >= 2:
        draw_outer_border(rad_cached, line_w)
        if not error:
            screen.blit(SMALL.render(f"{cols} x {rows}, r={int(rad_cached)}, lw={line_w}", True, OK), (20, 74))
    if error:
        screen.blit(SMALL.render(error, True, ERR), (20, 74))
    pygame.display.flip()
    clock.tick(60)

                    pygame.draw.line(screen, INK, a, b, lw)
                    drawn.add(key)



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
    pygame.draw.rect(screen, ACC, btn, 0, border_radius=8)
    screen.blit(FONT.render("Generate", True, (255,255,255)), (btn.x + 18, btn.y + 8))

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

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx,my = e.pos
            for b in boxes:
                b["active"] = b["rect"].collidepoint(e.pos)
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
            draw_outline(rad_cached, line_w)
            if not error:
                screen.blit(SMALL.render(f"{cols} x {rows}, r={int(rad_cached)}, lw={line_w}", True, OK), (20, 74))
    if error:
        screen.blit(SMALL.render(error, True, ERR), (20, 74))
    pygame.display.flip()
    clock.tick(60)
