import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
P = '/Game/Props/ForestTemple/SM_FT_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_'
NEW = ['WallIvy', 'WallMossDrape', 'WallRelief', 'WallNiche', 'WallLantern', 'WallCrack', 'WallBanner', 'WallRoots', 'WallLedge']
FACE = 1192  # wall interior plane is 1200; sit 8 cm inside so plinth/cornice don't swallow pieces
SIDES = {'S': (0, lambda t: (t, -FACE)), 'N': (180, lambda t: (t, FACE)), 'W': (270, lambda t: (-FACE, t)), 'E': (90, lambda t: (FACE, t))}

# (piece, side, position along wall cm, height cm, scale, mirror)
DECOR = [
    ('WallIvy', 'S', -820, 0, 1.0, False), ('WallLantern', 'S', -140, 230, 1.0, False), ('WallBanner', 'S', 430, 610, 1.0, False),
    ('WallCrack', 'S', 960, 140, 1.0, True),
    ('WallMossDrape', 'N', -880, 785, 1.0, False), ('WallRoots', 'N', -330, 260, 1.0, False), ('WallLantern', 'N', 260, 230, 1.0, True),
    ('WallRelief', 'N', 720, 170, 1.0, False),
    ('WallIvy', 'W', -980, 0, 0.8, True), ('WallNiche', 'W', -480, 110, 1.0, False), ('WallMossDrape', 'W', 170, 785, 0.85, True),
    ('WallLedge', 'W', 690, 230, 1.0, False),
    ('WallMossDrape', 'E', -1010, 785, 0.7, False), ('WallBanner', 'E', -330, 620, 0.95, True), ('WallLantern', 'E', 380, 230, 1.0, False),
    ('WallCrack', 'E', 820, 290, 0.8, False), ('WallIvy', 'E', 1020, 0, 0.7, False),
]

def run():
    out = {}
    for a in call('scene.SceneTools.find_actors', {'name': 'FT_Decor_', 'tag': '', 'collision_channels': []}) + \
             call('scene.SceneTools.find_actors', {'name': 'FT_LanternLight_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for n in NEW:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_' + n,
             'source_file': SRC + n + '.fbx', 'import_materials': True})
    lights = []
    for k, (m, side, t, z, s, mirror) in enumerate(DECOR):
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': 'FT_Decor_%s_%02d' % (m, k),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
        if m == 'WallLantern':
            # small warm light just in front of the lantern glass
            ox = {'S': (0, 60), 'N': (0, -60), 'W': (60, 0), 'E': (-60, 0)}[side]
            lights.append((x + ox[0], y + ox[1], z + 40))
    for j, (x, y, z) in enumerate(lights):
        a = call('scene.SceneTools.add_to_scene_from_class', {'actor_type': ref('/Script/Engine.PointLight'), 'name': 'FT_LanternLight_%02d' % j,
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        comp = {'refPath': a['refPath'] + '.LightComponent0'}
        call('object.ObjectTools.set_properties', {'instance': comp, 'values': json.dumps(
            {'intensity': 1500, 'attenuationRadius': 700, 'lightColor': {'r': 255, 'g': 190, 'b': 120, 'a': 255}})})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['decor'] = len(DECOR); out['lights'] = len(lights)
    return out
