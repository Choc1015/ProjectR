import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Oasis/SM_OA_'
FACE = 1190  # sandstone face is the 1200 line, blocks stick out 1-3 cm (plinth 15 cm below 40 cm, carved band 8 cm at 5.0-5.4 m)
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallBanner', 'S', -800, 260, 1.0, False), ('WallNiche', 'S', -250, 120, 1.0, False),
    ('WallRelief', 'S', 350, 300, 1.0, False), ('WallSandDrift', 'S', 900, 0, 1.0, True),
    ('WallGrille', 'N', 850, 300, 1.0, False), ('WallShelf', 'N', 300, 150, 1.0, False),
    ('WallCrack', 'N', -250, 100, 1.0, True), ('WallBanner', 'N', -850, 260, 0.9, True),
    ('WallPalmMat', 'W', -700, 60, 1.0, False), ('WallRug', 'W', 500, 120, 1.0, False),
    ('WallNiche', 'W', -320, 120, 0.9, True), ('WallRelief', 'W', 900, 330, 0.8, True),
    ('WallGrille', 'E', -1000, 300, 0.9, True), ('WallRug', 'E', -400, 280, 0.9, True),
    ('WallShelf', 'E', 420, 180, 0.9, True), ('WallCrack', 'E', 700, 200, 0.8, False),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'OA_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'OA_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
