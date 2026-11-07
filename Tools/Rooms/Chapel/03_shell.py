import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Chapel/SM_CP_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WINDOWS = {('S', -600), ('S', 600), ('N', -200), ('N', 1000), ('W', -1000), ('W', 600), ('E', -600), ('E', 1000)}   # warm glowing chapel windows
MIRROR = {('S', -200), ('S', 1000), ('N', -600), ('W', -600), ('E', 200), ('E', 1000)}
# timber posts on some seams (irregular)
POSTS = [('S', -800), ('S', 400), ('N', -400), ('N', 800), ('W', -800), ('W', 400), ('E', -400), ('E', 800)]
# tall wild grass patches over the grass tiles
GRASS = [('GrassPatch', -420, -380, 30), ('GrassPatch', 520, 480, 170), ('GrassPatchSmall', 100, -660, 80), ('GrassPatchSmall', -700, 320, 220),
         ('GrassPatch', 820, -460, 300), ('GrassPatchSmall', -140, 760, 340), ('GrassPatch', -900, 900, 110), ('GrassPatchSmall', 950, 950, 20)]

LINES = (-800, -400, 0, 400, 800)
BROKEN = {(-200, 200), (600, -600), (-600, -1000), (1000, 600)}

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, sy, sz)})

def run():
    out = {'rm': 0}
    for p in ('CP_Floor_', 'CP_Grass_', 'CP_Wall_', 'CP_Post_', 'CP_Corner_', 'CP_Rafter_', 'CP_Roof_', 'CP_Entrance', 'CP_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    s = 0
    for gx in range(12):
        for gy in range(12):
            x, y = -1100 + gx * 200, -1100 + gy * 200
            m = 'FloorTileB' if ((gx * 73856093) ^ (gy * 19349663)) % 5 == 0 else 'FloorTile'
            pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'CP_Floor_%03d' % i, x, y, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, gx_, gy_, yaw) in enumerate(GRASS):
        pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'CP_Grass_%02d' % k, gx_, gy_, 0, yaw)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallWindow' if (side, c) in WINDOWS else 'Wall', 'CP_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(POSTS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Post', 'CP_Post_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'CP_Corner_%02d' % j, x, y, 0, yaw)
    r = 0
    for line in LINES:
        for c in CENTERS:
            add('Rafter', 'CP_Rafter_%02d' % r, c, line, 800, 0); r += 1
            add('Rafter', 'CP_Rafter_%02d' % r, line, c, 800, 90, 1.0, 1.0, 1.1); r += 1
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            add('RoofBroken' if (cx, cy) in BROKEN else 'Roof', 'CP_Roof_%02d' % j, cx, cy, 800, ((gx * 5 + gy * 3) % 4) * 90, 1.05, 1.05, 1.0); j += 1
    add('EntranceDoor', 'CP_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'CP_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'rafters': r, 'roof': j})
    return out
