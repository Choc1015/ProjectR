import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/SnowShrine/SM_SN_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WALLB = {('S', 600), ('S', -1000), ('N', -200), ('N', 1000), ('W', -600), ('W', 200), ('E', 1000), ('E', -200)}
MIRROR = {('S', -200), ('S', 1000), ('N', 600), ('N', -600), ('W', 1000), ('W', -1000), ('E', 600), ('E', -600)}
# timber posts in front of the walls, on some module seams only (irregular on purpose)
POSTS = [('S', -800), ('S', 400), ('N', -400), ('N', 800), ('W', -400), ('W', 800), ('E', -800), ('E', 400)]
SNOW = [('SnowPatch', -420, -360, 25), ('SnowPatch', 520, 480, 160), ('SnowPatchSmall', 100, -660, 80),
        ('SnowPatchSmall', -720, 320, 210), ('SnowPatch', 800, -460, 300), ('SnowPatchSmall', -140, 760, 340)]

# roof: rafter grid on the interior lines (both directions, tops at 800; the Y set is 10% deeper so their undersides differ),
# plank panels 6x6 scaled 1.1 so they meet over the rafters; broken panels let pale daylight in
LINES = (-800, -400, 0, 400, 800)
BROKEN = {(-200, 200), (600, -600), (-600, -1000), (1000, 600), (-1000, -200)}

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, sy, sz)})

def run():
    out = {'rm': 0}
    for p in ('SN_Floor_', 'SN_Snow_', 'SN_Wall_', 'SN_Post_', 'SN_Corner_', 'SN_Rafter_', 'SN_Roof_', 'SN_Entrance', 'SN_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3 + gx * gy) % 3 == 0 else 'FloorTile'
            add(m, 'SN_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, x, y, yaw) in enumerate(SNOW):
        add(m, 'SN_Snow_%02d' % k, x, y, 0, yaw)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallB' if (side, c) in WALLB else 'Wall', 'SN_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(POSTS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Post', 'SN_Post_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'SN_Corner_%02d' % j, x, y, 0, yaw)
    r = 0
    for line in LINES:
        for c in CENTERS:
            add('Rafter', 'SN_Rafter_%02d' % r, c, line, 800, 0); r += 1
            add('Rafter', 'SN_Rafter_%02d' % r, line, c, 800, 90, 1.0, 1.0, 1.1); r += 1
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            m = 'RoofPanelBroken' if (cx, cy) in BROKEN else 'RoofPanel'
            add(m, 'SN_Roof_%02d' % j, cx, cy, 800, ((gx * 5 + gy * 3) % 4) * 90, 1.1, 1.1, 1.0); j += 1
    add('EntranceGate', 'SN_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'SN_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'rafters': r, 'roof': j})
    return out
