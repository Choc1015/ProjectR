import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Vineyard/SM_VY_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Vineyard/SM_VY_'
STRUCT = ['FloorTile', 'FloorTileB', 'LeafPatch', 'LeafPatchSmall', 'Wall', 'WallVine', 'Pier', 'Corner', 'Beam',
          'VineCanopy', 'VineCanopySparse', 'ExitDoor', 'EntranceDoor']
PROPS = ['Barrel', 'BarrelStack', 'BarrelUp', 'GrapeBasket', 'GrapeBaskets', 'Crate', 'CrateStack', 'Trellis', 'Press', 'Table',
         'Bench', 'WineRack', 'Planter', 'LowWall']
DECOR = ['WallVines', 'WallBarrelEnd', 'WallShelf', 'WallBanner', 'WallTools', 'WallLamp']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Vineyard', 'asset_name': 'SM_VY_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
