import json
# Floor rework (review 2026-11-07: the 2 m plank tiles read as a tiring checker / stripe grid).
# Following stylized interior refs: ONE plank deck, boards all running the same way (toward the exit, +X), mixed lengths with
# staggered joints, three low-contrast tones. Single mesh made procedurally in blender (the flooded SW corner 6x6 m is left open for the basin).
# Source: SourceArt/Harbor_Floor.blend -> SourceArt/Export/Harbor/SM_HB_Deck.fbx. Replaces 03's floor tiles (03 no longer lays them).
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
AB, THEME = 'HB', 'Harbor'
IMPORT = True     # False after the first run
def run():
    call('scene.SceneTools.load_level', {'level_path': '/Game/Maps/Rooms/L_Room_' + THEME})
    out = {'rm': 0}
    for p in (AB + '_Floor_', AB + '_Deck'):
        for a in call('scene.SceneTools.find_actors', {'name': p, 'tag': '', 'collision_channels': []}):
            call('scene.SceneTools.remove_from_scene', {'actor': a}); out['rm'] += 1
    if IMPORT:
        try:
            call('asset.AssetTools.delete', {'path': '/Game/Props/%s/SM_%s_Deck' % (THEME, AB)})
        except Exception:
            pass
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/' + THEME, 'asset_name': 'SM_%s_Deck' % AB,
             'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/%s/SM_%s_Deck.fbx' % (THEME, AB), 'import_materials': True})
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': '/Game/Props/%s/SM_%s_Deck' % (THEME, AB), 'name': AB + '_Deck',
         'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
