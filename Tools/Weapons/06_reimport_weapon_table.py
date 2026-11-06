import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
# Weapons.csv만 고쳤을 때: DT_Weapons를 지우고 다시 임포트한다(캐릭터·바닥 무기는 경로로 찾으니 따로 연결할 것 없음).
def run():
    try:
        call('asset.AssetTools.delete', {'path': '/Game/Data/DT_Weapons'})
    except Exception:
        pass
    call('data_table.DataTableTools.import_file', {'folder_path': '/Game/Data', 'asset_name': 'DT_Weapons',
         'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Data/Weapons.csv', 'schema': {'refPath': '/Script/ProjectR.WeaponRow'}})
    row = call('data_table.DataTableTools.get_rows', {'data_table': {'refPath': '/Game/Data/DT_Weapons.DT_Weapons'}, 'row_names': ['Staff']})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'staff_offset': json.loads(row)['Staff']['meshOffsetLocation'] if isinstance(row, str) else str(row)[:300]}
