import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mill/SM_ML_'
# wall = river-stone base up to 2 m sticking 20 cm into the room, half-timber above (timber 8 cm out, plaster on the line)
def face(z):
    return 1176 if z < 200 else 1190
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Posts at S -400/800, W -800/400, E -400/800.
# The water wheel covers N t=50..550 (x -550..-50) up to 4.7 m. (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallTools', 'S', -800, 230, 1.0, False), ('WallSign', 'S', 500, 320, 1.0, False),
    ('WallLantern', 'S', -300, 260, 1.0, False), ('WallCloth', 'S', 1000, 230, 1.0, True),
    ('WallWheat', 'N', -500, 300, 1.0, False), ('WallShelf', 'N', 900, 280, 1.0, False), ('WallLantern', 'N', -1000, 280, 1.0, True),
    ('WallRope', 'W', -650, 220, 1.0, False), ('WallLantern', 'W', 250, 280, 1.0, False), ('WallWheat', 'W', 800, 300, 0.9, True),
    ('WallShelf', 'E', -700, 280, 0.9, True), ('WallLantern', 'E', 250, 280, 1.0, True), ('WallTools', 'E', 600, 230, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'ML_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t, face(z))
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'ML_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
