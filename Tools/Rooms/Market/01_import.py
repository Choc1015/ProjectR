import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Market/SM_MK_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Market/SM_MK_'
STRUCT = ['Ground', 'Flag_A', 'Flag_B', 'Flag_C', 'Tuft_A', 'Tuft_B', 'HouseFront', 'HouseFrontB', 'Corner', 'EntranceGate', 'ExitDoor']
PROPS = ['StallBlue', 'StallYellow', 'Well', 'CrateApples', 'CrateCabbage', 'CrateStack', 'Barrel', 'Barrels', 'Sacks', 'FlowerCart',
         'HayBarrow', 'Bench', 'JugTable', 'LanternPost', 'Firewood', 'BreadBasket']
DECOR = ['SignBread', 'WindowBox', 'WallLantern', 'OnionString', 'DoorAwning', 'PotShelf', 'SignHorseshoe', 'Ivy', 'NoticeBoard']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Market', 'asset_name': 'SM_MK_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
