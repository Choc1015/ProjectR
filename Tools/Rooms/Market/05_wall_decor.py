import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Market/SM_MK_'
FACE = 1194  # plaster face is the 1200 line, timber trims stand 3-5 cm out
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (-t, FACE)), 'W': (270, lambda t: (-FACE, -t)), 'E': (90, lambda t: (FACE, t))}
# t along the wall (S t=x, N t=-x, W t=-y, E t=y). Module seams at t = -800/-400/0/400/800. House front windows (module-local x): upper floor
# +-95 at z 330-450, ground window +100 at z 100-180 (A type), B type door at -90 z 0-210. Entrance W t=0 / exit E t=0 kept free below 4.4 m.
# (piece, side, t, z, scale, mirror)
DECOR = [
    ('WindowBox', 'S', -295, 300, 1.0, False), ('SignBread', 'S', 0, 260, 1.0, False), ('WallLantern', 'S', 400, 230, 1.0, False),
    ('OnionString', 'S', 870, 140, 1.0, False),
    ('DoorAwning', 'N', 110, 215, 1.0, False), ('PotShelf', 'N', -330, 170, 1.0, True), ('SignHorseshoe', 'N', -800, 260, 1.0, True),
    ('WindowBox', 'N', 905, 300, 1.0, True), ('Ivy', 'N', -1080, 30, 1.0, False),
    ('WallLantern', 'W', -400, 230, 1.0, False), ('WallLantern', 'W', 400, 230, 1.0, True), ('NoticeBoard', 'W', -800, 110, 1.0, False),
    ('WindowBox', 'W', 905, 300, 0.9, False),
    ('WallLantern', 'E', -400, 230, 1.0, False), ('WallLantern', 'E', 400, 230, 1.0, True), ('Ivy', 'E', 800, 30, 0.9, True),
    ('SignBread', 'E', -800, 260, 0.9, True),
]

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'MK_Decor_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MK_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(DECOR)
    return out
