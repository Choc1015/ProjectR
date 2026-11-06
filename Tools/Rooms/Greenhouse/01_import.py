import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
P = '/Game/Props/Greenhouse/SM_GH_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/Greenhouse/SM_GH_'
STRUCT = ['FloorTile', 'FloorTileB', 'GrassPatch', 'GrassPatchSmall', 'Wall', 'WallB', 'Post', 'Corner', 'Rib',
          'RoofGlass', 'RoofGlassBroken', 'ExitDoor', 'EntranceDoor']
PROPS = ['FlowerBed', 'Planter', 'Fountain', 'PlanterLow', 'PotTree', 'Topiary', 'Pots', 'PottingBench', 'Wheelbarrow', 'CanRake',
         'Bench', 'BirdStatue', 'GlassShards', 'Wildflowers', 'Sacks', 'RoseArch']
DECOR = ['WallIvy', 'WallIvyLow', 'WallBasket', 'WallTools', 'WallPlanterBox', 'WallSunshade', 'WallShelf', 'WallRoses', 'WallNest']
NAMES = STRUCT + PROPS + DECOR   # re-import only some: shorten this list and remove the actors that use them first

def run():
    out = {}
    for n in NAMES:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        try:
            call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/Greenhouse', 'asset_name': 'SM_GH_' + n,
                 'source_file': SRC + n + '.fbx', 'import_materials': True})
            out[n] = 'ok'
        except Exception as e:
            out[n] = str(e)[:120]
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return out
