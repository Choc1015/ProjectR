import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/SnowShrine/SM_SN_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/SnowShrine/SM_SN_'
STRUCT = ['FloorTile', 'FloorTileB', 'SnowPatch', 'SnowPatchSmall', 'Wall', 'WallB', 'Post', 'Corner', 'Rafter',
          'RoofPanel', 'RoofPanelBroken', 'ExitDoor', 'EntranceGate']
PROPS = ['PineTree', 'PineSmall', 'Shrine', 'FlagPost', 'Sled', 'SledTilted', 'Campfire', 'Firewood', 'IceRock', 'StoneWall',
         'SnowDrift', 'Signpost', 'Barrel', 'CrateStack', 'LanternPost', 'Skis']
DECOR = ['WallIcicles', 'WallFlags', 'WallSnowDrift', 'WallSnowshoes', 'WallPelt', 'WallSpiritShelf', 'WallShield', 'WallFrostCrack', 'WallWindow']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/SnowShrine', 'asset_name': 'SM_SN_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
