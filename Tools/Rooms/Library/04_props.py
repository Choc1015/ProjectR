import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Library/SM_LB_'

# (mesh, x, y, z, yaw, scale). Middle ~14 m open (round rug), two low covers. +Y north, entrance west (-X), exit east (+X).
# Bookshelves are wall-attached (back 12 cm off the 1200 line, in front of the wall base): S yaw 0, N 180, W 270, E 90. Pillars at S -400/800, N x=800/-400,
# W y=800/-400, E y=-400/800 - shelves are kept between them. 08_lights uses the candle positions below.
PLACE = [
    # cover
    ('BookshelfLow', -250, -250, 0, 30, 1.0), ('Chest', 320, 300, 0, 15, 1.0),
    # south wall
    ('Bookshelf', -800, -1188, 0, 0, 1.0), ('Bookshelf', 100, -1188, 0, 0, 1.0), ('Desk', 560, -1020, 0, 0, 1.0),
    ('ReadingChair', 560, -880, 0, 180, 1.0), ('BookStack', 300, -950, 0, 20, 1.0),
    # north wall
    ('Bookshelf', -250, 1188, 0, 180, 1.0), ('Bookshelf', 560, 1188, 0, 180, 1.0), ('ScrollPile', -650, 1000, 0, 30, 1.0),
    ('Globe', -1000, 1000, 0, 0, 1.0), ('Telescope', 950, 950, 0, 225, 1.0),
    # west wall (entrance |y|<300 clear)
    ('Bookshelf', -1188, 600, 0, 270, 1.0), ('Bookshelf', -1188, -750, 0, 270, 1.0), ('Lectern', -1000, -1000, 0, 45, 1.0),
    ('Candles', -980, -560, 0, 0, 1.0), ('Chest', -1050, 330, 0, 90, 0.9),
    # east wall (exit |y|<300 clear)
    ('Bookshelf', 1188, 550, 0, 90, 1.0), ('Bookshelf', 1188, -750, 0, 90, 1.0), ('CandleStand', 1050, -1050, 0, 0, 1.0),
    ('BookStack', 1050, 330, 0, 200, 0.9), ('ReadingChair', 1000, -450, 0, 270, 1.0),
    # accents at the edge of the open floor
    ('Candles', 650, -700, 0, 40, 1.0), ('ScrollPile', 600, 650, 0, 160, 0.9),
]

def xf(x, y, z, yaw, s):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def run():
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'LB_Prop_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'LB_Prop_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['placed'] = len(PLACE)
    return out
