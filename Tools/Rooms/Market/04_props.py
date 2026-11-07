import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Market/SM_MK_'

# (mesh, x, y, z, yaw, scale). +Y north, entrance west (-X), exit east (+X); doors keep |y| < 300 clear.
# Middle ~14 m open; the well is the low cover off-centre, a crate stack the second. Prop fronts (blender -Y -> Unreal +Y) face the middle:
# south band yaw 0, north 180, west band 270 (faces +X), east band 90 - same yaws as the walls in 03.
PLACE = [
    # cover
    ('Well', 300, -250, 0, 20, 1.0), ('CrateStack', -350, 300, 0, 35, 1.0),
    # north band (stalls face south = yaw 180)
    ('StallBlue', -700, 1000, 0, 180, 1.0), ('CrateApples', -330, 980, 0, 170, 1.0), ('StallYellow', 150, 1000, 0, 180, 1.0),
    ('BreadBasket', 520, 1020, 0, 0, 1.0), ('Barrels', 800, 1030, 0, 160, 1.0), ('LanternPost', -1000, 900, 0, 0, 1.0),
    # south band (stalls face north = yaw 0)
    ('StallYellow', -500, -1000, 0, 0, 1.0), ('CrateCabbage', -150, -980, 0, 10, 1.0), ('Sacks', 150, -1030, 0, 200, 1.0),
    ('StallBlue', 550, -1000, 0, 0, 1.0), ('Firewood', 950, -1050, 0, 0, 1.0), ('LanternPost', -1000, -950, 0, 0, 1.0),
    # west band (entrance at y 0): cart and bench beside the gate
    ('FlowerCart', -1030, 550, 0, 270, 1.0), ('Bench', -1080, -550, 0, 90, 1.0), ('Barrel', -1060, -800, 0, 0, 1.0),
    # east band (exit at y 0)
    ('HayBarrow', 1020, 600, 0, 110, 1.0), ('JugTable', 1030, -550, 0, 90, 1.0), ('Barrel', 1070, -780, 0, 30, 0.9),
    ('CrateStack', 1010, 1000, 0, 10, 0.9),
    # accents at the edge of the open floor
    ('CrateApples', 650, 600, 0, 40, 0.9), ('Sacks', -650, -620, 0, 70, 0.8),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'MK_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MK_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
