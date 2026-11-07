import json, math
# Floor rework (review 2026-11-07: "the 2 m tile mix is messy"). Following the greenhouse reference and stylized environment refs:
# ONE low-contrast ground (olive moss plane) + pale flagstones of mixed sizes laid in rough rows, dense in the middle and along the
# entrance -> exit path, thinning out to bare moss near the walls; grass tufts grow in the gaps. Replaces 03's GH_Floor_ tiles / GH_Grass_ patches.
# Meshes: SourceArt/Greenhouse_Floor.blend -> SourceArt/Export/Greenhouse/SM_GH_{Ground,Flag_A/B/C,Tuft_A/B}.fbx
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Greenhouse/SM_GH_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Greenhouse/SM_GH_'
NEW = ['Ground', 'Flag_A', 'Flag_B', 'Flag_C', 'Tuft_A', 'Tuft_B']
IMPORT = True          # False after the first run (meshes already in /Game/Props/Greenhouse)
SEED = 7
ROW_H = (55, 70, 85)                 # row depth (cm), random per row
LEN = (60, 80, 100, 120)             # stone length along the row (cm)
GAP = 7                              # moss line between stones
CORE = (720, 620)                    # paved ellipse radii (x, y)
PATH_HALF = 170                      # half width of the entrance (W) -> exit (E) path along y = 0
FADE = 260                           # width of the ragged edge where stones thin out
HOLES = 0.05                         # missing stones inside the paved area (moss shows through)

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

def paved(x, y):
    # signed distance-ish: <0 inside the paved shape, >0 outside (cm)
    e = (math.sqrt((x / CORE[0]) ** 2 + (y / CORE[1]) ** 2) - 1.0) * min(CORE)
    widen = 60 * smooth((abs(x) - 900) / 300)          # path flares a little at the doors
    p = abs(y) - (PATH_HALF + widen)
    return min(e, p)

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, *a):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(*a)})

def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_Greenhouse'})
    out = {'rm': 0}
    for p in ('GH_Floor_', 'GH_Grass_', 'GH_Ground', 'GH_Flag_', 'GH_Tuft_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    if IMPORT:
        for n in NEW:
            try:
                call('asset.AssetTools.delete', {'path': P + n})
            except Exception:
                pass
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Greenhouse', 'asset_name': 'SM_GH_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
    add('Ground', 'GH_Ground', 0, 0, 0)
    rng = Rng(SEED)
    flags, tufts, spots = 0, 0, []
    y = -1180
    while y < 1180:
        h = rng.choice(ROW_H)
        x = -1180 + rng.choice((0, 20, 40))           # stagger the row starts so joints don't line up
        while x < 1180:
            L = rng.choice(LEN)
            cx, cy = x + L / 2, y + h / 2
            d = paved(cx, cy)
            keep = 1.0 - smooth((d + FADE * 0.3) / FADE)   # 1 inside, 0 outside, ragged band between
            if rng.random() < keep and not rng.random() < HOLES:
                m = rng.choice(('Flag_A', 'Flag_A', 'Flag_B', 'Flag_C'))
                yaw = rng.uniform(-2.5, 2.5) + rng.choice((0, 180))
                add(m, 'GH_Flag_%03d' % flags, cx, cy, 0, yaw, (L - GAP) / 104.0, (h - GAP) / 104.0, rng.uniform(0.8, 1.2))
                flags += 1
            elif keep > 0.1:
                spots.append((cx, cy))                  # a gap next to stones: tuft candidate
            x += L
        y += h
    rng.shuffle(spots)
    for cx, cy in spots[:36]:
        add(rng.choice(('Tuft_A', 'Tuft_B')), 'GH_Tuft_%02d' % tufts, cx + rng.uniform(-15, 15), cy + rng.uniform(-10, 10), 0,
            rng.uniform(0, 360), *([rng.uniform(0.8, 1.2)] * 3))
        tufts += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'flags': flags, 'tufts': tufts})
    return out
