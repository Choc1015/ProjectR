import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Market/SM_MK_'
OA = '/Game/Props/Oasis/SM_OA_'      # beam grid + cloth canopies are shared with the oasis (same faded blue / straw / terracotta cloth)
# wall sides: yaw so the blender -Y face points into the room; t = position along the wall in the wall mesh's own X
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

# house fronts: B type (door, other windows) and mirrors mixed irregularly so no two neighbours look alike
WALLB = {('S', -600), ('S', 600), ('N', -1000), ('N', 200), ('W', -1000), ('W', 600), ('E', -600), ('E', 1000)}
MIRROR = {('S', 200), ('S', -1000), ('N', -600), ('N', 600), ('W', -600), ('W', 1000), ('E', 600), ('E', -1000)}

# ceiling: beam grid (X beams at the wall top, Y beams just under), cloth awnings in the cells, some missing so dawn light falls in
BEAM_LINES = (-800, -400, 0, 400, 800)
CANOPY_Z = 720
MISSING = {(-200, 200), (600, -600), (-600, -1000), (1000, 600)}
TORN = {(200, -200): 'CanopyTorn_Red', (-1000, 200): 'CanopyTorn_Blue', (600, 1000): 'CanopyTorn_Blue'}
COLORS = ('Canopy_Blue', 'Canopy_Yellow', 'Canopy_Red')

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(path, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': path, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_Market'})
    out = {'rm': 0}
    for p in ('MK_Wall_', 'MK_Corner_', 'MK_Beam_', 'MK_Canopy_', 'MK_Entrance', 'MK_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add(P + ('HouseFrontB' if (side, c) in WALLB else 'HouseFront'), 'MK_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (x, y, yaw) in enumerate([(-1200, -1200, 0), (1200, -1200, 90), (-1200, 1200, 270), (1200, 1200, 180)]):
        add(P + 'Corner', 'MK_Corner_%02d' % j, x, y, 0, yaw)
    b = 0
    for line in BEAM_LINES:
        for c in CENTERS:
            add(OA + 'Beam', 'MK_Beam_%02d' % b, c, line, 800, 0); b += 1
            add(OA + 'Beam', 'MK_Beam_%02d' % b, line, c, 760, 90); b += 1
    j = 0
    for gx, cx in enumerate(CENTERS):
        for gy, cy in enumerate(CENTERS):
            if (cx, cy) in MISSING:
                continue
            m = TORN[(cx, cy)] if (cx, cy) in TORN else COLORS[(gx * 5 + gy * 11 + gx * gy) % 3]
            add(OA + m, 'MK_Canopy_%02d' % j, cx, cy, CANOPY_Z, ((gx * 5 + gy * 3) % 4) * 90); j += 1
    add(P + 'EntranceGate', 'MK_Entrance', -1200, 0, 0, 270)
    add(P + 'ExitDoor', 'MK_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'walls': k, 'beams': b, 'canopies': j})
    return out
