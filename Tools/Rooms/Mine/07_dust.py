import json, math
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
# light dust (reused from the forest temple) under each ceiling crack, shifted along the sun beam to mid height
CRACKS = {(-200, 200): 'A', (600, -600): 'B', (-600, -1000): 'B'}   # same as 03_shell
HOLE = {'A': (0, -110), 'B': (120, -120)}                            # hole centre in blender cm; y flips on import
SUN_PITCH, SUN_YAW = -62, 30
ENABLED = False  # night mine: no sunbeams, so no dust. True puts it back under the cracks.
def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'MN_LightDust_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    if not ENABLED:
        call('asset.AssetTools.save_assets', {'asset_paths': []})
        return {'placed': 0}
    run_h = (820 - 400) / math.tan(math.radians(-SUN_PITCH))
    dx, dy = run_h * math.cos(math.radians(SUN_YAW)), run_h * math.sin(math.radians(SUN_YAW))
    n = 0
    for (cx, cy), kind in CRACKS.items():
        yaw = ((cx + cy) // 400 % 4) * 90
        ox, oy = HOLE[kind][0], -HOLE[kind][1]
        r = math.radians(yaw)
        hx = cx + ox * math.cos(r) - oy * math.sin(r)
        hy = cy + ox * math.sin(r) + oy * math.cos(r)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': '/Game/Props/ForestTemple/NS_FT_LightDust', 'name': 'MN_LightDust_%02d' % n,
             'xform': {'location': {'x': hx + dx, 'y': hy + dy, 'z': 400}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        n += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'placed': n}
