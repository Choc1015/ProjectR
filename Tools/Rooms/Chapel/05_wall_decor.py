import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Chapel/SM_CP_'
# wall = stone base up to 2 m sticking 15 cm into the room, plaster above (timber trim 6 cm out)
def face(z):
    return 1180 if z < 200 else 1192
SIDES = {'S': (0, lambda t, d: (t, -d)), 'N': (180, lambda t, d: (-t, d)), 'W': (270, lambda t, d: (-d, -t)), 'E': (90, lambda t, d: (d, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Posts at S -800/400, N -400/800, W -800/400, E -400/800.
# Windows (3.2-4.8 m) on S -600/600, N -200/1000, W -1000/600, E -600/1000 - decor kept off them. (piece, side, t, z, scale, mirror)
DECOR = [
    ('WallCandelabra', 'S', -200, 240, 1.0, False), ('WallPlaque', 'S', 200, 220, 1.0, False), ('WallIvy', 'S', 1000, 220, 1.0, True),
    ('WallBanner', 'N', 200, 300, 1.0, False), ('WallNiche', 'N', -600, 220, 1.0, False), ('WallCandelabra', 'N', 600, 240, 1.0, True),
    ('WallLantern', 'W', -250, 260, 1.0, False), ('WallFlowers', 'W', 250, 250, 1.0, True), ('WallShelf', 'W', -600, 230, 1.0, False),
    ('WallLantern', 'E', 250, 260, 1.0, True), ('WallCandelabra', 'E', -1000, 240, 0.9, False), ('WallPlaque', 'E', 600, 220, 0.9, True),
    ('WallIvy', 'E', -200, 220, 0.9, False),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'CP_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t, face(z))
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'CP_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
