import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/ForestTemple/SM_FT_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_'

def add(m, name, x, y, yaw, sx=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name,
         'xform': {'location': {'x': x, 'y': y, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': sx, 'y': 1, 'z': 1}}})

def run():
    out = {}
    n = 0
    for p in ('FT_TWall_', 'FT_TWallDoor_'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); n += 1
    out['removed'] = n
    for m in ('TempleWall', 'TempleWallMoss', 'TempleWallDoor'):
        try:
            call('asset.AssetTools.delete', {'path': P + m})
        except Exception:
            pass
    for m in ('TempleWall', 'TempleWallMoss'):
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_' + m,
             'source_file': SRC + m + '.fbx', 'import_materials': True})
    # (side, center) -> mirrored moss variant on only a few modules, irregularly
    moss = {('S', -600): 1.0, ('N', 1000): -1.0, ('W', 200): 1.0, ('E', -1000): -1.0}
    k = 0
    for c in (-1000, -600, -200, 200, 600, 1000):
        for side, x, y, yaw in (('S', c, -1200, 0), ('N', c, 1200, 180), ('W', -1200, c, 270), ('E', 1200, c, 90)):
            sx = moss.get((side, c))
            add('TempleWallMoss' if sx else 'TempleWall', 'FT_TWall_%02d' % k, x, y, yaw, sx or 1.0)
            k += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['walls'] = k
    return out
