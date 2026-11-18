# 变更记录 #1 · 2026-10-15 01:48:00 · 内测5修订157。
# 删除：无；新增：仅采样增强版2.7的进程内存与堆信息；修改：无。
# 用途：每5秒记录工作集/私有提交和系统可用内存，每30秒读取JVM堆，不触发GC、不记录令牌。
param([string]$Label='baseline',[int]$Seconds=300)
$ErrorActionPreference='Stop'
$taskLog=Join-Path (Get-Location).Path 'logs\enhanced27-memory-20261015'
$taskLog=[IO.Path]::GetFullPath($taskLog)
$samplerStop=(Get-Date).AddSeconds($Seconds)
$sampleIndex=0
$targetMarker='GregTech Leisure-增强版 2.7'
$jcmd=Join-Path $env:APPDATA 'PrismLauncher\java\java-runtime-delta\bin\jcmd.exe'
while((Get-Date) -lt $samplerStop){
    $candidates=@(Get-CimInstance Win32_Process -Filter "Name='javaw.exe' OR Name='java.exe'" | Where-Object { $_.CommandLine -like "*$targetMarker*" -and $_.CommandLine -match 'EntryPoint|forgeclient' })
    foreach($candidate in $candidates){
        $gameProcess=Get-Process -Id $candidate.ProcessId -ErrorAction SilentlyContinue
        if($null -eq $gameProcess){continue}
        $os=Get-CimInstance Win32_OperatingSystem
        $sample=[ordered]@{time=(Get-Date).ToString('o');label=$Label;pid=$gameProcess.Id;workingSet=$gameProcess.WorkingSet64;privateBytes=$gameProcess.PrivateMemorySize64;peakWorkingSet=$gameProcess.PeakWorkingSet64;cpu=$gameProcess.CPU;freePhysicalBytes=([long]$os.FreePhysicalMemory*1024)}
        $sample | ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $taskLog "samples-$Label.jsonl") -Encoding UTF8
        if(($sampleIndex % 6) -eq 0){
            (Get-Date).ToString('o') | Add-Content -LiteralPath (Join-Path $taskLog "heap-$Label.log") -Encoding UTF8
            & $jcmd $gameProcess.Id GC.heap_info 2>&1 | Add-Content -LiteralPath (Join-Path $taskLog "heap-$Label.log") -Encoding UTF8
        }
    }
    $sampleIndex++
    Start-Sleep -Seconds 5
}
Write-Output "Sampling completed: $Label"
