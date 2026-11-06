import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Forge/SM_FG_'

# molten metal channels (2 m straight pieces) along the west band and the south band
CHANNELS = [(-950, y, 90) for y in (-1000, -800, -600)] + [(x, -950, 0) for x in (400, 600, 800)]

# (mesh, x, y, z, yaw, scale). Middle ~14 m open, two low covers. +Y north, entrance west (-X), exit east (+X).
PLACE = [
    # cover
    ('AnvilBlock', -250, -200, 0, 20, 1.0), ('Ingots', 320, 300, 0, 10, 1.0),
    # north band: the big furnace against the wall, bellows, coal, ore cart
    ('Furnace', -200, 1200, 0, 180, 1.0), ('Bellows', -650, 1000, 0, 180, 1.0), ('CoalPile', 300, 1030, 0, 20, 1.0),
    ('OreCart', 650, 1000, 0, 10, 1.0), ('Barrel', 850, 1090, 0, 30, 1.0),
    # corners
    ('Brazier', 1000, 1000, 0, 0, 1.0), ('Pillar', -950, 850, 0, 0, 1.0), ('Brazier', 1050, -1050, 0, 45, 1.0),
    ('Brazier', -780, -1050, 0, 20, 1.0),
    # west band (channel at x=-950, y -1100..-500; entrance |y|<300 clear)
    ('Trough', -1050, 500, 0, 270, 1.0), ('Grindstone', -1050, 330, 0, 270, 0.9), ('AnvilStump', -760, -400, 0, 30, 1.0),
    # south band (channel at y=-950, x 300..900)
    ('Workbench', -300, -1180, 0, 0, 1.0), ('Barrel', 100, -1080, 0, 10, 1.0), ('WeaponRack', 600, -1190, 0, 0, 1.0),
    # east band (exit |y|<300 clear)
    ('CrateStack', 1050, -700, 0, 90, 1.0), ('CoalPile', 1050, -420, 0, 140, 0.8), ('AnvilStump', 950, 500, 0, 200, 1.0),
    ('Barrel', 1080, 720, 0, 60, 0.9), ('WeaponRack', 1190, 1000, 0, 90, 0.9),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for p in ('FG_Channel_', 'FG_Prop_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (x, y, yaw) in enumerate(CHANNELS):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + 'Channel', 'name': 'FG_Channel_%02d' % k, 'xform': xf(x, y, 0, yaw, 1.0)})
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'FG_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(CHANNELS) + len(PLACE)
    return out
