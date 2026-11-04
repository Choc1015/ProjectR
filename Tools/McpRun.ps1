# 언리얼 MCP 연결이 끊긴 세션에서도 HTTP로 바로 ProgrammaticToolset 스크립트를 실행한다.
# 사용: Tools/McpRun.ps1 -ScriptFile <run()이 dict를 반환하는 .py>
param([Parameter(Mandatory)][string]$ScriptFile, [string]$Url = "http://127.0.0.1:8010/mcp")

$h = @{ Accept = "application/json, text/event-stream" }
function Post([string]$json) {
    $r = Invoke-WebRequest -Uri $Url -Method Post -Headers $h -ContentType "application/json; charset=utf-8" `
        -Body ([Text.Encoding]::UTF8.GetBytes($json)) -UseBasicParsing -TimeoutSec 900
    if ($r.Headers["Mcp-Session-Id"]) { $h["Mcp-Session-Id"] = $r.Headers["Mcp-Session-Id"] }
    [Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray())
}
function Call([string]$tool, [string]$argsJson) {
    Post ('{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"call_tool","arguments":{' +
        '"toolset_name":"editor_toolset.toolsets.programmatic.ProgrammaticToolset","tool_name":"' + $tool +
        '","arguments":' + $argsJson + '}}}')
}

Post '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"mcprun","version":"1"}}}' | Out-Null
Post '{"jsonrpc":"2.0","method":"notifications/initialized"}' | Out-Null
Call "get_execution_environment" "{}" | Out-Null
$script = ConvertTo-Json ([IO.File]::ReadAllText($ScriptFile, [Text.Encoding]::UTF8))
$res = Call "execute_tool_script" ('{"script":' + $script + '}') | ConvertFrom-Json
($res.result.content | ForEach-Object { $_.text }) -join "`n"
