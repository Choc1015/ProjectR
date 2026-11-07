<!-- CLAUDE.md에서 옮겨 옴(2026-11-07). 맵·방 작업 전에 읽는다. -->
## 맵 규칙 (사용자가 정함)

- 맵은 **방 단위**로 만들어 계속 찍어낸다. 방은 실내가 아니라 **세상 한 조각을 방 크기에 담은 것**(숲, 폐허 등 바깥 풍경도 방 하나).
- 방마다 입구·출구가 있고, 가운데는 몬스터와 싸울 공간, 둘레는 소품으로 알뜰하게 채운다.
- 순서: 제미나이로 테마·소품 레퍼런스를 뽑아 보여 준다 → 사용자가 고른다 → 블렌더로 만든다 → 언리얼에 배치 → 사용자 검수.
- 레퍼런스는 `Docs/ArtRef/Rooms/`. 2026-11-07 밤샘으로 10개 더 만듦(Oasis·SnowShrine·Forge·Greenhouse·Harbor·Mushroom·Library·Vineyard·Mill·Chapel, 검수 전, 보고서 `Docs/Rooms/2026-11-07_밤샘_방_제작.md`). 첫 방 테마: 숲속 신전 폐허. 두 번째 방: 버려진 광산 동굴 `L_Room_Mine`(약자 MN, 바위벽·바위 천장 틈 3곳, 나무 갱도 틀 출구, 밤: 랜턴 불빛이 주광이고 사용자가 원해서 발광·포인트 라이트를 씀). DevMap에는 PostProcessVolume이 없어 방 라이팅 스크립트가 처음 한 번 만든다.
- 방 만드는 전체 절차·결정 묶음은 프로젝트 스킬 `.claude/skills/make-room/SKILL.md`, 방별 조립 스크립트는 `Tools/Rooms/<테마>/`(README에 번호별 설명). 방 수정은 해당 번호 스크립트를 고쳐 다시 돌린다.
- 방 레벨은 `/Game/Maps/Rooms/L_Room_<테마>`(DevMap을 복제해 조명 유지). 방 크기 24m x 24m, 중심 원점, 바닥은 2m 타일 12x12(두 모양을 섞고 돌려 반복 무늬 방지, 이끼는 타일에 넣지 않고 큰 덩어리로 따로).
- 출구는 뚫지 않고 검은 판을 채운 아치문 `SM_FT_ExitDoor`(동쪽 +X 벽 가운데. 벽 모듈 이음매의 기둥·받침을 가리려고 검은 판을 벽에서 38cm 앞에 두고 문턱 없음). 입구는 아직 없음.
- 방은 사방 벽과 천장으로 막는다(숲속 신전: 높이 8m 석조 벽 4m 모듈(문 없이 막힘, 이끼는 `TempleWallMoss` 몇 개만 불규칙하게·일부 좌우 반전, 벽 장식 `SM_FT_Wall*` 8종을 위치·높이·크기·좌우 반전을 섞어 16개, 장식 원점은 벽면 Y=0이고 방 쪽으로 튀어나옴. 랜턴 발광·조명은 없음)
- 라이팅(숲속 신전): 해 pitch -62 yaw 30·40 lux, 스카이라이트 1.2(아래 반구 따뜻한 회색, 구석이 새까맣지 않게), 볼류메트릭 안개, PostProcessVolume_0 노출 고정 EV 3.6. 빛줄기는 진짜 빛 + 볼류메트릭 안개로만(해 산란 20, 안개 밀도 0.08·산란 분포 0.9). 빛기둥 메시 `SM_FT_LightShaft`는 만들어 뒀지만 배치하지 않음(사용자 선택). 빛 떨어지는 곳마다 떠다니는 빛 먼지 `NS_FT_LightDust`(엔진 HangingParticulates 템플릿, 따뜻한 HDR 색, 상자 320x320x650)
- 나이아가라 MCP: `NiagaraToolsets.NiagaraToolset_System.*`(CreateNiagaraSystem은 템플릿 시스템 필수 → MinimalLightweight로 만들고 RemoveEmitter·AddEmitter), 입력은 GetEmitterTopology로 scriptName 찾고 SetStackInputData(struct는 GetStackInputData 결과 그대로), 천장 4m 판 6x6을 z=8m에 두고 일부는 무너진 판으로 하늘·빛이 들게).
- 소품: 블렌더 원본 `SourceArt/<테마>_Props.blend`, FBX `SourceArt/Export/<테마>/SM_<약자>_*.fbx`, 언리얼 `/Game/Props/<테마>/`(숲속 신전은 약자 FT).
- MCP 배치: `SceneTools.add_to_scene_from_asset`의 `xform`은 `{location, rotation{pitch,yaw,roll}, scale}` 형식이다(`translation`/쿼터니언을 넘기면 조용히 원점에 놓인다).

