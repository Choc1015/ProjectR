import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Library/SM_LB_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Library/SM_LB_'
STRUCT = ['FloorTile', 'FloorTileB', 'Rug', 'Wall', 'WallWindow', 'Pillar', 'Corner', 'Ceiling', 'Beam', 'ExitDoor', 'EntranceDoor']
PROPS = ['Bookshelf', 'BookshelfLow', 'Telescope', 'Desk', 'Globe', 'ScrollPile', 'BookStack', 'CandleStand', 'Candles', 'ReadingChair',
         'Chest', 'Lectern']
DECOR = ['WallStarMap', 'WallStarChart', 'WallSconce', 'WallShelf', 'WallClock', 'WallBanner']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Library', 'asset_name': 'SM_LB_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
