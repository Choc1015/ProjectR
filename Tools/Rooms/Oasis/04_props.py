import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Oasis/SM_OA_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m stays open; two low covers in it. +Y = north, entrance west (-X), exit east (+X).
PLACE = [
    # cover in the fighting area
    ('ColumnFallen', -250, -200, 0, 25, 1.0), ('Block', 320, 280, 0, 10, 1.0),
    # north-west corner: the oasis pool with two palms
    ('Pool', -880, 880, 0, 0, 1.0), ('PalmTree', -1060, 620, 0, 30, 1.0), ('PalmTree', -640, 1060, 0, 200, 0.9),
    ('Shrub', -640, 560, 0, 60, 0.7),
    # north band
    ('PotGroup', -300, 1060, 0, 180, 1.0), ('Column', 60, 1080, 0, 0, 1.0), ('Baskets', 330, 1050, 0, 160, 1.0),
    ('CrateCloth', 560, 1080, 0, 15, 1.0),
    # north-east corner
    ('SandDrift', 950, 950, 0, 45, 1.0), ('Rubble', 560, 720, 0, 120, 0.6),
    # east band (exit doorway |y|<300 stays clear)
    ('ColumnStump', 1050, 400, 0, 20, 1.0), ('Shrub', 1070, 640, 0, 200, 0.9), ('Rugs', 1180, -340, 0, 90, 1.0),
    ('Stall', 1000, -650, 0, 90, 1.0), ('Amphora', 1080, -1000, 0, 30, 1.0),
    # south band
    ('Column', -600, -1080, 0, 0, 1.0), ('Rubble', -250, -1020, 0, 0, 1.0), ('StatueHead', 250, -980, 0, 200, 1.0),
    ('Baskets', 620, -1060, 0, 70, 0.9), ('CrateCloth', 850, -1050, 0, 40, 1.0),
    # south-west corner and west band (entrance |y|<300 stays clear)
    ('SandDrift', -950, -950, 0, 225, 0.8), ('PotGroup', -1060, -650, 0, 270, 1.0), ('Column', -1080, -480, 0, 0, 0.9),
    ('Shrub', -1070, -330, 0, 120, 0.8), ('Amphora', -1060, 380, 0, 300, 1.0),
    # accents at the edge of the open floor
    ('ColumnStump', 650, -640, 0, 30, 0.9),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'OA_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'OA_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
