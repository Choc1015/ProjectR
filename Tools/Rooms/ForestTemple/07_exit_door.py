import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/ForestTemple/'
def xf(x, y, z, yaw, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}
def run():
    out = {}
    for a in call('scene.SceneTools.find_actors', {'name': 'FT_ExitDoor', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    for a in ('SM_FT_ExitDoor', 'M_FT_DoorBlack'):
        try: call('asset.AssetTools.delete', {'path': P + a})
        except Exception: pass
    call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_ExitDoor',
         'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_ExitDoor.fbx', 'import_materials': True})
    # exit on the east (+X) wall, facing into the room
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + 'SM_FT_ExitDoor', 'name': 'FT_ExitDoor', 'xform': xf(1198, 0, 0, 90)})
    # keep the doorway clear: move the boulder that sat in front of it
    b = call('scene.SceneTools.find_actors', {'name': 'FT_Boulder_27', 'tag': '', 'collision_channels': []})
    if b:
        call('actor.ActorTools.set_actor_transform', {'actor': b[0], 'xform': xf(980, 720, 0, 210, 0.8)})
    out['boulder_moved'] = bool(b)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
