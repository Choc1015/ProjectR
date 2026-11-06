import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mushroom/SM_MU_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Mushroom/SM_MU_'
STRUCT = ['FloorTile', 'FloorTileB', 'MossPatch', 'MossPatchSmall', 'Wall', 'WallB', 'Corner', 'Ceiling', 'CeilingHole',
          'ExitDoor', 'EntranceDoor']
PROPS = ['MushAmber', 'MushPink', 'MushTeal', 'MushTiny', 'Log', 'FlatStone', 'MossRock', 'Fern', 'Bench', 'Table', 'Stump', 'Leaves',
         'SeedString', 'MossMound', 'Signpost', 'Basket']
DECOR = ['WallFungus', 'WallGlowCrack', 'WallMossDrape', 'WallNest', 'WallIvy', 'WallMask', 'WallSeedPods', 'WallShelf', 'WallMoss']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Mushroom', 'asset_name': 'SM_MU_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
