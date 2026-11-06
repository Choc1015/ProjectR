import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
P = '/Game/Props/ForestTemple/SM_FT_'
SRC = 'C:/UnrealProject/ProjectR/SourceArt/Export/ForestTemple/SM_FT_'
NEW = ['FloorTile', 'FloorTileB', 'MossPatch', 'MossPatchSmall', 'TempleWall', 'TempleWallDoor', 'TempleCorner',
       'Ceiling', 'CeilingBroken', 'CeilingBrokenB', 'HangingVines']

def xf(x, y, z=0, yaw=0, s=1.0):
    return {'location': {'x': x, 'y': y, 'z': z}, 'rotation': {'pitch': 0, 'yaw': yaw, 'roll': 0}, 'scale': {'x': s, 'y': s, 'z': s}}

def add(m, name, x, y, z=0, yaw=0, s=1.0):
    call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': P + m, 'name': name, 'xform': xf(x, y, z, yaw, s)})

def remove_named(prefix):
    acts = call('scene.SceneTools.find_actors', {'name': prefix, 'tag': '', 'collision_channels': []})
    for a in acts:
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    return len(acts)

def run():
    out = {'rm': {}}
    # old floor, edge arches and edge ruin walls go away (the temple walls replace them)
    for p in ('FT_Floor_', 'FT_Arch_', 'FT_WallRuinA_', 'FT_WallRuinB_'):
        out['rm'][p] = remove_named(p)
    # re-import changed/new meshes (delete first: same-name reimport fails)
    for n in NEW:
        try:
            call('asset.AssetTools.delete', {'path': P + n})
        except Exception:
            pass
        call('static_mesh.StaticMeshTools.import_file', {'folder_path': '/Game/Props/ForestTemple', 'asset_name': 'SM_FT_' + n,
             'source_file': SRC + n + '.fbx', 'import_materials': True})
    # floor: mix two tile layouts with rotation so no pattern repeats
    i = 0
    for gx in range(12):
        for gy in range(12):
            m = 'FloorTileB' if (gx * 5 + gy * 3) % 3 == 0 else 'FloorTile'
            add(m, 'FT_Floor_%03d' % i, -1100 + gx * 200, -1100 + gy * 200, 0, ((gx * 7 + gy * 11) % 4) * 90)
            i += 1
    # big soft moss patches, few and irregular
    for k, (m, x, y, yaw) in enumerate([('MossPatch', -420, -300, 20), ('MossPatch', 520, 380, 145), ('MossPatchSmall', 80, -620, 70),
                                         ('MossPatchSmall', -700, 420, 200), ('MossPatch', 760, -480, 290), ('MossPatchSmall', -150, 700, 330)]):
        add(m, 'FT_Moss_%02d' % k, x, y, 0.5, yaw)
    # walls: interior face on the room edge, 6 modules of 4 m per side, doors on -X / +X
    k = 0
    for c in (-1000, -600, -200, 200, 600, 1000):
        add('TempleWall', 'FT_TWall_%02d' % k, c, -1200, 0, 0); k += 1
        add('TempleWall', 'FT_TWall_%02d' % k, c, 1200, 0, 180); k += 1
    for c in (-1000, -600, 600, 1000):
        add('TempleWall', 'FT_TWall_%02d' % k, -1200, c, 0, 270); k += 1
        add('TempleWall', 'FT_TWall_%02d' % k, 1200, c, 0, 90); k += 1
    add('TempleWallDoor', 'FT_TWallDoor_00', -1200, 0, 0, 270)
    add('TempleWallDoor', 'FT_TWallDoor_01', 1200, 0, 0, 90)
    for j, (x, y) in enumerate([(-1250, -1250), (1250, -1250), (-1250, 1250), (1250, 1250)]):
        add('TempleCorner', 'FT_TCorner_%02d' % j, x, y)
    # ceiling 6x6, broken pieces over the trees and one near the middle for sunlight
    broken = {(-1000, 1000): 'CeilingBroken', (1000, -1000): 'CeilingBroken', (1000, 1000): 'CeilingBrokenB',
              (200, -1000): 'CeilingBrokenB', (-200, 200): 'CeilingBroken', (-600, -600): 'CeilingBrokenB'}
    j = 0
    for cx in (-1000, -600, -200, 200, 600, 1000):
        for cy in (-1000, -600, -200, 200, 600, 1000):
            m = broken.get((cx, cy), 'Ceiling')
            add(m, 'FT_Ceiling_%02d' % j, cx, cy, 800, ((cx + cy) // 400 % 4) * 90); j += 1
    for v, (x, y, yaw) in enumerate([(-1000, 800, 0), (900, -850, 90), (-300, 250, 200), (850, 950, 300), (-550, -700, 45)]):
        add('HangingVines', 'FT_Vines_%02d' % v, x, y, 800, yaw)
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    out['floor'] = i
    return out
