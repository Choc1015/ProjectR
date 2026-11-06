import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Chapel/SM_CP_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# Graves face into the room. 08_lights uses the Candles / Altar positions below.
PLACE = [
    # cover
    ('WallStub', -250, -220, 0, 25, 1.0), ('Coffin', 330, 300, 0, 75, 1.0),
    # north band: the altar between graves
    ('Altar', 0, 1060, 0, 180, 1.0), ('Candles', -350, 1050, 0, 0, 1.0), ('GraveRound', -650, 1050, 0, 185, 1.0),
    ('GraveCross', 350, 1060, 0, 175, 1.0), ('GraveRound', 650, 1030, 0, 160, 0.9), ('Grass', 900, 1050, 0, 30, 1.0),
    # north-west: angel with candles, graves
    ('Angel', -1000, 1000, 0, 225, 1.0), ('Candles', -1000, 780, 0, 40, 0.8), ('GraveSlab', -1000, 450, 0, 90, 1.0),
    # north-east: well and dead tree
    ('Well', 1000, 850, 0, 30, 1.0), ('DeadTree', 1050, 1050, 0, 0, 1.0),
    # east band (exit |y|<300 clear)
    ('Wheelbarrow', 1030, 480, 0, 100, 1.0), ('Bench', 1060, -500, 0, 90, 1.0), ('GraveRound', 1050, -850, 0, 260, 1.0),
    ('Candles', 1000, -1050, 0, 0, 1.0),
    # south band
    ('GraveCross', -700, -1060, 0, 10, 1.0), ('GraveSlab', -300, -1000, 0, 0, 1.0), ('WoodCross', 100, -1080, 0, 5, 1.0),
    ('LanternPost', 450, -1050, 0, 0, 1.0), ('GraveRound', 750, -1060, 0, 350, 0.9), ('Rubble', -1000, -1000, 0, 30, 1.0),
    # west band (entrance |y|<300 clear)
    ('GraveRound', -1050, -450, 0, 80, 0.9), ('Grass', -1050, -700, 0, 200, 1.0), ('WoodCross', -1080, 350, 0, 95, 0.9),
    # accents at the edge of the open floor
    ('Grass', 650, -650, 0, 0, 0.8), ('Candles', -650, 650, 0, 0, 0.6),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'CP_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'CP_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
