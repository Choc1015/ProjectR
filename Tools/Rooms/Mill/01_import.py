import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mill/SM_ML_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Mill/SM_ML_'
STRUCT = ['FloorTile', 'FloorTileB', 'Stream', 'StreamEnd', 'Wall', 'WallWindow', 'Post', 'Corner', 'Rafter', 'Roof', 'RoofBroken',
          'ExitDoor', 'EntranceDoor']
PROPS = ['WaterWheel', 'Millstones', 'MillstoneLeaning', 'Sacks', 'SackPile', 'GrainBin', 'Cart', 'Barrel', 'Scale', 'Workbench',
         'Crates', 'Rope', 'Bench']
DECOR = ['WallTools', 'WallWheat', 'WallShelf', 'WallSign', 'WallRope', 'WallLantern', 'WallCloth']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Mill', 'asset_name': 'SM_ML_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
