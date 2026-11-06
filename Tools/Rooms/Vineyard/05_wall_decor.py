import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Vineyard/SM_VY_'
FACE = 1188  # stone face is the 1200 line; plinth 12 cm below 40 cm, stone band 8 cm at 4.0-4.25 m (keep decor off it)
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Piers at S -400/800, N -800/400, W -800/400, E -400/800.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallVines', 'S', -900, 60, 1.0, False), ('WallLamp', 'S', 150, 250, 1.0, False), ('WallBanner', 'S', 1000, 450, 1.0, False),
    ('WallBarrelEnd', 'N', -1000, 150, 1.0, False), ('WallShelf', 'N', -150, 220, 1.0, False), ('WallLamp', 'N', 650, 250, 1.0, True),
    ('WallTools', 'W', -550, 150, 1.0, False), ('WallLamp', 'W', 250, 250, 1.0, False), ('WallVines', 'W', 650, 60, 0.9, True),
    ('WallBanner', 'E', -1000, 450, 0.9, True), ('WallLamp', 'E', 250, 250, 1.0, True), ('WallShelf', 'E', 600, 220, 0.9, True),
    ('WallVines', 'E', -700, 60, 0.9, False),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'VY_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'VY_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
