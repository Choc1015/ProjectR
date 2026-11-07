<!-- CLAUDE.md에서 옮겨 옴(2026-11-07). 블렌더 모델링·익스포트·임포트·애니메이션 작업 전에 읽는다. -->
## 에셋 규칙 (블렌더 → 언리얼)
<!-- 첫 에셋을 언리얼로 가져와 방향·크기를 확인한 뒤 확정한 값을 적는다. -->
- 블렌더 원본 경로: `SourceArt/` (`.blend`, Git LFS)
- 익스포트 경로: `SourceArt/Export/` (`.fbx`)
- 언리얼 임포트 경로: 캐릭터 `/Game/Characters/<이름>/`, 무기 `/Game/Weapons/<이름>/`, 소품 `/Game/Props/<이름>/`, 블루프린트 `/Game/Blueprints/`
- 스케일/단위: 블렌더 미터 단위, 1 unit = 1 m (언리얼 100 cm). 확정
- 익스포트 설정(확정): `apply_scale_options='FBX_SCALE_NONE'`, `mesh_smooth_type='FACE'`, 나머지 기본값.
  `FBX_SCALE_ALL`은 언리얼에서 100배 작게(1 m → 1 cm) 들어온다.
- 축·원점(확정): 블렌더 정면 -Y, 원점 바닥 중앙. 스태틱 메시는 언리얼에서 정면이 +Y로 들어온다(허수아비는 yaw 90으로 배치).
- 미사모 캐릭터(현재 SK_Player): 업로드 FBX가 `FBX_SCALE_ALL`로 내보낸 것이라 `AnimationAssetTools`로 `uniform_scale=100` 임포트.
  손 본에 x100 스케일이 있으므로 본에 붙이는 컴포넌트는 `bAbsoluteScale=True`. 메시 yaw 180이 정면(+X).
- 임포트·몽타주·애님BP 생성은 프로젝트 툴셋 `projectr_toolset.toolsets.animation_asset.AnimationAssetTools`를 쓴다.
  수정 후 다시 불러오기: 엔진 파이썬으로 `toolset_registry/tests/reload_remote.py projectr_toolset` (새 테스트 추가는 에디터 재시작 필요).
- `ActorTools.set_actor_transform`은 빠진 필드를 0으로 덮어쓴다. 위치·회전·스케일을 모두 넘긴다.
- 블렌더에서 미사모 리그로 애니메이션을 만들 때: 불러온 아마추어에 X 90도 회전이 걸려 있어, 내보내기 전에
  회전 적용(`transform_apply(rotation=True)`)을 해야 언리얼에서 눕지 않는다. 임포트는 `uniform_scale=100`.
  (직접 만든 베기 모션은 품질 문제로 폐기하고 미사모 Attack 1~3을 쓴다. 기록은 커밋 b96adc6.)
- 블렌더 MCP: `bpy.ops.wm.read_factory_settings`·`read_homefile`·파일 새로 열기는 애드온 서버를 내려 연결이 끊긴다. 씬을 비울 땐 오브젝트·액션·메시를 직접 지운다. 호출은 하나씩 순서대로.
- 알려진 문제: 애니메이션을 `replace_existing=True`로 재임포트하면 배율이 두 번 곱해진다(x10000). 지우고 새로 임포트한다.
