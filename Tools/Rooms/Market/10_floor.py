import json, math
# Floor rework (review 2026-11-07: "the 2 m tile mix is messy"), same recipe as Greenhouse/10_floor.py:
# ONE low-contrast ground plane + flagstones of mixed sizes laid in rough rows, dense where people walk, thinning out to bare
# ground near the walls; grass tufts in the gaps. Replaces 03's floor tiles / patches (03 no longer lays them).
# Meshes: SourceArt/Market_Floor.blend -> SourceArt/Export/Market/SM_MK_{Ground,Flag_A/B/C,Tuft_A/B}.fbx (greenhouse shapes, room colours)
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
AB, THEME = 'MK', 'Market'
P = '/Game/Props/%s/SM_%s_' % (THEME, AB)
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/%s/SM_%s_' % (THEME, AB)
NEW = ['Ground', 'Flag_A', 'Flag_B', 'Flag_C', 'Tuft_A', 'Tuft_B']
OLD = ()                          # actor prefixes of the old floor
IMPORT = True                        # False after the first run (meshes already imported)
SEED = 21
# market square: packed earth with a wide band of big pale flagstones from the entrance gate (W) to the exit alley (E), widening around the middle
ROW_H = (60, 75, 90)
LEN = (70, 90, 110, 130)
GAP = 8
CORE = (620, 460)
PATH_HALF = 260
BRANCHES = []
FADE = 220
HOLES = 0.04
TUFTS = 24
try:
    GROUND                           # (x, y, scale x, scale y) pieces of the 24x24 m ground plane
except NameError:
    GROUND = [(0, 0, 1.0, 1.0)]
try:
    EXCLUDE                          # no stones in these rects (x1, y1, x2, y2), cm
except NameError:
    EXCLUDE = []

class Rng:
    # tiny LCG: the MCP script sandbox does not allow 'import random'
    def __init__(self, seed): self.s = seed * 2654435761 % 4294967296
    def random(self):
        self.s = (1664525 * self.s + 1013904223) % 4294967296
        return self.s / 4294967296.0
    def uniform(self, a, b): return a + (b - a) * self.random()
    def choice(self, seq): return seq[int(self.random() * len(seq)) % len(seq)]
    def shuffle(self, lst):
        for i in range(len(lst) - 1, 0, -1):
            j = int(self.random() * (i + 1)) % (i + 1)
            lst[i], lst[j] = lst[j], lst[i]

def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def seg_dist(x, y, a, b, c, d):
    vx, vy = c - a, d - b
    if vx == 0 and vy == 0:
        return math.hypot(x - a, y - b)
    t = max(0.0, min(1.0, ((x - a) * vx + (y - b) * vy) / float(vx * vx + vy * vy)))
    return math.hypot(x - (a + vx * t), y - (b + vy * t))

def paved(x, y):
    # < 0 inside the paved shape, > 0 outside (cm)
    ds = []
    if CORE:
        ds.append((math.sqrt((x / CORE[0]) ** 2 + (y / CORE[1]) ** 2) - 1.0) * min(CORE))
    widen = 60 * smooth((abs(x) - 900) / 300)          # the entrance (W) -> exit (E) path flares a little at the doors
    ds.append(abs(y) - (PATH_HALF + widen))
    for (a, b, c, d, half) in BRANCHES:
        ds.append(seg_dist(x, y, a, b, c, d) - half)
    return min(ds)

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, *a):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(*a)})

def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_' + THEME})
    out = {'rm': 0}
    for p in OLD + (AB + '_Ground', AB + '_Flag_', AB + '_Tuft_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    if IMPORT:
        for n in NEW:
            try:
                call('asset.AssetTools.delete', {'path': P + n})
            except Exception:
                pass
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/' + THEME, 'asset_name': 'SM_%s_%s' % (AB, n),
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
    for k, (gx, gy, sx, sy) in enumerate(GROUND):          # ground plane is 24x24 m; scaled pieces leave holes (water etc.)
        add('Ground', '%s_Ground_%d' % (AB, k), gx, gy, 0, 0, sx, sy, 1.0)
    rng = Rng(SEED)
    flags, tufts, spots = 0, 0, []
    y = -1180
    while y < 1180:
        h = rng.choice(ROW_H)
        x = -1180 + rng.choice((0, 20, 40))           # stagger the row starts so joints don't line up
        while x < 1180:
            L = rng.choice(LEN)
            cx, cy = x + L / 2, y + h / 2
            if any(a - 30 < cx < c + 30 and b - 30 < cy < d + 30 for (a, b, c, d) in EXCLUDE):
                x += L; continue
            keep = 1.0 - smooth((paved(cx, cy) + FADE * 0.3) / FADE)   # 1 inside, 0 outside, ragged band between
            if rng.random() < keep and not rng.random() < HOLES:
                m = rng.choice(('Flag_A', 'Flag_A', 'Flag_B', 'Flag_C'))
                yaw = rng.uniform(-2.5, 2.5) + rng.choice((0, 180))
                add(m, '%s_Flag_%03d' % (AB, flags), cx, cy, 0, yaw, (L - GAP) / 104.0, (h - GAP) / 104.0, rng.uniform(0.8, 1.2))
                flags += 1
            elif keep > 0.1:
                spots.append((cx, cy))                  # a gap next to stones: tuft candidate
            x += L
        y += h
    rng.shuffle(spots)
    for cx, cy in spots[:TUFTS]:
        add(rng.choice(('Tuft_A', 'Tuft_B')), '%s_Tuft_%02d' % (AB, tufts), cx + rng.uniform(-15, 15), cy + rng.uniform(-10, 10), 0,
            rng.uniform(0, 360), *([rng.uniform(0.8, 1.2)] * 3))
        tufts += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'flags': flags, 'tufts': tufts})
    return out
