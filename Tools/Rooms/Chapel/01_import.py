import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Chapel/SM_CP_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Chapel/SM_CP_'
STRUCT = ['FloorTile', 'FloorTileB', 'GrassPatch', 'GrassPatchSmall', 'Wall', 'WallWindow', 'Post', 'Corner', 'Rafter', 'Roof',
          'RoofBroken', 'ExitDoor', 'EntranceDoor']
PROPS = ['GraveRound', 'GraveCross', 'GraveSlab', 'Angel', 'WallStub', 'Coffin', 'Candles', 'Altar', 'LanternPost', 'Grass', 'Bench',
         'Wheelbarrow', 'Well', 'DeadTree', 'Rubble', 'WoodCross']
DECOR = ['WallCandelabra', 'WallPlaque', 'WallIvy', 'WallBanner', 'WallNiche', 'WallLantern', 'WallFlowers', 'WallShelf']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Chapel', 'asset_name': 'SM_CP_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
