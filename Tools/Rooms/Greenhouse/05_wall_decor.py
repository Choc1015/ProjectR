import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Greenhouse/SM_GH_'
# wall = stone base 1.2 m tall sticking 25 cm into the room, iron frame + glass above it (frame front 5 cm in)
def face(z):
    return 1172 if z < 125 else 1192
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Iron posts at S -800/400, N -400/800, W -400/800, E -800/400.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallIvy', 'S', -300, 130, 1.0, False), ('WallBasket', 'S', 150, 300, 1.0, False),
    ('WallTools', 'S', 650, 180, 1.0, False), ('WallIvyLow', 'S', 1000, 0, 1.0, True),
    ('WallSunshade', 'N', -150, 200, 1.0, False), ('WallShelf', 'N', 550, 180, 1.0, False),
    ('WallIvy', 'N', -650, 130, 1.0, True), ('WallNest', 'N', 1000, 300, 1.0, False),
    ('WallRoses', 'W', -700, 140, 1.0, False), ('WallPlanterBox', 'W', 300, 160, 1.0, False),
    ('WallIvyLow', 'W', -1000, 0, 0.9, False), ('WallBasket', 'W', 650, 250, 0.9, True),
    ('WallTools', 'E', -300, 180, 0.9, True), ('WallIvy', 'E', 650, 130, 0.9, False),
    ('WallBasket', 'E', -1000, 280, 1.0, False), ('WallPlanterBox', 'E', 300, 160, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'GH_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t, face(z))
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'GH_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
