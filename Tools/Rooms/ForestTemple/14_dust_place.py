import json, math
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
BROKEN = {(-1000, 1000): 'B', (1000, -1000): 'B', (1000, 1000): 'BB', (200, -1000): 'BB', (-200, 200): 'B', (-600, -600): 'BB'}
HOLE = {'B': (0, -110), 'BB': (120, -120)}
SUN_PITCH, SUN_YAW = -62, 30
def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'FT_LightDust_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    run_h = (820 - 400) / math.tan(math.radians(-SUN_PITCH))  # horizontal drift of the beam down to mid height
    dx, dy = run_h * math.cos(math.radians(SUN_YAW)), run_h * math.sin(math.radians(SUN_YAW))
    n = 0
    for (cx, cy), kind in BROKEN.items():
        yaw = ((cx + cy) // 400 % 4) * 90
        ox, oy = HOLE[kind]
        r = math.radians(yaw)
        hx = cx + ox * math.cos(r) - oy * math.sin(r)
        hy = cy + ox * math.sin(r) + oy * math.cos(r)
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': '/Game/Props/ForestTemple/NS_FT_LightDust', 'name': 'FT_LightDust_%02d' % n,
             'xform': {'location': {'x': hx + dx, 'y': hy + dy, 'z': 400}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
        n += 1
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'placed': n}
