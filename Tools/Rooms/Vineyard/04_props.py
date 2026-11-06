import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Vineyard/SM_VY_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# Piers at S x=-400/800, N x=800/-400, W y=800/-400, E y=-400/800. WineRack is wall-attached (S yaw 0, N 180, W 270, E 90).
PLACE = [
    # cover
    ('CrateStack', -250, -220, 0, 25, 1.0), ('LowWall', 320, 300, 0, 10, 1.0),
    # north-west: the press and baskets
    ('Press', -950, 950, 0, 20, 1.0), ('GrapeBaskets', -650, 1050, 0, 0, 1.0), ('Planter', -1050, 620, 0, 0, 1.0),
    # north band
    ('BarrelStack', 0, 1060, 0, 0, 1.0), ('WineRack', 560, 1188, 0, 180, 1.0), ('GrapeBasket', 300, 950, 0, 40, 1.0),
    # north-east
    ('Trellis', 980, 980, 0, 225, 1.0), ('Crate', 760, 760, 0, 20, 0.8),
    # east band (exit |y|<300 clear)
    ('Barrel', 1030, 550, 0, 90, 1.0), ('BarrelUp', 1060, -450, 0, 0, 1.0), ('Table', 1000, -720, 0, 90, 1.0),
    ('Bench', 820, -720, 0, 90, 1.0), ('Planter', 1050, -1050, 0, 30, 1.0),
    # south band
    ('BarrelStack', -550, -1060, 0, 0, 1.0), ('Crate', 0, -1050, 0, 15, 1.0), ('GrapeBaskets', 300, -1050, 0, 160, 1.0),
    ('WineRack', 600, -1188, 0, 0, 1.0),
    # south-west / west band (entrance |y|<300 clear)
    ('Trellis', -980, -980, 0, 45, 0.9), ('BarrelUp', -1060, -560, 0, 0, 0.9), ('Barrel', -1030, 420, 0, 270, 1.0),
    # accents at the edge of the open floor
    ('GrapeBasket', 650, -650, 0, 0, 0.9), ('Crate', -650, 640, 0, 60, 0.8),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'VY_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'VY_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
