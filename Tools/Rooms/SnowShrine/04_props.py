import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/SnowShrine/SM_SN_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
PLACE = [
    # cover
    ('SledTilted', -250, -220, 0, 30, 1.0), ('StoneWall', 320, 300, 0, 15, 1.0),
    # north-west: pines and the little shrine facing into the room
    ('PineTree', -1000, 1000, 0, 0, 1.0), ('PineSmall', -760, 1080, 0, 40, 1.0), ('Shrine', -1000, 620, 0, 270, 1.0),
    # north band: two flag posts whose strings meet in the middle, a loaded sled
    ('FlagPost', -450, 1080, 0, 0, 1.0), ('FlagPost', 150, 1080, 0, 180, 1.0),
    ('Sled', 450, 1040, 0, 10, 1.0), ('Barrel', 700, 1090, 0, 20, 1.0),
    # north-east
    ('PineTree', 1000, 1000, 0, 70, 0.9), ('IceRock', 1050, 700, 0, 40, 1.0),
    # east band (exit |y|<300 clear)
    ('LanternPost', 1080, 450, 0, 90, 1.0), ('CrateStack', 1060, -450, 0, 20, 1.0), ('Firewood', 1050, -750, 0, 90, 1.0),
    ('Barrel', 1080, -1000, 0, 60, 0.9),
    # south band
    ('PineTree', 1000, -1020, 0, 150, 0.85), ('Signpost', 200, -1000, 0, 20, 1.0), ('Campfire', -300, -950, 0, 0, 1.0),
    ('Firewood', -650, -1070, 0, 0, 0.9), ('IceRock', -1000, -1000, 0, 200, 1.1),
    # west band (entrance |y|<300 clear)
    ('LanternPost', -1080, -420, 0, 270, 1.0), ('Skis', -1180, -700, 0, 270, 1.0), ('CrateStack', -1050, 380, 0, 70, 0.9),
    # accents at the edge of the open floor
    ('SnowDrift', 600, 620, 0, 30, 0.6), ('IceRock', -650, -640, 0, 300, 0.6), ('PineSmall', 620, -700, 0, 10, 0.8),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'SN_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'SN_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
