import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Harbor/SM_HB_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Harbor/SM_HB_'
STRUCT = ['FloorTile', 'FloorTileB', 'Wall', 'WallB', 'Post', 'Corner', 'Rafter', 'Roof', 'RoofBroken', 'WaterBasin',
          'ExitDoor', 'EntranceDoor']
PROPS = ['CrateStack', 'BoatOverturned', 'Rowboat', 'Jetty', 'MooringPost', 'NetPile', 'Barrel', 'Barrels', 'RopeCoil', 'LobsterTrap',
         'Anchor', 'Oars', 'FishBaskets', 'Crane', 'CrateTarp', 'PlankPile']
DECOR = ['WallNet', 'WallRing', 'WallShelf', 'WallRope', 'WallSail', 'WallBoard', 'WallOars', 'WallFish', 'WallGap']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Harbor', 'asset_name': 'SM_HB_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
