# ProjectR

언리얼 MCP(에디터)와 블렌더 MCP(에셋)로 만드는 언리얼 엔진 프로젝트. 사용자에게 보이는 글은 마지막 안내 상자까지 전부 한국어로 쓴다.

## 작업 규칙 (사용자가 정함)

1. **결정은 사용자가 한다.** 지금 요청한 기능만 만든다. 규칙·밸런스는 나중에 붙이므로 처음부터 큰 시스템을 깔지 않는다.
   - 물어볼 것: 게임플레이, 규칙, 수치, 시각적 방향, 새 시스템 추가
   - 직접 정하고 알릴 것: 폴더, 에셋 이름(UE 접두사 `BP_`/`M_`/`SM_` 등), 변수명 같은 기술 세부사항
2. **에셋은 블렌더 MCP로, 임시 도형 금지.** 처음부터 블렌더로 실제 모델을 만든다. 모델·에셋·애니메이션이 필요하면 사용자에게 요청하거나 추천한다(무료 우선: Fab, Mixamo, Poly Haven).
3. **velog 개발일지.** `Docs/Devlog/NN_제목.md`(템플릿: `Docs/Devlog/_TEMPLATE.md`), 스크린샷은 `Docs/Devlog/images/`.
   구성: 목표 → 구현 → 문제와 해결 → 다음 할 일. 말투는 반말("~했다"). 기능 하나가 동작할 때마다 여기서 끊을지 제안한다.
4. **혼합 구현.** 핵심 로직은 C++(라이브 코딩으로 컴파일), 조정과 연결은 블루프린트.
5. **작게 키운다.** 거시적인 기획 질문은 하지 않는다. 다음 작은 단계만 묻는다.

## 백업

- GitHub: https://github.com/Choc1015/ProjectR (브랜치 `main`, uasset/umap/blend/fbx/텍스처는 Git LFS)
- 개발일지를 끊는 시점마다 묻지 않고 커밋·푸쉬한다. 커밋 서명 줄은 현재 세션 지침을 따른다.

## MCP 작업 규칙 (토큰 절약)

### 역할 분담
- **메인 세션**: 설계, C++/블루프린트 구조 결정, C++ 코드 작성, 버그 원인 분석, 워커 결과 검토
- **unreal-worker**(Sonnet): 언리얼 에디터 조작. 배치, 수정, 조회, 임포트, 정리
- **blender-worker**(Sonnet): 블렌더 모델링, 머티리얼, 익스포트
- 블렌더 → 언리얼: blender-worker가 익스포트하고 unreal-worker가 임포트·배치한다. 메인은 두 요약만 받는다.

### 직접 호출 vs 위임
- **위임**: MCP 호출이 3번 이상이거나, 결과가 클 것 같은 작업(씬 조회, 에셋 목록, 모델링)
- **직접 호출**: 값 1~2개 확인처럼 작은 호출. 서브에이전트는 매번 처음부터 시작해서, 작은 일에는 오히려 토큰이 더 든다.
- 워커가 같은 작업에서 2번 실패하면 그 작업만 메인에서 직접 처리한다.

### 위임하는 법
- "무엇을, 어디에, 어떤 값으로"를 분명하게 쓴다. 에셋 경로와 이름까지 정해서 넘긴다.
- 서로 독립적인 조작은 한 번의 위임에 묶는다.
- 결과는 요약만 받는다.

### 컨텍스트 절약
- 레벨·액터 전체 덤프 금지. 필요한 범위만 걸러서 조회한다.
- 스크린샷은 시각 확인이 꼭 필요할 때만, 작은 크기로.
- 아래 "프로젝트 구조"와 `.claude/unreal-tools.md`(확인된 도구 목록)에 있는 내용은 MCP로 다시 조회하지 않는다.
- 기능 하나가 끝나면 `/compact` 또는 새 세션을 제안한다.

## 프로젝트 구조
<!-- 자주 조회하는 정보를 적어 두면 매번 MCP로 확인할 필요가 없다. 알게 될 때마다 채운다. -->
- 엔진 버전: UE 5.8 (`C:\Program Files\Epic Games\UE_5.8`), C++ 모듈 `ProjectR`
- 주요 레벨: `/Game/DevMap`, `/Game/Maps/DevMap` (GameDefaultMap은 아직 템플릿 기본값 `/Engine/Maps/Templates/OpenWorld`)
- Unreal MCP: `http://127.0.0.1:8010/mcp` (Config/DefaultEditorPerProjectUserSettings.ini에서 자동 시작)
- 주요 C++ 클래스 / 블루프린트 위치:
- 폴더 규칙:
- 네이밍 규칙: UE 표준 접두사(`BP_`, `WBP_`, `M_`, `MI_`, `SM_`, `SK_`, `T_`, `ABP_`, `NS_`)

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
- 알려진 문제: 애니메이션을 `replace_existing=True`로 재임포트하면 배율이 두 번 곱해진다(x10000). 지우고 새로 임포트한다.
