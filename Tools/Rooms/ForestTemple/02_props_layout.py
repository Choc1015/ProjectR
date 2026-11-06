import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/ForestTemple/SM_FT_'

def xf(x, y, z=0, yaw=0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

PLACE = [
    ('Arch', -1150, 0, 0, 90, 1), ('Arch', 1150, 0, 0, 90, 1),
    ('WallRuinA', -1150, -600, 0, 90, 1), ('WallRuinB', -1150, 650, 0, 270, 1),
    ('WallRuinB', 1150, -650, 0, 90, 1), ('WallRuinA', 1150, 600, 0, 270, 1),
    ('WallRuinB', -500, 1150, 0, 0, 1), ('WallRuinA', 600, 1150, 0, 0, 1),
    ('WallRuinA', -650, -1150, 0, 180, 1),
    ('Tree', -950, 950, 0, 20, 1), ('Tree', 950, -1000, 0, 140, 1), ('Tree', 1000, 950, 0, 260, 0.85), ('Tree', 150, -1120, 0, 80, 0.9),
    ('Root', -700, 700, 0, 30, 1), ('Root', 720, -760, 0, 200, 1), ('Root', 760, 740, 0, 300, 0.8),
    ('PillarVines', -700, 820, 0, 0, 1), ('PillarVines', 700, -820, 0, 45, 1),
    ('PillarBrokenTall', 400, 860, 0, 15, 1), ('PillarBrokenTall', -420, -860, 0, 200, 1),
    ('PillarBrokenShort', 860, 380, 0, 30, 1), ('PillarBrokenShort', -860, -380, 0, 110, 1), ('PillarBrokenShort', 880, -420, 0, 250, 1),
    ('Altar', 0, 930, 0, 180, 1), ('Statue', 0, 960, 63, 180, 1),
    ('Fountain', -820, -820, 0, 0, 1),
    ('Boulder', -980, 300, 0, 60, 1), ('Boulder', 1000, 250, 0, 210, 0.8), ('Boulder', 450, -1000, 0, 120, 0.9),
    ('Bush', -1000, 480, 0, 0, 1), ('Bush', 1000, 480, 0, 90, 1), ('Bush', 300, -1000, 0, 30, 1), ('Bush', -300, 1000, 0, 60, 1),
    ('Bush', -1020, -250, 0, 10, 0.9), ('Bush', 620, 1000, 0, 200, 0.9),
    ('FernMushroom', -900, -600, 0, 0, 1), ('FernMushroom', 600, 950, 0, 70, 1), ('FernMushroom', 950, -550, 0, 140, 1),
    ('FernMushroom', -600, -1000, 0, 220, 1), ('FernMushroom', -850, 650, 0, 300, 1), ('FernMushroom', 300, 1020, 0, 10, 1),
    ('Flowers', -880, 120, 0, 0, 1), ('Flowers', 880, -150, 0, 90, 1), ('Flowers', 220, 880, 0, 180, 1),
    ('Flowers', -220, -880, 0, 270, 1), ('Flowers', 860, 860, 0, 45, 0.8),
    ('FallenColumn', -250, 260, 0, 30, 1), ('Rubble', 320, -220, 0, 0, 1),
]

def run():
    out = {}
    old = call('scene.SceneTools.find_actors', {'name': 'FT_', 'tag': '', 'collision_channels': []})
    for a in old:
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    out['removed'] = len(old)
    i = 0
    for gx in range(12):
        for gy in range(12):
            call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + 'FloorTile', 'name': 'FT_Floor_%03d' % i,
                 'xform': xf(-1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 3) % 4) * 90)})
            i += 1
    for k, (m, x, y, z, yaw, s) in enumerate(PLACE):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'FT_%s_%02d' % (m, k), 'xform': xf(x, y, z, yaw, s)})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    t = call('scene.SceneTools.find_actors', {'name': 'FT_Arch', 'tag': '', 'collision_channels': []})
    out['arch'] = [call('actor.ActorTools.get_actor_transform', {'actor': a})['location'] for a in t]
    out['placed'] = i + len(PLACE)
    return out
