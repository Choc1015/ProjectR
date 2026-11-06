import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Forge/SM_FG_'
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WALLB = {('S', 200), ('S', -1000), ('N', 600), ('N', -1000), ('W', -200), ('W', 1000), ('E', -600), ('E', 600)}
MIRROR = {('S', -600), ('S', 1000), ('N', -200), ('N', 1000), ('W', 600), ('W', -600), ('E', 200), ('E', -1000)}
# stone pilasters on some module seams (the furnace takes N t=50..350, keep pilasters off it)
PILASTERS = [('S', -400), ('S', 800), ('N', -400), ('N', 800), ('W', -800), ('W', 400), ('E', -400), ('E', 800)]
SOOT = [('SootPatch', -420, -380, 30), ('SootPatch', 480, 520, 170), ('SootPatchSmall', 100, -660, 80),
        ('SootPatchSmall', -680, 300, 220), ('SootPatch', 760, -420, 300), ('SootPatchSmall', -160, 640, 340)]
# stone ceiling 6x6 at 8 m, two smoke vents; iron-bound beams under it (kept off the vent holes)
VENTS = {(-600, -200): 'CeilingVent', (600, 600): 'CeilingVent'}
BEAM_ROWS = (-1000, -500, 300, 1000)

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    out = {'rm': 0}
    for p in ('FG_Floor_', 'FG_Soot_', 'FG_Wall_', 'FG_Pilaster_', 'FG_Corner_', 'FG_Ceiling_', 'FG_Beam_', 'FG_Entrance', 'FG_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3 + gx * gy) % 3 == 0 else 'FloorTile'
            add(m, 'FG_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, x, y, yaw) in enumerate(SOOT):
        add(m, 'FG_Soot_%02d' % k, x, y, 0, yaw)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallB' if (side, c) in WALLB else 'Wall', 'FG_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(PILASTERS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Pilaster', 'FG_Pilaster_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'FG_Corner_%02d' % j, x, y, 0, yaw)
    j = 0
    for cx in CENTERS:
        for cy in CENTERS:
            add(VENTS.get((cx, cy), 'Ceiling'), 'FG_Ceiling_%02d' % j, cx, cy, 800, 0); j += 1
    b = 0
    for y in BEAM_ROWS:
        for cx in CENTERS:
            add('Beam', 'FG_Beam_%02d' % b, cx, y, 800, 0); b += 1
    add('EntranceDoor', 'FG_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'FG_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'ceiling': j, 'beams': b})
    return out
