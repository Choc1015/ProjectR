import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mill/SM_ML_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WINDOWS = {('S', 600), ('E', -600), ('W', 1000), ('N', 600)}
MIRROR = {('S', -200), ('S', 1000), ('N', -600), ('W', -600), ('E', 200), ('E', 1000)}
# timber posts on some seams; none on the north wall (the stream runs along it)
POSTS = [('S', -400), ('S', 800), ('W', -800), ('W', 400), ('E', -400), ('E', 800)]
# the stream fills the floor row next to the north wall (gy = 11, y 1000..1200); its 1.2 m section is stretched to the 2 m row
STREAM_GY = 11
STREAM_SY = 2.0 / 1.2
LINES = (-800, -400, 0, 400, 800)
BROKEN = {(-200, 200), (600, -600), (-600, -1000), (1000, 600)}

def xf(x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': sy, 'z': sz}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, sy=1.0, sz=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, sy, sz)})

def run():
    out = {'rm': 0}
    for p in ('ML_Floor_', 'ML_Stream_', 'ML_Wall_', 'ML_Post_', 'ML_Corner_', 'ML_Rafter_', 'ML_Roof_', 'ML_Entrance', 'ML_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    s = 0
    for gx in range(12):
        for gy in range(12):
            x, y = -1100 + gx * 200, -1100 + gy * 200
            if gy == STREAM_GY:
                add('Stream', 'ML_Stream_%02d' % s, x, y, 0, 0, 1.0, STREAM_SY, 1.0); s += 1
                continue
            m = 'FloorTileB' if ((gx * 73856093) ^ (gy * 19349663)) % 5 == 0 else 'FloorTile'
            add(m, 'ML_Floor_%03d' % i, x, y, 0, ((gx * 7 + gy * 11) % 2) * 180); i += 1   # planks keep one direction
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallWindow' if (side, c) in WINDOWS else 'Wall', 'ML_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(POSTS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Post', 'ML_Post_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'ML_Corner_%02d' % j, x, y, 0, yaw)
    r = 0
    for line in LINES:
        for c in CENTERS:
            add('Rafter', 'ML_Rafter_%02d' % r, c, line, 800, 0); r += 1
            add('Rafter', 'ML_Rafter_%02d' % r, line, c, 800, 90, 1.0, 1.0, 1.1); r += 1
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            add('RoofBroken' if (cx, cy) in BROKEN else 'Roof', 'ML_Roof_%02d' % j, cx, cy, 800, ((gx * 5 + gy * 3) % 4) * 90, 1.05, 1.05, 1.0); j += 1
    add('EntranceDoor', 'ML_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'ML_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'stream': s, 'walls': k, 'rafters': r, 'roof': j})
    return out
