import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Harbor/SM_HB_'
FACE = 1192  # plank face is the 1200 line, planks step 1-2 cm
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Posts at S -400/800, N -400/800, W -800/400, E -800/400.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallGap', 'S', -900, 250, 1.0, False), ('WallSail', 'S', -150, 250, 1.0, False),
    ('WallFish', 'S', 350, 280, 1.0, False), ('WallBoard', 'S', 1000, 180, 1.0, False),
    ('WallNet', 'N', -800, 150, 1.0, False), ('WallRing', 'N', 150, 250, 1.0, False),
    ('WallShelf', 'N', 550, 200, 1.0, True), ('WallGap', 'N', -350, 400, 0.8, True),
    ('WallRope', 'W', -650, 150, 1.0, False), ('WallOars', 'W', 550, 250, 1.0, True),
    ('WallFish', 'W', -950, 300, 0.9, True), ('WallGap', 'W', 950, 250, 1.1, False),
    ('WallNet', 'E', -500, 150, 0.9, True), ('WallBoard', 'E', 700, 180, 0.9, True),
    ('WallRing', 'E', -1000, 250, 0.9, False), ('WallSail', 'E', -300, 260, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'HB_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'HB_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
