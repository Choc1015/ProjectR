import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mine/SM_MN_'
RAIL_Z = 14  # cart wheels sit on the rail tops

# rails: along the north wall heading +X, a quarter curve turning south, then down the east side toward the exit
RAILS = [('RailStraight', x, 850, 0) for x in (-800, -600, -400, -200, 0, 200, 400, 600)] + \
        [('RailCurve', 700, 850, 0)] + [('RailStraight', 900, y, 90) for y in (550, 350)]

# (mesh, x, y, z, yaw, scale). Middle ~14 m stays open; only two low covers in it.
PLACE = [
    # cover in the fighting area
    ('CartOverturned', -250, -250, 0, 30, 1.0), ('CrateStack', 300, 300, 0, 15, 0.9),
    # north band, behind the rails
    ('OreCart', -300, 850, RAIL_Z, 0, 1.0), ('Barrel', -950, 1060, 0, 0, 1.0), ('Barrel', -150, 1080, 0, 40, 0.9),
    ('PickShovel', -520, 1180, 0, 180, 1.0), ('Pulley', 120, 1040, 0, 160, 1.0), ('OreCrate', 470, 1060, 0, 10, 1.0),
    ('CrystalLarge', 1000, 1000, 0, 30, 1.0),
    # east band, rails at x=900 (y 250..650); exit doorway |y|<300 stays clear
    ('OreCart', 900, 420, RAIL_Z, 90, 1.0), ('CrystalSmall', 1060, 700, 0, 70, 0.9),
    ('Workbench', 1180, -400, 0, 90, 1.0), ('CrystalSmall', 1080, -800, 0, 200, 0.8), ('Barrel', 1040, -1000, 0, 15, 1.0),
    ('OreCrate', 880, -1060, 0, 25, 0.9),
    # south band
    ('LadderBroken', -300, -1180, 0, 0, 1.0), ('Rubble', 220, -1000, 0, 0, 1.0), ('CrystalLarge', -620, -1000, 0, 200, 0.8),
    ('OreCrate', 620, -1060, 0, 50, 1.0), ('Barrel', 760, -1080, 0, 0, 0.85), ('CrystalSmall', 860, -880, 0, 120, 1.0),
    # west band, boarded tunnel at y=0
    ('Rubble', -1000, -420, 0, 90, 0.9), ('CrateStack', -980, -960, 0, 40, 1.0), ('OreCrate', -1020, -690, 0, 70, 1.0),
    ('CrateStack', -1000, 600, 0, 70, 0.9), ('CrystalSmall', -1060, 950, 0, 10, 1.0), ('CrystalLarge', -1020, 330, 0, 250, 0.7),
    # small crystals at the edge of the open floor
    ('CrystalSmall', 660, -660, 0, 40, 0.7), ('CrystalSmall', -690, 620, 0, 300, 0.6), ('Rubble', 520, -800, 0, 160, 0.6),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for p in ('MN_Rail_', 'MN_Prop_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, yaw) in enumerate(RAILS):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MN_Rail_%02d' % k, 'xform': xf(x, y, 0, yaw, 1.0)})
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'MN_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(RAILS) + len(PLACE)
    return out
