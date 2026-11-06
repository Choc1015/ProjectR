import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Harbor/SM_HB_'
WATER_Z = -30   # WaterBasin water surface

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# Flooded corner = x, y < -600 (south-west). Wall-attached (Anchor, Oars): S yaw 0, N 180, W 270, E 90.
PLACE = [
    # cover
    ('CrateStack', -250, 250, 0, 15, 1.0), ('BoatOverturned', 350, -250, 0, 30, 1.0),
    # flooded corner: jetty from the floor edge into the water, a boat, a mooring post at the broken edge
    ('Jetty', -750, -900, 0, 0, 1.0), ('Rowboat', -950, -1060, WATER_Z, 10, 1.0), ('MooringPost', -560, -620, 0, 0, 1.0),
    # north-west
    ('NetPile', -950, 950, 0, 20, 1.0), ('Barrels', -1000, 600, 0, 270, 1.0),
    # north band
    ('Anchor', -500, 1190, 0, 180, 1.0), ('Oars', -200, 1190, 0, 180, 1.0), ('CrateTarp', 150, 1060, 0, 10, 1.0),
    ('Barrel', 400, 1080, 0, 30, 1.0), ('LobsterTrap', 700, 1030, 0, 15, 1.0),
    # north-east
    ('Crane', 1000, 1000, 0, 225, 1.0), ('PlankPile', 750, 800, 0, 40, 0.8),
    # east band (exit |y|<300 clear)
    ('Barrels', 1050, 600, 0, 90, 1.0), ('RopeCoil', 1050, -450, 0, 0, 1.0), ('FishBaskets', 1050, -750, 0, 90, 1.0),
    ('CrateStack', 1000, -1030, 0, 0, 1.0),
    # south band (east of the water)
    ('RopeCoil', -350, -1050, 0, 30, 0.9), ('LobsterTrap', 0, -1060, 0, 170, 1.0), ('Barrel', 300, -1080, 0, 0, 1.0),
    ('NetPile', 650, -1030, 0, 160, 0.9),
    # west band (north of the water, entrance |y|<300 clear)
    ('FishBaskets', -1050, -420, 0, 270, 0.9), ('CrateTarp', -1050, 420, 0, 60, 1.0),
    # accent
    ('RopeCoil', 600, 620, 0, 0, 0.7),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'HB_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'HB_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
