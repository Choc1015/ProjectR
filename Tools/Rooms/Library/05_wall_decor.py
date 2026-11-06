import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Library/SM_LB_'
FACE = 1188  # stone frame face is the 1200 line; base 12 cm below 0.5 m, stone band 8 cm at 5.4-5.6 m
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall in the wall's own X (S t=x, N t=-x, W t=-y, E t=y). Bookshelves are 3 m tall, so decor next to / above them.
# (piece, side, t cm, height cm, scale, mirror)
DECOR = [
    ('WallStarMap', 'S', -300, 300, 1.0, False), ('WallSconce', 'S', 500, 230, 1.0, False), ('WallClock', 'S', 1000, 380, 1.0, False),
    ('WallSconce', 'N', -100, 230, 1.0, True), ('WallStarChart', 'N', -950, 300, 1.0, False), ('WallBanner', 'N', 650, 280, 1.0, False),
    ('WallSconce', 'W', -250, 230, 1.0, False), ('WallShelf', 'W', -950, 180, 1.0, True), ('WallClock', 'W', 1000, 300, 0.9, True),
    ('WallSconce', 'E', 250, 230, 1.0, True), ('WallBanner', 'E', -1000, 280, 0.9, True), ('WallStarChart', 'E', 1000, 300, 0.9, True),
    ('WallShelf', 'E', -550, 180, 1.0, False),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'LB_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'LB_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
