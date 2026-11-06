import json
E = 'editor_toolset.toolsets.'
def call(n, a): return execute_tool(E + n, json.dumps(a))['returnValue']
def ref(p): return {'refPath': p}
LV = '/Game/Maps/Rooms/L_Room_ForestTemple.L_Room_ForestTemple:PersistentLevel.'
def setp(path, vals):
    call('object.ObjectTools.set_properties', {'instance': ref(LV + path), 'values': json.dumps(vals)})
def run():
    # lift the shadows: brighter sky fill with a warm floor bounce, slightly brighter exposure
    setp('SkyLight_0.SkyLightComponent0', {'intensity': 1.2, 'bLowerHemisphereIsBlack': False,
         'lowerHemisphereColor': {'r': 0.35, 'g': 0.3, 'b': 0.24, 'a': 1}})
    setp('PostProcessVolume_0', {'settings': {'bOverride_AutoExposureMinBrightness': True, 'autoExposureMinBrightness': 3.6,
         'bOverride_AutoExposureMaxBrightness': True, 'autoExposureMaxBrightness': 3.6}})
    call('asset.AssetTools.save_assets', {'asset_paths': []})
    return {'sky': call('object.ObjectTools.get_properties', {'instance': ref(LV + 'SkyLight_0.SkyLightComponent0'), 'properties': ['intensity', 'bLowerHemisphereIsBlack']})}
