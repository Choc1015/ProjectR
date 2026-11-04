# C++ 변경 후 한 번에: 에디터 종료 → 빌드 → 에디터 실행 → MCP(8010) 대기.
# 실행 전에 MCP로 AssetTools.save_assets([])를 호출해 저장해 둔다.
# 출력은 빌드 오류/결과 줄만 남겨 토큰을 아낀다.
param([int]$ExitTimeout = 90)

$ue = "C:\Program Files\Epic Games\UE_5.8\Engine"
$proj = "C:\UnrealProject\ProjectR\ProjectR.uproject"

$p = Get-Process UnrealEditor -ErrorAction SilentlyContinue
if ($p) {
    $p.CloseMainWindow() | Out-Null
    if (-not $p.WaitForExit($ExitTimeout * 1000)) { "EDITOR_DID_NOT_EXIT (저장 확인 창이 떠 있을 수 있음)"; exit 1 }
}

& "$ue\Build\BatchFiles\Build.bat" ProjectREditor Win64 Development "-Project=$proj" -WaitMutex 2>&1 |
    Select-String -Pattern "error|warning C|Result:" | Select-Object -First 15 | ForEach-Object { $_.Line }
if ($LASTEXITCODE -ne 0) { "BUILD_FAILED"; exit 1 }

Start-Process "$ue\Binaries\Win64\UnrealEditor.exe" -ArgumentList "`"$proj`""
Start-Sleep 30
for ($i = 0; $i -lt 60; $i++) {
    if (Get-NetTCPConnection -LocalPort 8010 -State Listen -ErrorAction SilentlyContinue) { break }
    Start-Sleep 5
}
Start-Sleep 15
"EDITOR_UP"
