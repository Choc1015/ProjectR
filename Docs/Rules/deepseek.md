# DeepSeek 위임 규칙 (Claude Code 전용)

> **이 파일은 Claude(Opus·Sonnet)로 돌고 있을 때만 따른다.**
> 네가 OpenCode의 DeepSeek라면 이 파일을 무시한다. 너 자신에게 다시 위임하지 않는다.

Claude 주간 토큰을 아끼려고, 판단이 필요 없는 일은 OpenCode의 DeepSeek에게 넘긴다.
DeepSeek는 Claude보다 수십 배 싸지만 **이미지를 못 보고**, 설계 판단은 Claude보다 약하다.
그래서 Claude는 "결정·검토"를, DeepSeek는 "지시가 분명한 실행"을 맡는다.

## 무엇을 넘기나

| DeepSeek에게 넘긴다 | Claude가 직접 한다 |
|---|---|
| 언리얼 MCP 배치·수정·조회 (지금 `unreal-worker` 서브에이전트에 줄 일) | 이미지·스크린샷 보고 판단, 아트 검수, 레퍼런스 비교 |
| 블렌더 모델링·익스포트 중 숫자로 확인되는 것 (지금 `blender-worker`에 줄 일) | 사용자에게 묻기·선택지 정리 (AskUserQuestion) |
| 설계가 끝난 C++ 구현 (함수·클래스·수정 위치가 정해진 것) | 새 시스템 설계, 클래스 구조 결정, 버그 원인 분석 |
| CSV·DT 행 추가·수정, 반복 스크립트 실행 | DeepSeek 결과 검토와 최종 확인 |
| 코드·폴더 검색과 요약, 빌드 오류 로그 요약 | DeepSeek가 2번 실패한 일 |
| 개발일지 초안 (Claude가 다듬음) | 커밋·푸쉬 |

애매하면 "Claude가 결정할 것"과 "그대로 실행만 하면 될 것"으로 쪼개서 뒤쪽만 넘긴다.
1~2번 호출로 끝나는 아주 작은 일은 넘기지 않고 직접 한다(위임 지시문이 더 길어진다).

## 어떻게 넘기나

PowerShell에서 실행한다. 프로젝트 루트(`C:\UnrealProject\ProjectR`)에서.

| 할 일 | 명령 |
|---|---|
| 언리얼 조작 | `opencode.cmd run --agent unreal-worker --title "<짧은 제목>" "<지시>"` |
| 블렌더 조작 | `opencode.cmd run --agent blender-worker --title "<짧은 제목>" "<지시>"` |
| 코드 작성·수정·검색 | `opencode.cmd run --title "<짧은 제목>" "<지시>"` (기본 Flash) |
| 어려운 구현 | 위 명령에 `-m deepseek/deepseek-v4-pro` 추가 |

- 출력에는 도구 호출 기록이 섞여 길다. **끝부분만 읽는다**: 명령 뒤에 `2>&1 | Select-Object -Last 25`.
- 1분 넘게 걸릴 일은 백그라운드로 돌리고 끝나면 결과를 본다.
- 서로 같은 파일을 건드리는 위임을 동시에 두 개 돌리지 않는다.

### 지시문 쓰는 법

DeepSeek는 이 대화를 모른다. 지시문 하나로 끝까지 할 수 있게 쓴다.

```
[목표] 무엇을 하는지 한 줄
[대상] 파일 경로 / 에셋 경로 / 액터 이름
[할 일] 1. ... 2. ... (값까지 정해서)
[하지 말 것] 커밋·푸쉬 금지. 지시 밖 파일 수정 금지. 모르면 추측하지 말고 멈춰서 보고.
[참고] 읽어야 할 규칙 파일 (예: Docs/Rules/asset.md)
[보고] 마지막에 "결과: 성공/실패", 바뀐 것 한 줄씩(최대 10줄)
```

## 받은 뒤

- **믿지 말고 확인한다.** 코드면 `git diff --stat`과 바뀐 부분만 읽고, 빌드는 `Tools/Rebuild.ps1`.
  언리얼·블렌더면 숫자 하나(`get_actor_bounds`, 오브젝트 수 등)로 확인한다.
- 틀렸으면 고칠 점만 담아 한 번 더 넘긴다(`-c`로 이어서 하면 앞 맥락이 남는다).
  **같은 일이 2번 실패하면** 더 넘기지 말고 Claude(또는 Sonnet 워커)가 직접 한다.
- 화면으로만 판단할 수 있는 결과는 Claude가 스크린샷으로 보거나 사용자에게 확인을 받는다.

## 비용

- 사용량: `opencode.cmd stats`. 잔액은 platform.deepseek.com.
- 잔액이 바닥나면 `402 Insufficient Balance`로 실패한다. 그때는 사용자에게 알리고 기존 방식(Sonnet 워커)으로 돌아간다.
