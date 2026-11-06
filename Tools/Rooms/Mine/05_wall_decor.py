import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mine/SM_MN_'
FACE = 1175  # rock faces bulge up to 25 cm into the room from the 1200 line; decor backs sit just in front
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t is along the wall in the wall's own X (same as FRAMES in 03_shell). Frames sit at S -800/400, N -400/800, W -800/800, E -800/400.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallCrystal', 'S', -1000, 420, 0.8, False), ('WallCrystalVein', 'S', -350, 300, 1.0, False),
    ('WallShelf', 'S', 400, 150, 1.0, False), ('WallTarp', 'S', 860, 240, 0.9, True),
    ('WallBoards', 'N', -860, 60, 1.0, False), ('WallSign', 'N', -400, 210, 1.0, False),
    ('WallCrystal', 'N', 250, 520, 1.0, True), ('WallChain', 'N', 800, 380, 1.0, False),
    ('WallRopeHook', 'W', -800, 110, 1.0, False), ('WallCrystalVein', 'W', -420, 460, 0.8, True),
    ('WallNiche', 'W', 450, 120, 1.0, False), ('WallCrystal', 'W', 1000, 250, 0.7, False),
    ('WallCrystalVein', 'E', -1080, 200, 0.8, False), ('WallChain', 'E', -800, 400, 0.9, True),
    ('WallTarp', 'E', -450, 280, 1.0, False), ('WallShelf', 'E', 800, 160, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'MN_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MN_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
