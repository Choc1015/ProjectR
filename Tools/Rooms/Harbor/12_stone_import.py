import json
# Review 2026-11-07: stone warehouse walls + plain timber roof (SourceArt/Harbor_Walls.blend). Import these, then run 03 and 05 again.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
NEW = ['StoneWall', 'StoneWallB', 'StoneCorner', 'RoofPlain']
def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_Harbor'})
    out = {}
    for p in ('HB_Wall_', 'HB_Corner_', 'HB_Roof_'):        # actors using the meshes go first (03 puts them back)
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a})
    for n in NEW:
        try:
            call('asset.AssetTools.delete', {'path': '/Game/Props/Harbor/SM_HB_' + n})
        except Exception:
            pass
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Harbor', 'asset_name': 'SM_HB_' + n,
             'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/Harbor/SM_HB_' + n + '.fbx', 'import_materials': True})
        out[n] = 'ok'
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
