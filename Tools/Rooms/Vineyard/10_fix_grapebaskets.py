import json
# Review 2026-11-07: SM_VY_GrapeBaskets flickered - the wood rim/band were closed cylinders whose top caps sat at the
# same height as the basket's top cap (z 0.248 / 0.26). The caps were deleted in blender (open rings) and the FBX re-exported.
# NOTE: the fix was made on an appended copy, so SourceArt/Vineyard_Props.blend still has the old caps
# (delete M_VY_Wood faces that are flat in Z on SM_VY_GrapeBaskets before exporting it again).
# This re-imports that one mesh, then run 04_props again to put the baskets back.
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_Vineyard'})
    out = {'rm': 0}
    for a in call('scene.SceneTools.find_actors', {'name': 'VY_Prop_GrapeBaskets', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    try:
        call('asset.AssetTools.delete', {'path': '/Game/Props/Vineyard/SM_VY_GrapeBaskets'})
        out['del'] = 'ok'
    except Exception as e:
        out['del'] = str(e)[:150]
    call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Vineyard', 'asset_name': 'SM_VY_GrapeBaskets',
         'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/Vineyard/SM_VY_GrapeBaskets.fbx', 'import_materials': True})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
