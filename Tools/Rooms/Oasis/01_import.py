import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Oasis/SM_OA_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Oasis/SM_OA_'
STRUCT = ['FloorTile', 'FloorTileB', 'SandPatch', 'SandPatchSmall', 'Wall', 'WallB', 'Corner', 'Beam',
          'Canopy_Blue', 'Canopy_Yellow', 'Canopy_Red', 'CanopyTorn_Blue', 'CanopyTorn_Red', 'ExitDoor', 'EntranceArch']
PROPS = ['Column', 'ColumnStump', 'ColumnFallen', 'Block', 'PalmTree', 'Pool', 'PotGroup', 'Amphora', 'Baskets', 'Rugs',
         'Stall', 'CrateCloth', 'Shrub', 'SandDrift', 'StatueHead', 'Rubble']
DECOR = ['WallBanner', 'WallRelief', 'WallNiche', 'WallPalmMat', 'WallCrack', 'WallShelf', 'WallSandDrift', 'WallRug', 'WallGrille']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Oasis', 'asset_name': 'SM_OA_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
