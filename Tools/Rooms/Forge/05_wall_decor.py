import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Forge/SM_FG_'
FACE = 1188  # stone face is the 1200 line, blocks stick out 1-3 cm, plinth 12 cm below 40 cm
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Pilasters at S -400/800, N -400/800, W -800/400, E -400/800.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallShield', 'S', -800, 250, 1.0, False), ('WallBanner', 'S', 100, 300, 1.0, False),
    ('WallVent', 'S', 350, 60, 1.0, False), ('WallAxes', 'S', 1000, 300, 0.9, True),
    ('WallChains', 'N', -150, 380, 1.0, False), ('WallRelief', 'N', -650, 300, 1.0, False),
    ('WallToolRack', 'N', 650, 200, 1.0, True), ('WallBrazier', 'N', 1000, 250, 1.0, False),
    ('WallBrazier', 'W', -600, 250, 1.0, True), ('WallShelf', 'W', 750, 160, 1.0, False),
    ('WallBanner', 'W', -950, 300, 0.9, True), ('WallVent', 'W', 220, 60, 0.9, True),
    ('WallShield', 'E', -700, 250, 0.9, True), ('WallChains', 'E', -1000, 380, 0.9, True),
    ('WallRelief', 'E', 550, 300, 0.9, True), ('WallBrazier', 'E', 300, 250, 0.9, False),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'FG_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'FG_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
