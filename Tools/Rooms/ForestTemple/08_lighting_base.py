import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_ForestTemple.L_Room_ForestTemple:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})

# tunables
SUN = {'pitch': -62, 'yaw': 30, 'lux': 12.0, 'scatter': 8.0}
EV = 1.0

def run():
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'DirectionalLight_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 1500}, 'rotation': {'pitch': SUN['pitch'], 'yaw': SUN['yaw'], 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('DirectionalLight_0.LightComponent0', {'intensity': SUN['lux'], 'lightColor': {'r': 255, 'g': 228, 'b': 186, 'a': 255},
         'volumetricScatteringIntensity': SUN['scatter'], 'bCastVolumetricShadow': True})
    call('actor.ActorTools.set_actor_transform', {'actor': ref(LV + 'ExponentialHeightFog_0'),
         'xform': {'location': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'pitch': 0, 'yaw': 0, 'roll': 0}, 'scale': {'x': 1, 'y': 1, 'z': 1}}})
    setp('ExponentialHeightFog_0.HeightFogComponent0', {'fogDensity': 0.05, 'fogHeightFalloff': 0.3, 'bEnableVolumetricFog': True,
         'volumetricFogScatteringDistribution': 0.75, 'volumetricFogExtinctionScale': 1.5, 'volumetricFogDistance': 3500
         })
    setp('SkyLight_0.SkyLightComponent0', {'intensity': 0.5})
    setp('PostProcessVolume_0', {'bUnbound': True, 'settings': {
        'bOverride_AutoExposureMinBrightness': True, 'autoExposureMinBrightness': EV,
        'bOverride_AutoExposureMaxBrightness': True, 'autoExposureMaxBrightness': EV,
        'bOverride_BloomIntensity': True, 'bloomIntensity': 0.9,
        'bOverride_VignetteIntensity': True, 'vignetteIntensity': 0.5}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    pp = json.loads(call('object.ObjectTools.get_properties', {'instance': ref(LV + 'PostProcessVolume_0'), 'properties': ['settings', 'bUnbound']}))
    st = pp['settings']
    return {'unbound': pp['bUnbound'], 'ev': [st.get(k) for k in ('autoExposureMinBrightness', 'autoExposureMaxBrightness', 'bOverride_AutoExposureMinBrightness')],
            'fog': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'ExponentialHeightFog_0.HeightFogComponent0'), 'properties': ['bEnableVolumetricFog', 'fogDensity']})}
