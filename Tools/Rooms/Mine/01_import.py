import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Mine/SM_MN_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Mine/SM_MN_'
# structure pieces (blender batch 1) + props / wall decor (batch 2). Re-run with only the changed names to re-import.
STRUCT = ['FloorTile', 'FloorTileB', 'DirtPatch', 'DirtPatchSmall', 'RockWall', 'RockWallB', 'RockCorner',
          'Ceiling', 'CeilingCrack', 'CeilingCrackB', 'CeilingBeam', 'SupportFrame', 'TunnelEntrance', 'ExitDoor']
PROPS = ['RailStraight', 'RailCurve', 'OreCart', 'CartOverturned', 'OreCrate', 'CrateStack', 'Barrel', 'PickShovel',
         'LadderBroken', 'Rubble', 'CrystalLarge', 'CrystalSmall', 'Pulley', 'Workbench']
DECOR = ['WallCrystal', 'WallCrystalVein', 'WallBoards', 'WallRopeHook', 'WallShelf', 'WallTarp', 'WallSign', 'WallChain', 'WallNiche']
NAMES = STRUCT + PROPS + DECOR

def run():
    out = {}
    for n in NAMES:
        # same-name reimport fails: delete first (actors using it must be removed beforehand)
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Mine', 'asset_name': 'SM_MN_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
