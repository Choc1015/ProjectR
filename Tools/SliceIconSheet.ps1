# 제미나이 아이콘 시트(흰 배경, 격자)를 칸마다 잘라 흰 배경을 지우고 정사각 PNG로 저장한다.
# 사용: Tools/SliceIconSheet.ps1 -Sheet a.png -Names A,B,C,... -OutDir SourceArt/UI/SkillIcons [-Cols 4 -Rows 4 -Size 256]
# 한 장짜리 그림(설명창 틀 등)은 -Cols 1 -Rows 1 -Size 0 -Prefix ""  → 흰색만 지우고 비율 그대로 잘라 저장
param(
    [Parameter(Mandatory)][string]$Sheet,
    [Parameter(Mandatory)][string[]]$Names,
    [Parameter(Mandatory)][string]$OutDir,
    [int]$Cols = 4, [int]$Rows = 4, [int]$Size = 256, [int]$Tolerance = 40, [string]$Prefix = "T_Skill_"
)
Add-Type -AssemblyName System.Drawing
if (-not ("IconSlicer" -as [type])) {
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
public static class IconSlicer
{
    public static void Cut(Bitmap src, Rectangle cell, int tol, int size, string path)
    {
        int w = cell.Width, h = cell.Height;
        Bitmap b = src.Clone(cell, PixelFormat.Format32bppArgb);
        bool[] seen = new bool[w * h];
        Queue<int> q = new Queue<int>();
        for (int x = 0; x < w; x++) { q.Enqueue(x); q.Enqueue((h - 1) * w + x); }
        for (int y = 0; y < h; y++) { q.Enqueue(y * w); q.Enqueue(y * w + w - 1); }
        while (q.Count > 0)
        {
            int i = q.Dequeue();
            if (seen[i]) continue;
            int x = i % w, y = i / w;
            Color c = b.GetPixel(x, y);
            if (255 - Math.Min(c.R, Math.Min(c.G, c.B)) > tol) continue;
            seen[i] = true;
            b.SetPixel(x, y, Color.FromArgb(0, 255, 255, 255));
            if (x > 0) q.Enqueue(i - 1);
            if (x < w - 1) q.Enqueue(i + 1);
            if (y > 0) q.Enqueue(i - w);
            if (y < h - 1) q.Enqueue(i + w);
        }
        int minX = w, minY = h, maxX = -1, maxY = -1;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                if (b.GetPixel(x, y).A > 0) { minX = Math.Min(minX, x); maxX = Math.Max(maxX, x); minY = Math.Min(minY, y); maxY = Math.Max(maxY, y); }
        if (maxX < 0) { b.Dispose(); return; }
        int bw = maxX - minX + 1, bh = maxY - minY + 1, side = Math.Max(bw, bh);
        if (size <= 0)
        {
            using (Bitmap crop = b.Clone(new Rectangle(minX, minY, bw, bh), PixelFormat.Format32bppArgb)) crop.Save(path, ImageFormat.Png);
            b.Dispose();
            return;
        }
        int inner = (int)(size * 0.9);
        float scale = (float)inner / side;
        using (Bitmap outBmp = new Bitmap(size, size, PixelFormat.Format32bppArgb))
        using (Graphics g = Graphics.FromImage(outBmp))
        {
            g.Clear(Color.Transparent);
            g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
            g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.HighQuality;
            float dw = bw * scale, dh = bh * scale;
            g.DrawImage(b, new RectangleF((size - dw) / 2f, (size - dh) / 2f, dw, dh), new RectangleF(minX, minY, bw, bh), GraphicsUnit.Pixel);
            outBmp.Save(path, ImageFormat.Png);
        }
        b.Dispose();
    }
}
"@
}
New-Item -ItemType Directory -Force $OutDir | Out-Null
$src = New-Object System.Drawing.Bitmap((Resolve-Path $Sheet).Path)
$cw = [int][Math]::Floor($src.Width / $Cols); $ch = [int][Math]::Floor($src.Height / $Rows)
for ($i = 0; $i -lt [Math]::Min($Names.Count, $Cols * $Rows); $i++) {
    if (-not $Names[$i]) { continue }
    $rect = [System.Drawing.Rectangle]::new(($i % $Cols) * $cw, [Math]::Floor($i / $Cols) * $ch, $cw, $ch)
    $out = Join-Path (Resolve-Path $OutDir).Path ($Prefix + $Names[$i] + ".png")
    [IconSlicer]::Cut($src, $rect, $Tolerance, $Size, $out)
}
$info = "$($src.Width)x$($src.Height)"; $src.Dispose()
"SLICED $([Math]::Min($Names.Count, $Cols * $Rows)) from $info"
