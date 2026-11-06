import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Forge/SM_FG_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Forge/SM_FG_'
STRUCT = ['FloorTile', 'FloorTileB', 'SootPatch', 'SootPatchSmall', 'Wall', 'WallB', 'Pilaster', 'Corner', 'Ceiling', 'CeilingVent',
          'Beam', 'ExitDoor', 'EntranceDoor']
PROPS = ['Furnace', 'Channel', 'AnvilStump', 'AnvilBlock', 'Ingots', 'Trough', 'WeaponRack', 'CoalPile', 'OreCart', 'Bellows',
         'Grindstone', 'Brazier', 'Barrel', 'CrateStack', 'Workbench', 'Pillar']
DECOR = ['WallToolRack', 'WallShield', 'WallChains', 'WallRelief', 'WallBrazier', 'WallBanner', 'WallShelf', 'WallVent', 'WallAxes']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Forge', 'asset_name': 'SM_FG_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
