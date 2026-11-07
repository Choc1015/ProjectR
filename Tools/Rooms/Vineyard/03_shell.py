import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Vineyard/SM_VY_'
# wall sides: yaw so the blender -Y face points into the room; t = position along the wall in the wall mesh's own X
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

WALLB = {('S', -200), ('S', 1000), ('N', -600), ('N', 600), ('W', 1000), ('W', -600), ('E', -1000), ('E', 600)}
MIRROR = {('S', 600), ('S', -1000), ('N', 200), ('N', -1000), ('W', -200), ('W', 600), ('E', 200), ('E', -600)}
# stone piers on some module seams (irregular)
PIERS = [('S', -400), ('S', 800), ('N', -800), ('N', 400), ('W', -800), ('W', 400), ('E', -400), ('E', 800)]
LEAVES = [('LeafPatch', -420, -380, 30), ('LeafPatch', 520, 460, 170), ('LeafPatchSmall', 80, -680, 80),
        ('LeafPatchSmall', -700, 300, 220), ('LeafPatch', 820, -480, 300), ('LeafPatchSmall', -120, 760, 340)]

# ceiling: pergola beam grid (X beams on the interior lines at the wall top, Y beams just under them), vine canopies in the cells
BEAM_LINES = (-800, -400, 0, 400, 800)
CANOPY_Z = 720                 # canopy corners hang just under the Y beams (their underside is 760 - 40)
MISSING = {(200, -200), (-600, 600), (600, 600), (-1000, -600)}       # sunlight falls in here
TORN = {(-200, -600): 'VineCanopySparse', (1000, 200): 'VineCanopySparse', (-600, 1000): 'VineCanopySparse', (200, 1000): 'VineCanopySparse'}
COLORS = ('VineCanopy', 'VineCanopy', 'VineCanopy')

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    out = {'rm': 0}
    for p in ('VY_Floor_', 'VY_Leaf_', 'VY_Wall_', 'VY_Pier_', 'VY_Corner_', 'VY_Beam_', 'VY_Canopy_', 'VY_Entrance', 'VY_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    i = 0
    for gx in range(12):
        for gy in range(12):
            # dirt tiles are high contrast: only ~1 in 5, scattered by a hash (the old modulo formula drew diagonal stairs)
            m = 'FloorTileB' if ((gx * 73856093) ^ (gy * 19349663)) % 5 == 0 else 'FloorTile'
            pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'VY_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, x, y, yaw) in enumerate(LEAVES):
        pass  # floor moved to 10_floor.py (review 2026-11-07): add(m, 'VY_Leaf_%02d' % k, x, y, 0, yaw)
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('WallVine' if (side, c) in WALLB else 'Wall', 'VY_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (side, t) in enumerate(PIERS):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('Pier', 'VY_Pier_%02d' % j, x, y, 0, yaw)
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add('Corner', 'VY_Corner_%02d' % j, x, y, 0, yaw)
    b = 0
    for line in BEAM_LINES:
        for c in CENTERS:
            add('Beam', 'VY_Beam_%02d' % b, c, line, 800, 0); b += 1          # along X
            add('Beam', 'VY_Beam_%02d' % b, line, c, 760, 90); b += 1         # along Y, just under
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            if (cx, cy) in MISSING:
                continue
            m = TORN.get((cx, cy)) or COLORS[(gx * 7 + gy * 13 + gx * gy) % 3]
            add(m, 'VY_Canopy_%02d' % j, cx, cy, CANOPY_Z, ((gx * 5 + gy * 3) % 4) * 90); j += 1
    add('EntranceDoor', 'VY_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'VY_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'beams': b, 'canopies': j})
    return out
