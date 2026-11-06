import json
def ref(p): return {'refPath': p}
NS = '/Game/Props/ForestTemple/NS_FT_LightDust'
def run():
    out = {}
    for prefix in ('NiagaraToolsets.NiagaraToolset_System.', 'NiagaraToolset_System.', 'NiagaraToolsets.System.'):
        try:
            r = execute_tool(prefix + 'CreateNiagaraSystem', json.dumps({'AssetName': 'NS_FT_LightDust', 'AssetPath': '/Game/Props/ForestTemple',
                'TemplateSystem': ref('/Niagara/DefaultAssets/Templates/Systems/MinimalLightweight.MinimalLightweight')}))
            out['prefix'] = prefix; out['create'] = str(r)[:300]
            break
        except Exception as e:
            out[prefix] = str(e)[:200]
    if 'prefix' in out:
        out['summary'] = str(execute_tool(out['prefix'] + 'GetSystemSummary', json.dumps({'System': ref(NS + '.NS_FT_LightDust')})))[:1500]
    return out
