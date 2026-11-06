import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
NAMES = ['FloorTile','Arch','PillarVines','PillarBrokenShort','PillarBrokenTall','FallenColumn','WallRuinA','WallRuinB',
         'Altar','Statue','Fountain','Boulder','Rubble','Tree','Root','Bush','FernMushroom','Flowers']
LV = '/Game/Maps/Rooms/L_Room_ForestTemple'

def run():
    out = {'import': {}}
    for n in NAMES:
        try:
            r = call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_' + n,
                 'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_' + n + '.fbx', 'import_materials': True})
            out['import'][n] = 'ok'
        except Exception as e:
            out['import'][n] = str(e)[:160]
    out['dup'] = call('asset.AssetTools.duplicate', {'path': '/Game/Maps/DevMap', 'new_path': LV})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    call('scene.SceneTools.load_level', {'level_path': LV})
    acts = call('scene.SceneTools.find_actors', {})
    labels = []
    for a in acts:
        labels.append(a['refPath'].split('.')[-1])
    out['actors'] = labels
    return out
