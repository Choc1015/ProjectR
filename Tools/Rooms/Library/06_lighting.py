import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_Library.L_Room_Library:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})

# tunables - EVENING library: candles (08_lights, 09_glow) carry the light, a little dusk sky fill so the shelves read.
# sky fill only keeps the corners from going pitch black. (day version was sun 40 lux / sky 1.2 / EV 3.6)
SUN = {'pitch': -62, 'yaw': 30, 'lux': 0.6, 'scatter': 4.0, 'color': {'r': 0.67, 'g': 0.75, 'b': 1.0, 'a': 1.0}}
FOG = {'density': 0.03, 'scatter_dist': 0.6}
SKY = {'intensity': 0.12, 'lower': {'r': 0.06, 'g': 0.05, 'b': 0.05, 'a': 1}}
EV = 0.4

def ppv():
    # DevMap has no post process volume: make one (unbound) the first time and use its real object path
    found = call('scene.SceneTools.find_actors', {'name': 'PostProcessVolume', 'tag': '', 'collision_channels': []})
    if not found:
        found = [call('scene.SceneTools.add_to_scene_from_class', {'actor_type': {'refPath': '/Script/Engine.PostProcessVolume'},
                 'name': 'PostProcessVolume', 'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})]
    return found[0]['refPath'].split('PersistentLevel.')[-1]

def run():
    call('scene.SceneTools.load_level', {'level_path': LV.split('.')[0]})   # light colours are linear 0-1 (0-255 clamps to white)
    pp = ppv()
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'DirectionalLight_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 1500}, 'rotation': {'pitch': SUN['pitch'], 'yaw': SUN['yaw'], 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('DirectionalLight_0.LightComponent0', {'intensity': SUN['lux'], 'lightColor': SUN['color'],
         'volumetricScatteringIntensity': SUN['scatter'], 'bCastVolumetricShadow': True, 'bEnableLightShaftBloom': True})
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'ExponentialHeightFog_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('ExponentialHeightFog_0.HeightFogComponent0', {'fogDensity': FOG['density'], 'fogHeightFalloff': 0.2, 'bEnableVolumetricFog': True,
         'volumetricFogScatteringDistribution': FOG['scatter_dist'], 'volumetricFogExtinctionScale': 1.0, 'volumetricFogDistance': 3000})
    setp('SkyLight_0.SkyLightComponent0', {'intensity': SKY['intensity'], 'volumetricScatteringIntensity': 0.2,
         'bLowerHemisphereIsBlack': False, 'lowerHemisphereColor': SKY['lower']})
    setp(pp, {'bUnbound': True, 'settings': {
        'bOverride_AutoExposureMinBrightness': True, 'autoExposureMinBrightness': EV,
        'bOverride_AutoExposureMaxBrightness': True, 'autoExposureMaxBrightness': EV,
        'bOverride_BloomIntensity': True, 'bloomIntensity': 0.9,
        'bOverride_VignetteIntensity': True, 'vignetteIntensity': 0.5}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'pp': pp, 'sky': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'SkyLight_0.SkyLightComponent0'), 'properties': ['intensity']}),
            'fog': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'ExponentialHeightFog_0.HeightFogComponent0'), 'properties': ['bEnableVolumetricFog', 'fogDensity']})}
