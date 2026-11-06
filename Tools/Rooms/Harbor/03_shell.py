import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Harbor/SM_HB_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WALLB = {('S', 600), ('S', -1000), ('N', -200), ('N', 1000), ('W', -600), ('W', 200), ('W', 1000), ('E', -200)}  # west wall faces the sunset: more gaps
MIRROR = {('S', -200), ('S', 1000), ('N', 600), ('N', -600), ('W', -1000), ('E', 600), ('E', -600)}
# timber posts on some seams, kept off the flooded corner (south-west, x and y < -600)
POSTS = [('S', -400), ('S', 800), ('N', -400), ('N', 800), ('W', -800), ('W', 400), ('E', -800), ('E', 400)]
# flooded corner: these floor cells are left out and the sunken WaterBasin (6x6 m) fills them
FLOOD = {(gx, gy) for gx in range(3) for gy in range(3)}
BASIN = (-900, -900)
LINES = (-800, -400, 0, 400, 800)
BROKEN = {(-200, 200), (600, -600), (-600, 1000), (1000, 600), (-1000, -200)}

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, sy, sz)})

def run():
    out = {'rm': 0}
    for p in ('HB_Floor_', 'HB_Basin', 'HB_Wall_', 'HB_Post_', 'HB_Corner_', 'HB_Rafter_', 'HB_Roof_', 'HB_Entrance', 'HB_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            if (gx, gy) in FLOOD:
                continue
            m = 'FloorTileB' if (gx * 5 + gy * 3 + gx * gy) % 4 == 0 else 'FloorTile'
            add(m, 'HB_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 2) * 180); i += 1   # planks keep one direction
    add('WaterBasin', 'HB_Basin', BASIN[0], BASIN[1], 0, 0)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallB' if (side, c) in WALLB else 'Wall', 'HB_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(POSTS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Post', 'HB_Post_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'HB_Corner_%02d' % j, x, y, 0, yaw)
    r = 0
    for line in LINES:
        for c in CENTERS:
            add('Rafter', 'HB_Rafter_%02d' % r, c, line, 800, 0); r += 1
            add('Rafter', 'HB_Rafter_%02d' % r, line, c, 800, 90, 1.0, 1.0, 1.1); r += 1
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            add('RoofBroken' if (cx, cy) in BROKEN else 'Roof', 'HB_Roof_%02d' % j, cx, cy, 800, ((gx * 5 + gy * 3) % 4) * 90, 1.05, 1.05, 1.0); j += 1
    add('EntranceDoor', 'HB_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'HB_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'rafters': r, 'roof': j})
    return out
