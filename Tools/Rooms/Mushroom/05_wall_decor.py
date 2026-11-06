import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mushroom/SM_MU_'
FACE = 1170  # bark ridges bulge up to 30 cm into the room from the 1200 line
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallFungus', 'S', -900, 300, 1.0, False), ('WallIvy', 'S', -300, 150, 1.0, False),
    ('WallGlowCrack', 'S', 300, 60, 1.0, False), ('WallMask', 'S', 900, 220, 1.0, False),
    ('WallSeedPods', 'N', -600, 350, 1.0, False), ('WallShelf', 'N', 300, 160, 1.0, False),
    ('WallMossDrape', 'N', -150, 300, 1.0, True), ('WallNest', 'N', 800, 350, 1.0, False),
    ('WallMoss', 'W', -650, 120, 1.0, False), ('WallGlowCrack', 'W', 600, 60, 0.9, True),
    ('WallFungus', 'W', -1000, 350, 0.9, True), ('WallMask', 'W', 350, 220, 0.9, True),
    ('WallIvy', 'E', -600, 150, 0.9, True), ('WallShelf', 'E', 550, 160, 0.9, True),
    ('WallMossDrape', 'E', -1000, 350, 0.9, False), ('WallSeedPods', 'E', 350, 330, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'MU_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MU_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
