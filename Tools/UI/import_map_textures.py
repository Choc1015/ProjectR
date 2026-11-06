import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']

# 방 지도 UI 그림을 /Game/UI/Map 으로 임포트한다(같은 이름이 있으면 지우고 다시).
NAMES = ['T_MapBackdrop', 'T_MapNode_Combat', 'T_MapNode_Start', 'T_MapNode_Current', 'T_MapCross']

def run():
    out = {}
    for n in NAMES:
        path = '/Game/UI/Map/' + n
        try:
            call('asset.AssetTools.delete', {'asset_paths': [path]})
        except Exception:
            pass
        try:
            call('texture.TextureTools.import_file', {'folder_path': '/Game/UI/Map', 'asset_name': n,
                 'source_file': 'C:/UnrealProject/ProjectR/SourceArt/UI/Map/' + n + '.png'})
            call('object.ObjectTools.set_properties', {'instance': {'refPath': path + '.' + n},
                 'values': json.dumps({'compressionSettings': 'TC_EditorIcon', 'lODGroup': 'TEXTUREGROUP_UI'})})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:200]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
