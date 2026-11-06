import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mine/SM_MN_'
# wall sides: yaw so the blender -Y face points into the room, and (x, y) from a position t along the wall
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
CENTERS = (-1000, -600, -200, 200, 600, 1000)

# rock wall module per (side, center): B variant / mirrored, mixed irregularly so no pattern repeats
WALLB = {('S', -600), ('S', 600), ('N', -1000), ('N', 200), ('W', -200), ('W', 1000), ('E', -600), ('E', 600)}
MIRROR = {('S', 200), ('S', -1000), ('N', -600), ('N', 600), ('W', -1000), ('W', 600), ('E', -200), ('E', 1000)}
# timber support frames against the walls (side, t) - they also cover module seams
FRAMES = [('S', -800), ('S', 400), ('N', -400), ('N', 800), ('W', -800), ('W', 800), ('E', -800), ('E', 400)]
# ceiling: three cracked slabs where daylight falls in, everything else solid
CRACKS = {(-200, 200): 'CeilingCrack', (600, -600): 'CeilingCrackB', (-600, -1000): 'CeilingCrackB'}
BEAM_ROWS = (-1050, -300, 700)  # y of beam lines running along X under the ceiling (kept off the crack holes)
DIRT = [('DirtPatch', -480, -320, 25), ('DirtPatch', 430, 520, 160), ('DirtPatchSmall', 120, -640, 75),
        ('DirtPatchSmall', -720, 380, 210), ('DirtPatch', 780, -420, 300), ('DirtPatchSmall', -160, 760, 340)]

def xf(x, y, z=0, yaw=0, sx=1.0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx * s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, sx=1.0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, sx, s)})

def run():
    out = {'rm': 0}
    for p in ('MN_Floor_', 'MN_Dirt_', 'MN_Wall_', 'MN_Corner_', 'MN_Ceiling_', 'MN_Beam_', 'MN_Frame_', 'MN_Entrance', 'MN_ExitDoor'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    # floor: two tile kinds, rotated in 90 degree steps
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3) % 3 == 0 else 'FloorTile'
            add(m, 'MN_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90); i += 1
    for k, (m, x, y, yaw) in enumerate(DIRT):
        add(m, 'MN_Dirt_%02d' % k, x, y, 0, yaw)
    # rock walls 6 per side
    k = 0
    for side, (yaw, pos) in SIDES.items():
        for c in CENTERS:
            x, y = pos(c, 1200)
            add('RockWallB' if (side, c) in WALLB else 'RockWall', 'MN_Wall_%02d' % k, x, y, 0, yaw, -1.0 if (side, c) in MIRROR else 1.0); k += 1
    for j, (x, y, yaw) in enumerate([(-1220, -1220, 0), (1220, -1220, 90), (-1220, 1220, 270), (1220, 1220, 180)]):
        add('RockCorner', 'MN_Corner_%02d' % j, x, y, 0, yaw)
    # ceiling 6x6 at 8 m
    j = 0
    for cx in CENTERS:
        for cy in CENTERS:
            add(CRACKS.get((cx, cy), 'Ceiling'), 'MN_Ceiling_%02d' % j, cx, cy, 800, ((cx + cy) // 400 % 4) * 90); j += 1
    b = 0
    for y in BEAM_ROWS:
        for cx in CENTERS:
            add('CeilingBeam', 'MN_Beam_%02d' % b, cx, y, 800, 0); b += 1
    for f, (side, t) in enumerate(FRAMES):
        yaw, pos = SIDES[side]
        x, y = pos(t, 1200)
        add('SupportFrame', 'MN_Frame_%02d' % f, x, y, 0, yaw)
    # boarded tunnel on the west wall (start side), exit tunnel filled black on the east wall, no threshold
    add('TunnelEntrance', 'MN_Entrance', -1200, 0, 0, 270)
    add('ExitDoor', 'MN_ExitDoor', 1200, 0, 0, 90)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out.update({'floor': i, 'walls': k, 'ceiling': j, 'beams': b, 'frames': len(FRAMES)})
    return out
