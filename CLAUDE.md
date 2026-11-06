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

## 맵 규칙 (사용자가 정함)

- 맵은 **방 단위**로 만들어 계속 찍어낸다. 방은 실내가 아니라 **세상 한 조각을 방 크기에 담은 것**(숲, 폐허 등 바깥 풍경도 방 하나).
- 방마다 입구·출구가 있고, 가운데는 몬스터와 싸울 공간, 둘레는 소품으로 알뜰하게 채운다.
- 순서: 제미나이로 테마·소품 레퍼런스를 뽑아 보여 준다 → 사용자가 고른다 → 블렌더로 만든다 → 언리얼에 배치 → 사용자 검수.
- 레퍼런스는 `Docs/ArtRef/Rooms/`. 첫 방 테마: 숲속 신전 폐허.
- 방 레벨은 `/Game/Maps/Rooms/L_Room_<테마>`(DevMap을 복제해 조명 유지). 방 크기 24m x 24m, 중심 원점, 바닥은 2m 타일 12x12(두 모양을 섞고 돌려 반복 무늬 방지, 이끼는 타일에 넣지 않고 큰 덩어리로 따로).
- 방은 사방 벽과 천장으로 막는다(숲속 신전: 높이 8m 석조 벽 4m 모듈(문 없이 막힘, 이끼는 `TempleWallMoss` 몇 개만 불규칙하게·일부 좌우 반전, 벽 장식 `SM_FT_Wall*` 8종을 위치·높이·크기·좌우 반전을 섞어 16개, 장식 원점은 벽면 Y=0이고 방 쪽으로 튀어나옴. 랜턴 발광·조명은 없음)
- 라이팅(숲속 신전): 해 pitch -62 yaw 30·40 lux, 스카이라이트 0.3, 볼류메트릭 안개, PostProcessVolume_0 노출 고정 EV 4.5. 천장 구멍마다 빛기둥 메시 `SM_FT_LightShaft`(가산 발광 `M_FT_LightShaft`, 버텍스 컬러로 위→아래 페이드, 해 방향으로 기울임 pitch = 90+해pitch), 천장 4m 판 6x6을 z=8m에 두고 일부는 무너진 판으로 하늘·빛이 들게).
- 소품: 블렌더 원본 `SourceArt/<테마>_Props.blend`, FBX `SourceArt/Export/<테마>/SM_<약자>_*.fbx`, 언리얼 `/Game/Props/<테마>/`(숲속 신전은 약자 FT).
- MCP 배치: `SceneTools.add_to_scene_from_asset`의 `xform`은 `{location, rotation{pitch,yaw,roll}, scale}` 형식이다(`translation`/쿼터니언을 넘기면 조용히 원점에 놓인다).

## 아트 통일 규칙 (모든 모델·UI·이펙트·아이콘에 적용)

새 그래픽은 지금 만들어진 것과 같은 게임처럼 보여야 한다. 기준은 `Docs/ArtRef/`의 그림과 `Docs/ArtRef/GeminiPrompts.md`.
- **3D(모델·소품·무기·이펙트):** 스타일라이즈드 로우폴리, 면 셰이딩, 단색 + 약한 그라데이션, 세밀한 텍스처 없음.
  색은 가죽 갈색 · 철 회색 · 바랜 천 파랑 · 짚 노랑의 차분하고 따뜻한 톤. 밝고 아늑한 중세 판타지(다크·네온·사실적 톤 금지).
- **2D(UI·아이콘):** 빈티지 양피지 바탕 위 세피아 잉크 선, 강조는 바랜 금박, 포인트는 진한 붉은 밀랍. 깔끔하고 단정하게.
  UI 조각은 흰 단색(#FFFFFF) 배경으로 따로 뽑아 흰색을 지운다(바탕과 합쳐 뽑지 않는다).
- **제미나이 프롬프트:** 3D는 "공통 스타일 문구", 2D는 "UI 공통 스타일 문구"를 반드시 끝에 붙인다. 새 프롬프트는 `GeminiPrompts.md`에 추가한다.
- **블렌더 모델링:** 레퍼런스 그림을 먼저 받고 만든다. 기존 모델(`SK_Player`, 허수아비, 검)과 폴리 밀도·색감·비율을 맞춘다.
- 위 기준에서 벗어나는 그래픽이 필요하면 만들기 전에 사용자에게 묻는다. 스타일이 바뀌면 이 절과 프롬프트 문서를 같이 고친다.

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
- 아래 "프로젝트 구조"와 `.claude/unreal-tools.md`(확인된 도구 목록)에 있는 내용은 MCP로 다시 조회하지 않는다.
  `describe_toolset`은 결과가 수만 자라 금지. 모르는 도구는 엔진 파이썬 소스를 grep한다
  (`C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\**\*.py`).
- 기능 하나가 끝나면 `/compact` 또는 새 세션을 제안한다.

### 매번 지키는 토큰 규칙
1. **MCP 호출은 한 번에 묶는다.** 여러 도구 호출은 `ProgrammaticToolset.execute_tool_script` 하나로 실행하고,
   필요한 값만 dict로 돌려받는다. 실패할 수 있는 단계(PIE 시작 등)는 맨 끝에 둔다.
2. **확인은 숫자로 먼저.** 크기·위치는 `get_actor_bounds`, 값은 `get_properties`로 본다.
   이미지는 숫자로 판단이 안 될 때만, `Tools/DecodeCapture.ps1`로 480px 이하로 줄여 한 장에 이어 붙여 본다.
3. **C++ 빌드는 스크립트 한 줄.** MCP `save_assets([])` 후 `Tools/Rebuild.ps1` 실행. 빌드 로그 전체를 읽지 않는다.
   BP 값·에셋만 바꾼 경우는 빌드하지 않는다.
4. **플레이 체감은 사용자에게 맡긴다.** 키·마우스 입력은 MCP로 못 넣는다. PIE는 오류 로그 확인용으로 한 번만 돌리고,
   화면 판단이 필요하면 사용자 스크린샷을 받는다. 같은 문제를 추측으로 두 번 이상 고치지 않고 먼저 원인을 묻는다.
5. **파일은 필요한 부분만 읽는다.** 이미 읽은 파일은 다시 읽지 않고, 큰 파일은 `offset/limit` 또는 Grep으로 본다.
6. **응답은 짧게.** 결과 요약·바뀐 값·조정 위치만 쓴다. 과정 설명과 이미 말한 내용을 반복하지 않는다.
7. **새로 알게 된 사실은 바로 기록한다.** 도구 사용법은 `.claude/unreal-tools.md`, 에셋·구조 규칙은 이 파일에 한 줄로.
   같은 조사를 두 번 하지 않기 위해서다.

## 프로젝트 구조
- 엔진 버전: UE 5.8 (`C:\Program Files\Epic Games\UE_5.8`), C++ 모듈 `ProjectR`
- 레벨: `/Game/Maps/DevMap` (월드 세팅 게임모드 `BP_GameMode`, PlayerStart (0,0,92) yaw 0, 허수아비 (250,0,0) yaw 90)
- Unreal MCP: `http://127.0.0.1:8010/mcp` (Config/DefaultEditorPerProjectUserSettings.ini에서 자동 시작)
- C++ (`Source/ProjectR/`)
  - `AProjectRCharacter`: 이동·시점(Enhanced Input을 코드에서 생성), 몽타주 콤보, `Hit` 노티파이 타격 판정,
    카메라 `FirstPersonCamera` 하나(캡슐에 붙음, 마우스 좌우·위아래, 코드는 카메라·메시 Transform을 덮어쓰지 않음 → BP 뷰포트 값 그대로), `CameraViewOffset`, 공격 시 카메라 전진, 공격별 검 회전
  - `ATrainingDummy`: 맞으면 흔들리고 횟수 표시 / `UProjectRAnimInstance`: `Speed`, `bIsInAir`
  - `USkillTreeComponent`(캐릭터의 `SkillTree`): 포인트·해금, 그림·배치 수치(`Style`) / `USkillTreeWidget`: 표를 읽어 원형 트리를 코드로 생성, K로 열기, 드래그 이동·휠 확대(배율은 `Style`의 View 항목), 노드 설명창(`Style`의 Tooltip 항목, 그림 `T_SkillTooltip`을 위·가운데·아래로 잘라 가운데만 세로로 늘림. UI 그림은 표시 크기의 1.5배 정도로 미리 줄여 넣는다)
  - `UPlayerStatsComponent`(캐릭터의 `Stats`): 스탯 `EPlayerStat` 15종, 기본값 `BaseStats`(BP에서 조정) + 해금한 스킬 보너스. 최종 = (기본 + 더하기) × (1 + %/100).
    현재 체력·마나와 재생, 방어 = 피해 × 100/(100+방어력−관통). 기본 공격 피해·치명타·공격 속도(몽타주 재생 속도)는 이미 연결됨. 특수 스킬(Stat=None)은 효과 미구현
  - `UPlayerSkillComponent`(캐릭터의 `Skills`): 젬 3칸 Q·E·R(`GemSkills`) + 무기 고유 스킬 F(`WeaponSkill`, 무기 액터가 생기면 무기로 옮김). 효과 종류 `ESkillEffect`(Dash/Spin/Slam/Heal), 효과는 `HitDelay` 초 뒤. 스킬 모션 중엔 기본 공격 막힘
    스킬 표 `SourceArt/Data/Skills.csv` → `/Game/Data/DT_Skills`(바꾸면 지우고 다시 임포트). 스킬 모션 `AM_Skill_<이름>`(미사모 원본 `SourceArt/Mixamo/Anim_Skill_*.fbx`, 팔만 남긴 것 `SourceArt/Export/A_Skill_*_ArmsOnly.fbx`)
  - `UPlayerHUDWidget`: 화면 아래 가운데 1~0 아이템 칸 10개(빈 칸) + 그 위 체력 바(왼쪽 반)·마나 바(오른쪽 반), 숫자 표시. 그림·배치는 캐릭터의 `HUDStyle`(그림 `/Game/UI/HUD/T_HudPanel`(전체를 감싸는 판)·`T_HudBar`·`T_HudSlot`, 판과 바 틀은 양끝 장식 비율 유지하고 가운데만 가로로 늘림)
- 스킬 표: 원본 `SourceArt/Data/SkillTree.csv`(UTF-8, 열 `---,DisplayName,Parent,Cost,Icon,Description,Stat,StatValue,bStatPercent`) → `/Game/Data/DT_SkillTree`(바꾸면 지우고 다시 임포트). UI 그림 `/Game/UI/SkillTree/`
- 스킬 아이콘: `SourceArt/UI/SkillIcons/T_Skill_<스킬ID>.png`(256px, 투명) → `/Game/UI/SkillIcons/`. 새 아이콘은 크롬(Claude in Chrome)에서 제미나이로 4x4 시트를 뽑아 `Tools/SliceIconSheet.ps1`로 자른다. 표의 Icon 칸은 `/Game/UI/SkillIcons/T_Skill_<ID>.T_Skill_<ID>`
- BP (`/Game/Blueprints/`): `BP_PlayerCharacter`(메시 `SK_PlayerArms`, 콤보 `AM_Attack5`→`AM_Attack2`,
  카메라 위치는 BP에서 눈 높이로), `BP_TrainingDummy`, `BP_GameMode`
- 캐릭터 (`/Game/Characters/Player/`): `SK_Player`(전신), `SK_PlayerArms`(튜닉 몸통 재질 분리), 스켈레톤 `SK_Player_Skeleton`,
  `ABP_Player`(BS_Locomotion: A_Idle·A_Walk_ArmsOnly·A_Run_ArmsOnly → Slot DefaultSlot. 걷기·달리기도 팔만 움직이고 몸은 제자리), `Animations/`, `Montages/`
- 공격 애니메이션은 미사모 원본(`SourceArt/Mixamo`)에서 팔 본만 남기고 몸은 대기 자세로 고정해 만든다
  (`SourceArt/Export/A_Attack*_ArmsOnly.fbx`). Hit 노티파이는 오른손 속도가 최대인 프레임에 둔다.
- 폴더 규칙: 개발용 스크립트는 `Tools/`, 프로젝트 툴셋은 `Content/Python/projectr_toolset/`
- 네이밍 규칙: UE 표준 접두사(`BP_`, `WBP_`, `M_`, `MI_`, `SM_`, `SK_`, `T_`, `ABP_`, `NS_`)
- 글꼴: 상업적 무료(SIL OFL 등)만 쓴다. 원본·라이선스는 `SourceArt/Fonts/`, 에셋은 `/Game/UI/Fonts/FF_<이름>`(FontFace, Inline). 설명창 글꼴은 나눔손글씨 펜(`FF_NanumPenScript`), HUD 숫자는 Cinzel Bold(`FF_Cinzel`, 영문·숫자만 있고 한글 없음). 이 글꼴엔 `·` 같은 특수기호가 없어 네모로 깨진다(표 설명에도 쓰지 말 것)

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
