import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']

# 인벤토리 그림을 /Game/UI/Inventory 로, Items.csv를 /Game/Data/DT_Items 로 임포트한다(있으면 지우고 다시).
# Items.csv만 고쳤으면 TEXTURES를 비우고 돌려도 된다.
SRC = 'C:/UnrealProject/ProjectR/SourceArt/UI/Inventory/'
TEXTURES = ['T_InventoryBackdrop', 'T_InvSlot', 'T_InvWeaponSlot', 'T_InvGemSlot', 'T_InvSelect',
            'T_Item_Potion', 'T_Item_ManaPotion', 'T_Item_Sword', 'T_Item_Staff',
            'T_Item_Gem_Spin', 'T_Item_Gem_Slam', 'T_Item_Gem_Breath']

def delete(path):
    try:
        call('asset.AssetTools.delete', {'path': path})
    except Exception:
        pass

def run():
    out = {}
    for n in TEXTURES:
        path = '/Game/UI/Inventory/' + n
        delete(path)
        try:
            call('texture.TextureTools.import_file', {'folder_path': '/Game/UI/Inventory', 'asset_name': n, 'source_file': SRC + n + '.png'})
            call('object.ObjectTools.set_properties', {'instance': {'refPath': path + '.' + n},
                 'values': json.dumps({'compressionSettings': 'TC_EditorIcon', 'lODGroup': 'TEXTUREGROUP_UI'})})
        except Exception as e:
            out[n] = str(e)[:200]
    delete('/Game/Data/DT_Items')
    call('data_table.DataTableTools.import_file', {'folder_path': '/Game/Data', 'asset_name': 'DT_Items',
         'source_file': 'C:/UnrealProject/ProjectR/SourceArt/Data/Items.csv', 'schema': {'refPath': '/Script/ProjectR.ItemRow'}})
    out['rows'] = call('data_table.DataTableTools.list_rows', {'data_table': {'refPath': '/Game/Data/DT_Items.DT_Items'}})
    potion = call('data_table.DataTableTools.get_rows', {'data_table': {'refPath': '/Game/Data/DT_Items.DT_Items'}, 'row_names': ['Potion']})
    out['potion'] = str(potion)[:300]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
