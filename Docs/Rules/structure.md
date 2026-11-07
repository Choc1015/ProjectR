<!-- CLAUDE.md에서 옮겨 옴(2026-11-07). C++·BP·데이터 표·UI·무기 작업 전에 읽는다. -->
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
  - 인벤토리: `UInventoryComponent`(캐릭터의 `Inventory`, 가방 20칸 + 장착칸 무기 1·젬 Q·E·R, 런 동안 `URunSubsystem`에 저장, 시작 아이템 `StartItems`, 창 그림·배치 `Style`) / `UInventoryWidget`(I로 열기, 게임 멈춤, 검은 바탕 위 찢어진 일지, 끌어다 놓기로 장착·옮기기, 우클릭으로 포션 마시기·장착). 아이템 표 `SourceArt/Data/Items.csv` → `/Game/Data/DT_Items`(행 이름 = 아이템 ID, 젬은 스킬 ID·무기는 무기 ID와 같게). 그림 `/Game/UI/Inventory/`(원본 `SourceArt/UI/Inventory/`, 임포트 `Tools/Inventory/01_import_textures_and_table.py`). 바닥 무기는 E로 줍으면 가방으로 들어간다
  - 방 지도(런): `URunSubsystem`(게임 인스턴스, 레벨을 옮겨도 지도 유지. 시작 칸 + 줄 6 x 열 5에 길 3개, 칸마다 방을 정하되 바로 아래 칸과 같은 방은 피함) / `URoomWorldSubsystem`(게임 월드 시작 시 메시 이름이 `_ExitDoor`로 끝나는 스태틱 메시 액터마다 `ARoomExitDoor` 판정을 자동으로 붙임 → 방 레벨에 따로 놓을 것 없음) / `URoomMapWidget`(지도 화면 코드 생성, 게임 일시정지, 갈 수 있는 칸만 숨쉬듯 커지고 클릭하면 `OpenLevel`, Esc 닫기). 방 목록·지도 크기·그림·배치는 프로젝트 세팅 > Game > Run Map(`URunSettings`, DefaultGame.ini). 맨 위 칸에서 출구로 나가면 새 지도로 처음 방부터. 지도 그림 `/Game/UI/Map/T_Map*`(원본 `SourceArt/UI/Map/`, 임포트 `Tools/UI/import_map_textures.py`)
  - 무기: 표 `SourceArt/Data/Weapons.csv` → `/Game/Data/DT_Weapons`(행 `FWeaponRow`: 메시, BP 손잡이 위치 위에 더할 오프셋, 콤보 몽타주(비우면 BP `AttackMontages`·검 회전), `bProjectileAttack`(Hit 순간 탄 발사), 탄 메시·속도·배율·발사 위치·불빛 색, 기본 공격 피해 배율 `DamageMultiplier`·모션 속도 배율 `AttackSpeedMultiplier`, 고유 스킬 F). 캐릭터 `EquipWeapon(ID)`가 `SwordMesh`(이름은 그대로, 지금 든 무기 메시) 교체. 런 동안 무기는 `URunSubsystem::CurrentWeapon`에 남아 방을 옮겨도 유지. 지금: 검(Sword, F=Sword_Dash), 스태프(Staff, 호박 탄 x0.8, F=Staff_Fireball 화염구 3m 폭발), 전투 도끼(BattleAxe, 피해 x1.4·속도 x0.8, 콤보 `AM_Axe_Attack1`→`2`(1타 미사모 Standing Melee Attack Downward를 내려찍는 동안 왼쪽으로 70도 sweep해 오른쪽→왼쪽 끝으로, 2타 Stable Sword Inward Slash Hit 1.3초, 어깨를 25도 들어 올림), F 던지기 속도 900, F=Axe_Throw 던져서 되돌아옴 `AThrownWeapon`), 번개 지팡이(StormWand, 노란 탄 피해 x0.6·모션 속도 x0.5, 기본 공격 `AM_Wand_Attack`(미사모 Bash 34~68프레임, Hit 0.5초 = 내리친 손이 앞에 오는 원본 49프레임), F=Wand_ChainLightning 연쇄 번개 3번 튐). 에셋 `/Game/Weapons/BattleAxe/`·`/Game/Weapons/StormWand/`(원본 `SourceArt/Weapons2.blend`, 원점=손잡이·대는 +Z), 조립 `Tools/Weapons/08_import_axe_and_wand.py`. 스킬 효과 `ThrowWeapon`(든 무기 메시를 던짐)·`ChainLightning`(표 열 ChainCount·ChainRadius, ProjectileMesh = +X 1m 번개 구간 메시)
  - 표를 고칠 때: 에디터가 쥔 DT는 지우고 다시 임포트가 안 된다(삭제가 안 먹고 "already exists"). `DataTableTools.add_rows`+`set_rows`로 행만 넣는다(08 스크립트 참고). CSV도 같이 고쳐 둔다
  - `AWeaponPickup`: 바닥 무기(떠서 회전, `WeaponId`만 고르면 메시는 표에서). 근처에서 E(젬 2번 칸 대신) → 가방에 넣음, HUD 가운데 안내 글 `SetPrompt`. 숲속 신전 시작 지점 앞(-650,0)에 스태프 하나
  - `AProjectRProjectile`: 탄·화염구 공용(중력 없음, 처음 닿은 곳에서 피해, `ExplosionRadius`>0이면 범위 피해 + 나이아가라). 스킬 효과 `ESkillEffect::Projectile`(스킬 표 열 ProjectileMesh·ProjectileSpeed·ImpactEffect, Range = 폭발 반지름)
  - 스태프 에셋 `/Game/Weapons/Staff/`(SM_Staff 원점=손잡이(아래 끝 0.5m 위)·대는 +Z, SM_StaffBolt, SM_Fireball, NS_FireballExplosion, 발광은 `Tools/Weapons/01`에서 재질에 꽂음). 블렌더 원본 `SourceArt/Staff.blend`. 조립 스크립트 `Tools/Weapons/01~05`
  - 팔만 남기는 모션 변환은 블렌더 MCP로 `Tools/Blender/arms_only.py`(JOBS만 바꿔 실행, 오른손 최고 속도 프레임 = Hit 시점도 알려 줌)
- 스킬 표: 원본 `SourceArt/Data/SkillTree.csv`(UTF-8, 열 `---,DisplayName,Parent,Cost,Icon,Description,Stat,StatValue,bStatPercent`) → `/Game/Data/DT_SkillTree`(바꾸면 지우고 다시 임포트). UI 그림 `/Game/UI/SkillTree/`
- 스킬 아이콘: `SourceArt/UI/SkillIcons/T_Skill_<스킬ID>.png`(256px, 투명) → `/Game/UI/SkillIcons/`. 새 아이콘은 크롬(Claude in Chrome)에서 제미나이로 4x4 시트를 뽑아 `Tools/SliceIconSheet.ps1`로 자른다. 표의 Icon 칸은 `/Game/UI/SkillIcons/T_Skill_<ID>.T_Skill_<ID>`
- BP (`/Game/Blueprints/`): `BP_PlayerCharacter`(메시 `SK_PlayerArms`, 콤보 `AM_Attack5`→`AM_Attack2`,
  카메라 위치는 BP에서 눈 높이로), `BP_TrainingDummy`, `BP_GameMode`
- 캐릭터 (`/Game/Characters/Player/`): `SK_Player`(전신), `SK_PlayerArms`(튜닉 몸통 재질 분리), 스켈레톤 `SK_Player_Skeleton`,
  `ABP_Player`(BS_Locomotion: A_Idle·A_Walk_ArmsOnly·A_Run_ArmsOnly → Slot DefaultSlot. 걷기·달리기도 팔만 움직이고 몸은 제자리), `Animations/`, `Montages/`
- 공격 애니메이션은 미사모 원본(`SourceArt/Mixamo`)에서 팔 본만 남기고 몸은 대기 자세로 고정해 만든다
  (`SourceArt/Export/A_Attack*_ArmsOnly.fbx`). Hit 노티파이는 오른손 속도가 최대인 프레임에 둔다. 몸통을 고정하면 팔 궤적이 틀어져서 `arms_only.py`가 어깨 방향을 원본의 엉덩이 기준 방향으로 다시 맞춘다(2026-11-06 고침. 그 전에 만든 검·스태프 모션은 예전 방식)
  미사모 모션은 몸통이 크게 도는 것·마법 시전 모션은 고르지 않고 휘두르는 모션을 고른다(무기 이름 키워드에 얽매이지 않음). 몸통을 돌려 좌우를 바꾸는 꼼수는 사용자가 싫어함. 후보 몇 개를 받아 팔만 남긴 오른손 궤적(앞·오른쪽·위)을 재고, 최종 선택은 사용자에게 이름으로 묻는다(미사모에서 미리 볼 수 있음).
- 폴더 규칙: 개발용 스크립트는 `Tools/`, 프로젝트 툴셋은 `Content/Python/projectr_toolset/`
- 네이밍 규칙: UE 표준 접두사(`BP_`, `WBP_`, `M_`, `MI_`, `SM_`, `SK_`, `T_`, `ABP_`, `NS_`)
- 글꼴: 상업적 무료(SIL OFL 등)만 쓴다. 원본·라이선스는 `SourceArt/Fonts/`, 에셋은 `/Game/UI/Fonts/FF_<이름>`(FontFace, Inline). 설명창 글꼴은 나눔손글씨 펜(`FF_NanumPenScript`), HUD 숫자는 Cinzel Bold(`FF_Cinzel`, 영문·숫자만 있고 한글 없음). 이 글꼴엔 `·` 같은 특수기호가 없어 네모로 깨진다(표 설명에도 쓰지 말 것)

