import json
N = 'NiagaraToolsets.NiagaraToolset_System.'
def ref(p): return {'refPath': p}
SYS = ref('/Game/Props/ForestTemple/NS_FT_LightDust.NS_FT_LightDust')
def nt(f, a): return execute_tool(N + f, json.dumps(a))
def run():
    out = {}
    out['add'] = str(nt('AddEmitter', {'System': SYS, 'TemplateEmitter': ref('/Niagara/DefaultAssets/Templates/Emitters/HangingParticulates.HangingParticulates'), 'EmitterName': 'Dust'}))[:200]
    try:
        nt('RemoveEmitter', {'EmitterToRemove': {'system': SYS, 'emitterName': 'Minimal'}})
        out['rm'] = 'ok'
    except Exception as e:
        out['rm'] = str(e)[:200]
    vals = nt('GetEmitterInputValues', {'EmitterRef': {'system': SYS, 'emitterName': 'Dust'}})
    out['vals'] = json.dumps(vals)[:6000]
    return out
