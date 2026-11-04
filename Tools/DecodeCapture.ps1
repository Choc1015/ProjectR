# MCP CaptureViewport 결과를 작은 PNG로 만든다(이미지 토큰 절약).
# MCP 스크립트에서 r['image']['data']를 AssetTools.write_file로 Saved/<Name>.txt 에 쓴 뒤 실행한다.
# 여러 이름을 주면 가로로 이어 붙인다. 읽은 .txt는 지운다.
param([string[]]$Names = @("vp"), [int]$Width = 480, [string]$Out = "")

Add-Type -AssemblyName System.Drawing
$saved = "C:\UnrealProject\ProjectR\Saved"
if (-not $Out) { $Out = Join-Path $env:TEMP "projectr_capture.png" }

$imgs = foreach ($n in $Names) {
    $f = Join-Path $saved "$n.txt"
    $b = [Convert]::FromBase64String((Get-Content $f -Raw).Trim())
    Remove-Item $f
    [Drawing.Image]::FromStream((New-Object IO.MemoryStream(, $b)))
}
$h = [int]($Width * $imgs[0].Height / $imgs[0].Width)
$canvas = New-Object Drawing.Bitmap ($Width * $imgs.Count), $h
$g = [Drawing.Graphics]::FromImage($canvas)
for ($k = 0; $k -lt $imgs.Count; $k++) { $g.DrawImage($imgs[$k], $k * $Width, 0, $Width, $h) }
$canvas.Save($Out)
$Out
