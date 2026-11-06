import json
N = 'NiagaraToolsets.NiagaraToolset_System.'
def ref(p): return {'refPath': p}
NAME = 'NS_FireballExplosion'
SYS = ref('/Game/Weapons/Staff/' + NAME + '.' + NAME)
def nt(f, a): return execute_tool(N + f, json.dumps(a))
# 화염구 폭발: 엔진 OmnidirectionalBurst 이미터 하나로 만든다(03에서 색·크기 조정).
def run():
    out = {}
    nt('CreateNiagaraSystem', {'AssetName': NAME, 'AssetPath': '/Game/Weapons/Staff',
        'TemplateSystem': ref('/Niagara/DefaultAssets/Templates/Systems/MinimalLightweight.MinimalLightweight')})
    nt('AddEmitter', {'System': SYS, 'TemplateEmitter': ref('/Niagara/DefaultAssets/Templates/Emitters/OmnidirectionalBurst.OmnidirectionalBurst'), 'EmitterName': 'Burst'})
    try:
        nt('RemoveEmitter', {'EmitterToRemove': {'system': SYS, 'emitterName': 'Minimal'}})
    except Exception as e:
        out['rm'] = str(e)[:200]
    vals = nt('GetEmitterInputValues', {'EmitterRef': {'system': SYS, 'emitterName': 'Burst'}})
    out['vals'] = json.dumps(vals)[:5000]
    return out
