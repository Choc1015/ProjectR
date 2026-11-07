import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mushroom/SM_MU_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

# bark wall modules (ridges hide the seams themselves, so no posts), B type and mirrors mixed irregularly
WALLB = {('S', -600), ('S', 600), ('N', -1000), ('N', 200), ('W', -200), ('W', 1000), ('E', -600), ('E', 1000)}
MIRROR = {('S', 200), ('S', -1000), ('N', -600), ('N', 600), ('W', -1000), ('W', 600), ('E', -200), ('E', 200)}
MOSS = [('MossPatch', -420, -360, 25), ('MossPatch', 520, 480, 160), ('MossPatchSmall', 100, -660, 80),
        ('MossPatchSmall', -720, 320, 210), ('MossPatch', 800, -460, 300), ('MossPatchSmall', -140, 760, 340),
        ('MossPatch', -880, 880, 110), ('MossPatch', 900, -900, 40), ('MossPatchSmall', 300, 1000, 200), ('MossPatchSmall', -950, -300, 130)]
# inner-wood ceiling 6x6 at 8 m, three knot holes for faint moonlight (hole centre: blender (0,-1.1) -> UE +110 in y)
# Review 2026-11-07: the hole at (200, 1000) sat against the north wall (its opening is shifted +110 in y, reaching past the wall face at
# 1170), so looking up through it showed the wall top and the open outside. Holes must stay at least one panel away from the walls.
HOLES = {(-600, 200), (600, -600), (200, 600)}

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    out = {'rm': 0}
    for p in ('MU_Floor_', 'MU_Moss_', 'MU_Wall_', 'MU_Corner_', 'MU_Ceiling_', 'MU_CeilingCap_', 'MU_Entrance', 'MU_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3 + gx * gy) % 3 == 0 else 'FloorTile'
            pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'MU_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, x, y, yaw) in enumerate(MOSS):
        pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'MU_Moss_%02d' % k, x, y, 0, yaw)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallB' if (side, c) in WALLB else 'Wall', 'MU_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'MU_Corner_%02d' % j, x, y, 0, yaw)
    j = 0
    for cx in CENTERS:
        for cy in CENTERS:
            add('CeilingHole' if (cx, cy) in HOLES else 'Ceiling', 'MU_Ceiling_%02d' % j, cx, cy, 800, 0); j += 1
    add('EntranceDoor', 'MU_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'MU_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'ceiling': j})
    return out
