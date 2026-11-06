import json, math
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
# light dust (forest temple's NS_FT_LightDust) under each missing / torn canopy, shifted along the sun beam to mid height
CENTERS = (-1000, -600, -200, 200, 600, 1000)
MISSING = [(200, -200), (-600, 600), (600, 600), (-1000, -600)]        # same as 03_shell
TORN = [(-200, -600), (1000, 200), (-600, 1000), (200, 1000)]          # same as 03_shell
TORN_HOLE = (40, 50)   # blender (0.4, -0.5) m -> UE cm, y flipped
SUN_PITCH, SUN_YAW = -55, 40                                            # same as 06_lighting
def run():
    for a in call('scene.SceneTools.find_actors', {'name': 'VY_LightDust_', 'tag': '', 'collision_channels': []}):
        call('scene.SceneTools.remove_from_scene', {'actor': a})
    run_h = (720 - 400) / math.tan(math.radians(-SUN_PITCH))
    dx, dy = run_h * math.cos(math.radians(SUN_YAW)), run_h * math.sin(math.radians(SUN_YAW))
    spots = list(MISSING)
    for cx, cy in TORN:
        gx, gy = CENTERS.index(cx), CENTERS.index(cy)
        r = math.radians(((gx * 5 + gy * 3) % 4) * 90)    # canopy yaw from 03_shell
        ox, oy = TORN_HOLE
        spots.append((cx + ox * math.cos(r) - oy * math.sin(r), cy + ox * math.sin(r) + oy * math.cos(r)))
    for n, (hx, hy) in enumerate(spots):
        call('scene.SceneTools.add_to_scene_from_asset', {'asset_path': '/Game/Props/ForestTemple/NS_FT_LightDust', 'name': 'VY_LightDust_%02d' % n,
             'xform': {'location': {'x': hx + dx, 'y': hy + dy, 'z': 400}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'placed': len(spots)}
