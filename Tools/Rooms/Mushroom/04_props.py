import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mushroom/SM_MU_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# The four big glowing mushroom clusters sit in the corners; 08_lights puts a coloured light in each (keep the two lists in sync).
PLACE = [
    # cover
    ('Log', -250, -200, 0, 25, 1.0), ('FlatStone', 330, 300, 0, 10, 1.0),
    # glowing clusters (corners)
    ('MushAmber', -950, 900, 0, 20, 1.0), ('MushPink', 1000, 950, 0, 200, 1.0), ('MushTeal', 980, -1000, 0, 120, 1.0),
    ('MushAmber', -1000, -950, 0, 300, 0.85),
    # north-west / north band
    ('Fern', -650, 1050, 0, 30, 1.0), ('MossRock', -1050, 550, 0, 60, 1.0), ('Bench', -200, 1080, 0, 0, 1.0),
    ('Table', 150, 1060, 0, 10, 1.0), ('Stump', 450, 1050, 0, 140, 1.0), ('SeedString', 750, 1000, 0, 0, 1.0),
    # east band (exit |y|<300 clear)
    ('MushTiny', 1060, 450, 0, 40, 1.0), ('Fern', 1060, 680, 0, 200, 0.9), ('Basket', 1080, -400, 0, 30, 1.0),
    ('MossMound', 1000, -700, 0, 60, 1.0),
    # south band
    ('Bench', -500, -1070, 0, 0, 1.0), ('Leaves', -100, -1000, 0, 0, 1.0), ('Signpost', 250, -1080, 0, 10, 1.0),
    ('MossRock', 550, -1050, 0, 200, 0.9), ('MushTiny', -780, -1060, 0, 110, 1.0),
    # west band (entrance |y|<300 clear)
    ('Stump', -1050, -450, 0, 20, 0.9), ('Fern', -1060, 400, 0, 90, 0.9), ('MushTiny', -1080, -650, 0, 250, 0.9),
    # accents at the edge of the open floor
    ('MushTiny', 650, -650, 0, 0, 0.8), ('Leaves', -650, 600, 0, 120, 0.8), ('MossMound', 600, 700, 0, 300, 0.7),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'MU_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MU_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
