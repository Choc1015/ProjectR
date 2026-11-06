import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mill/SM_ML_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# The stream runs along the north wall (y 1000..1200) - the water wheel hangs over it, nothing else stands in it.
# Wall-attached pieces sit 20 cm off the wall line (river-stone base): S yaw 0, N 180, W 270, E 90.
PLACE = [
    # cover
    ('SackPile', -250, -220, 0, 20, 1.0), ('Crates', 320, 300, 0, 10, 1.0),
    # water wheel over the stream, millstones and scale beside it
    ('WaterWheel', -300, 1180, 0, 180, 1.0), ('Millstones', 400, 850, 0, 0, 1.0), ('Scale', 800, 860, 0, 20, 1.0),
    ('Barrel', 1050, 850, 0, 30, 1.0),
    # east band (exit |y|<300 clear)
    ('GrainBin', 1050, 550, 0, 90, 1.0), ('Sacks', 1000, -500, 0, 90, 1.0), ('Cart', 950, -900, 0, 120, 1.0),
    # south band
    ('Workbench', -200, -1180, 0, 0, 1.0), ('MillstoneLeaning', 300, -1180, 0, 0, 1.0), ('Barrel', 650, -1060, 0, 0, 1.0),
    ('Bench', -650, -1050, 0, 0, 1.0), ('Sacks', -1000, -1000, 0, 200, 0.9),
    # west band (entrance |y|<300 clear)
    ('Rope', -1050, -500, 0, 0, 1.0), ('GrainBin', -1050, 550, 0, 270, 1.0), ('Scale', -1000, 820, 0, 300, 0.9),
    # accents at the edge of the open floor
    ('Rope', 600, -600, 0, 60, 0.8), ('SackPile', -650, 600, 0, 140, 0.7),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'ML_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'ML_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
