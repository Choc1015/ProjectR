---
name: make-room
description: Use when the user asks to make a new map room, a new room theme, more rooms, or to edit an existing room (forest temple etc.) in ProjectR. Covers the whole pipeline from Gemini references to Blender props, Unreal room level, lighting and review, with the user's choices batched into as few questions as possible.
---

# 방 만들기 (ProjectR)

방 하나 = 세상 한 조각을 방 크기에 담은 전투 공간. 계속 찍어낸다. 첫 방(숲속 신전 폐허, `L_Room_ForestTemple`)이 기준 예시이고, 만든 과정은 `Tools/Rooms/README.md`와 `Tools/Rooms/ForestTemple/*.py`에 있다. CLAUDE.md의 맵 규칙·아트 통일 규칙·MCP 규칙을 그대로 따른다.

## 사용자 결정은 한 번에 묶어서 묻는다 (사용자 요청)

사용자가 골라야 하는 것은 단계마다 흩어 묻지 말고 **두 번의 묶음 질문**으로 끝낸다. 각 질문은 AskUserQuestion 한 번(최대 4문항)으로, 추천안을 첫 번째에 둔다.

**묶음 1 — 테마 고르기** (레퍼런스 이미지와 함께)
1. 테마: 2x2 콘셉트 4개 중 하나(섞기·다른 테마는 "기타")
2. 방 크기: 24m(기준) / 16m / 32m
3. 막는 방식: 그 테마에 맞는 벽·천장 2~3안(예: 석조 벽+무너진 천장, 동굴 바위벽+종유석 천장, 나무 울타리+나뭇잎 천장)
4. 빛 분위기: 2~3안(예: 천장 틈 햇빛+빛 먼지, 횃불·화로 위주, 달빛·푸른 톤)

**묶음 2 — 상세 확인** (방 콘셉트·소품 시트·벽 장식 시트를 한꺼번에 보여 준 뒤)
1. 소품 시트: 그대로 / 뺄 것·더할 것
2. 벽 장식 시트: 그대로 / 고칠 것
3. 출구 모양: 검은 판 아치(기준) / 테마에 맞춘 다른 틀
그 뒤로는 검수 단계까지 묻지 않고 끝까지 만든다. 검수 피드백은 스크린샷으로 받아 고친다.

## 순서

1. **레퍼런스 (Claude in Chrome → 제미나이)** — 대화창 `https://gemini.google.com/app/273b03221003647f`에서 뽑는다. 프롬프트 맨 앞에 `Draw a brand-new separate image from scratch (do not reuse or edit the previous images).`를 붙인다(안 붙이면 앞 그림을 고쳐 버린다). 템플릿은 `Docs/ArtRef/GeminiPrompts.md`의 "방(맵) 콘셉트" 절. 결과는 `Docs/ArtRef/Rooms/<테마>_*.png`.
   - 묶음 1 전: 테마 2x2 콘셉트 1장
   - 묶음 2 전: 고른 테마의 (a) 막힌 방 내부 콘셉트(벽·천장 포함, 앞 두 벽을 잘라낸 컷어웨이), (b) 소품 시트 4x4, (c) 벽 장식 시트 3x3 — 세 장을 연달아 뽑아 한 번에 보여 준다.
2. **블렌더 모델링 (blender-worker에 위임)** — 소품(돌·건축), 자연물, 벽·천장·바닥 조각, 벽 장식을 묶음별로 위임. 원본 `SourceArt/<테마>_Props.blend`, FBX `SourceArt/Export/<테마>/SM_<약자>_*.fbx`. 위임 프롬프트에 아래 "블렌더 규칙"을 그대로 넣는다. 작은 수정(메시 한두 개)은 메인에서 직접 한다.
3. **언리얼 조립** — `Tools/Rooms/<테마>/`에 번호 스크립트를 새로 만들어 `Tools/McpRun.ps1`로 돌린다(ForestTemple 스크립트를 복사해 테마 약자·좌표만 바꾸는 게 빠르다). DevMap을 `/Game/Maps/Rooms/L_Room_<테마>`로 복제해 조명을 유지하고, 허수아비·바닥은 지운다.
4. **라이팅** — ForestTemple 최종값에서 시작해 테마에 맞게 조정(README 표). 랜턴 같은 발광·포인트 라이트는 넣지 않는다(사용자가 과하다고 함).
5. **검수** — 에디터 캡처(`Tools/Rooms/capture.py`)로 배치만 숫자·그림으로 확인하고, 분위기는 사용자 플레이 스크린샷으로 판단한다. 같은 문제를 추측으로 두 번 고치지 않는다.
6. **기록·백업** — 단계마다 커밋·푸쉬(서명 줄은 세션 지침). 새 프롬프트는 GeminiPrompts.md에, 새 사실은 CLAUDE.md에 한 줄로. 방 하나가 끝나면 개발일지를 끊을지 제안한다.

## 배치 기준 (24m 방)

- 중심 원점, 바닥 2m 타일 12x12. 타일은 두 모양 이상을 섞고 90도 단위로 돌려 반복 무늬를 없앤다. 이끼·얼룩은 타일에 넣지 않고 큰 불규칙 덩어리 몇 개만 따로.
- 사방 벽(4m 모듈, 높이 8m)과 천장(4m 판 6x6, z=8m, 일부는 무너진 판). 벽 장식은 위치·높이·크기·좌우 반전을 섞어 띄엄띄엄. 같은 장식이 규칙적으로 반복되면 안 된다.
- 가운데 약 14m는 싸울 공간(낮은 엄폐물 1~2개만), 둘레 5m 띠를 소품으로 알뜰하게.
- 시작 위치(PlayerStart) -X 쪽, 출구는 +X 벽 가운데의 검은 판 아치(뚫지 않음, 문턱 없음). 벽 모듈 이음매의 기둥·받침이 문 뒤로 가려지게 검은 판을 벽에서 앞으로 뺀다.
- 출구 메시 이름은 반드시 `SM_<약자>_ExitDoor`(정면 로컬 +Y가 방 쪽). 게임 시작 때 이 메시 자리에 출구 판정이 자동으로 붙어 방 지도가 열린다. 새 방은 프로젝트 세팅 > Game > Run Map의 Rooms에 레벨과 이름을 추가해야 지도에 나온다.
- `add_to_scene_from_asset`의 `xform`은 `{location, rotation{pitch,yaw,roll}, scale}`.
- 벽에 붙는 것은 블렌더에서 벽면 Y=0, 방 쪽이 -Y로 만든다 → 언리얼 yaw: 남(-Y 벽) 0, 북 180, 서 270, 동 90.

## 블렌더 규칙 (위임 프롬프트에 넣을 것)

- 스타일라이즈드 로우폴리, 면 셰이딩, 단색 머티리얼만, 밝고 아늑한 톤. 테마 머티리얼은 `M_<약자>_*`로 공유.
- 원점은 바닥 중앙(Z 최저점 0), 정면 -Y, 트랜스폼 적용. 천장은 아랫면 중앙, 늘어지는 것은 위 중앙.
- 익스포트: `use_selection=True, object_types={'MESH'}, apply_scale_options='FBX_SCALE_NONE', mesh_smooth_type='FACE'`, 원점에 둔 채로.
- 겹치는 면 금지: 같은 평면에 두 판을 겹치지 않는다(깜빡임), 블록끼리 서로 파고들지 않게 이어 붙인다.
- 벽을 뚫고 나온 나무뿌리 같은 큰 유기물 장식은 쓰지 않는다(사용자가 뺌).
- MCP: `read_factory_settings`·`read_homefile`·다른 파일 열기 금지(연결이 끊긴다). 씬 정리는 bpy.data로 직접. 호출은 하나씩.

## 자주 걸린 문제

- 제미나이 새 대화창은 이미지 생성을 거부한 적이 있다 → 위 대화창을 계속 쓴다.
- 에디터 캡처에는 볼류메트릭 안개·나이아가라가 안 보인다.
- 나이아가라 만들기는 CLAUDE.md의 "나이아가라 MCP" 줄 참고(빛 먼지 `NS_FT_LightDust`는 다른 방에서도 재사용 가능).
- 라이트 색(`lightColor`)은 0~1 선형 값으로 넣는다. 0~255는 흰색으로 잘린다.
- 다른 방 스크립트를 복사할 때 `LV`/`load_level`의 레벨 이름과 `/Game/Props/<테마>/` 경로를 전부 바꿨는지 grep으로 확인한다(06이 레벨을 열기 때문에, 틀리면 03~05가 남의 방에 놓인다).
- 발광은 FBX로 안 넘어온다 → 방의 `09_glow.py`로 머티리얼에 직접 연결(불꽃·유리·버섯처럼 빛나는 것은 언릿). 빛나는 모델 자리에 같은 색 포인트 라이트를 두면 "모델에서 빛이 난다"로 읽힌다(사용자 피드백).
- 제미나이 이미지 생성은 한도가 있다(하룻밤 두 번 걸림, 각 약 1~1.5시간). 걸리면 직전 2x2의 남은 테마 그림 한 장으로 블렌더를 시작해도 된다.
- 바닥 타일 두 종 섞기는 `(gx*5+gy*3+gx*gy)%3`보다 해시 `((gx*73856093)^(gy*19349663))%5`가 무늬가 덜 보인다(대비가 큰 타일일 때).
- 방 하나 = 2x2 → 레퍼런스 3장 → blender-worker 한 번(구조+소품+장식 전부) → 번호 스크립트 → 캡처. 본보기 스크립트: 낮 천 차양 `Oasis`, 판 지붕 `SnowShrine`/`Harbor`, 밤 발광 `Forge`/`Mushroom`, 촛불 `Library`/`Chapel`.
