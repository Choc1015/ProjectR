import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Library/SM_LB_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

# a few modules carry a round window (night-blue glass glows faintly in 09); mirrors mixed so panels don't repeat
WINDOWS = {('S', 600), ('N', -200), ('W', -600), ('E', 200), ('N', 1000)}
MIRROR = {('S', -600), ('S', 1000), ('N', 600), ('W', 200), ('E', -1000), ('E', 600)}
PILLARS = [('S', -400), ('S', 800), ('N', -800), ('N', 400), ('W', -800), ('W', 400), ('E', -400), ('E', 800)]
BEAM_ROWS = (-800, 0, 800)

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    out = {'rm': 0}
    for p in ('LB_Floor_', 'LB_Rug', 'LB_Wall_', 'LB_Pillar_', 'LB_Corner_', 'LB_Ceiling_', 'LB_Beam_', 'LB_Entrance', 'LB_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3 + gx * gy) % 3 == 0 else 'FloorTile'
            pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'LB_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    add('Rug', 'LB_Rug', 0, 0, 0, 10)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallWindow' if (side, c) in WINDOWS else 'Wall', 'LB_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(PILLARS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Pillar', 'LB_Pillar_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'LB_Corner_%02d' % j, x, y, 0, yaw)
    j = 0
    for cx in CENTERS:
        for cy in CENTERS:
            add('Ceiling', 'LB_Ceiling_%02d' % j, cx, cy, 800, ((cx + cy) // 400 % 4) * 90); j += 1
    b = 0
    for y in BEAM_ROWS:
        for cx in CENTERS:
            add('Beam', 'LB_Beam_%02d' % b, cx, y, 800, 0); b += 1
    add('EntranceDoor', 'LB_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'LB_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'ceiling': j, 'beams': b})
    return out
