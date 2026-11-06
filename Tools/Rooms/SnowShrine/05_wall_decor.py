import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/SnowShrine/SM_SN_'
FACE = 1188  # stone face is the 1200 line; blocks 1-3 cm, plinth 12 cm below 40 cm, timber band 25 cm at z 3.0-3.3 (keep decor off it)
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Posts at S -800/400, N -400/800, W -400/800, E -800/400.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallPelt', 'S', -950, 120, 1.0, False), ('WallIcicles', 'S', -400, 450, 1.0, False), ('WallShield', 'S', 150, 80, 1.0, False),
    ('WallSnowDrift', 'S', 650, 0, 1.0, True), ('WallWindow', 'S', 850, 450, 1.0, False),
    ('WallFlags', 'N', -700, 420, 1.0, False), ('WallSpiritShelf', 'N', 300, 130, 1.0, False),
    ('WallFrostCrack', 'N', -100, 120, 1.0, True), ('WallWindow', 'N', 550, 450, 0.9, True),
    ('WallIcicles', 'W', -750, 450, 0.9, True), ('WallPelt', 'W', 350, 150, 0.9, True),
    ('WallShield', 'W', 1000, 150, 0.9, True), ('WallWindow', 'W', -600, 420, 0.9, False),
    ('WallSnowshoes', 'E', -300, 100, 1.0, False), ('WallIcicles', 'E', 650, 450, 1.0, True),
    ('WallPelt', 'E', -1000, 150, 0.9, False), ('WallFlags', 'E', 250, 450, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'SN_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'SN_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
