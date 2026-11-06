import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Greenhouse/SM_GH_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
# Wall-attached pieces (PottingBench, CanRake) sit with their back on the wall line (S yaw 0, N 180, W 270, E 90).
PLACE = [
    # cover
    ('Fountain', -250, -200, 0, 0, 1.0), ('PlanterLow', 350, 320, 0, 15, 1.0),
    # north-west
    ('PotTree', -1000, 1000, 0, 20, 1.0), ('FlowerBed', -500, 1030, 0, 0, 1.0), ('Topiary', -1050, 650, 0, 0, 1.0),
    # north band
    ('PottingBench', 150, 1190, 0, 180, 1.0), ('CanRake', 500, 1190, 0, 180, 1.0), ('Pots', 720, 1050, 0, 30, 1.0),
    # north-east
    ('RoseArch', 950, 950, 0, 45, 1.0),
    # east band (exit |y|<300 clear)
    ('Wildflowers', 1050, 400, 0, 60, 1.0), ('Bench', 1080, 650, 0, 90, 1.0), ('FlowerBed', 1050, -650, 0, 90, 1.0),
    ('Planter', 1060, -1050, 0, 15, 1.0),
    # south band
    ('Wheelbarrow', -500, -1050, 0, 10, 1.0), ('Sacks', -850, -1080, 0, 0, 1.0), ('BirdStatue', 250, -1050, 0, 200, 1.0),
    ('Pots', 600, -1080, 0, 140, 0.9), ('GlassShards', 850, -760, 0, 30, 1.0),
    # west band (entrance |y|<300 clear)
    ('Bench', -1080, -600, 0, 270, 1.0), ('Planter', -1060, 450, 0, 70, 1.0), ('Wildflowers', -1050, -350, 0, 200, 0.9),
    ('PotTree', -1000, -950, 0, 120, 0.9),
    # accents at the edge of the open floor
    ('GlassShards', 550, -560, 0, 110, 0.8), ('Wildflowers', -650, 650, 0, 300, 0.8), ('Topiary', 680, 700, 0, 0, 0.8),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'GH_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'GH_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
