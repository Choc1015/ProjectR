import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/ForestTemple/'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_'
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
    out = {'rm': 0}
    for p in ('FT_Decor_WallNiche', 'FT_Decor_WallLantern', 'FT_Decor_WallRoots', 'FT_LanternLight_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    for a in ('SM_FT_WallRoots', 'SM_FT_WallNiche', 'SM_FT_WallLantern', 'M_FT_Glass', 'M_FT_Flame'):
        try:
            call('asset.AssetTools.delete', {'path': P + a})
        except Exception as e:
            out['del_' + a] = str(e)[:100]
    for n in ('WallNiche', 'WallLantern'):
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_' + n,
             'source_file': SRC + n + '.fbx', 'import_materials': True})
    k = 0
    for i, (m, side, t, z, s, mirror) in enumerate(DECOR):
        if m not in ('WallNiche', 'WallLantern'):
            continue
        yaw, pos = SIDES[side]
        x, y = pos(t)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + 'SM_FT_' + m, 'name': 'FT_Decor_%s_%02d' % (m, i),
             'xform': {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0},
                       'scale': {'x': -s if mirror else s, 'y': s, 'z': s}}})
        k += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['readded'] = k
    return out
