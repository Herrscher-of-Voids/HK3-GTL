#requires -Version 5.1
<#
【文件职责】读取本机 DPAPI 生图配置，将临时环境传给 imagegen 技能原有 CLI；不另写 SDK 请求。
【变更记录 #1】2026-10-20 01:24:57（香港时间，中转站图片接入）
删除：无；新增：配置预检、参考图边界、隔离 Python 与技能 CLI 调用及输出脱敏。
修改：不修改技能脚本；密钥只进入子进程环境，既不作为参数，也不写项目或日志。
用途：使用负责人指定中转站和 GPT Image 模型产出候选；成功生成不等于贴图获批。
边界：默认只预检；实际调用必须明确提供 Generate、Edit 或 Batch 模式及输出路径。
【变更记录 #2】2026-10-20 01:28:53（本地独立检查修正）
删除：批次自行切换模型、格式和数量的隐含通道；新增：批次输出边界与 PNG 签名检查。
修改：批次只能沿用所选模型、单项一张 PNG；编辑输入必须是真实 PNG 文件。
用途：保持中转站配置与实际请求一致；不改技能 CLI，不进行付费试图。
【变更记录 #3】2026-10-20 01:44:25（US 中转端点试图）
删除：仅域名直接发送到根路径的错误可能；新增：无路径地址补全已核验的 /v1。
修改：保留带路径配置，根地址仅在子进程内使用 /v1；不修改用户密钥或配置文件。
用途：实际 GET models 已确认 US /v1 返回200且包含所选模型，再使用同一 API 根地址生图。
#>
[CmdletBinding()]
param(
    [ValidateSet('Preflight', 'Generate', 'Edit', 'Batch')][string]$Mode = 'Preflight',
    [string]$PromptFile,
    [string]$Out,
    [string[]]$Image,
    [string]$InputBatch,
    [ValidateSet('low', 'medium', 'high', 'auto')][string]$Quality = 'medium',
    [string]$Size = '1024x1024',
    [switch]$DryRun
)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskLocal = Join-Path $env:LOCALAPPDATA 'HK3GTL'
$taskProfile = Join-Path $taskLocal 'credentials/image-relay.json'
$taskPython = Join-Path $taskLocal 'tools/imagegen-venv/Scripts/python.exe'
$taskSkill = Join-Path $env:USERPROFILE '.codex/skills/.system/imagegen/scripts/image_gen.py'
$taskCA = Join-Path $taskLocal 'tools/windows-ca-bundle.pem'
$taskKeyBytes = $null
$taskKey = $null
$taskProcess = $null

function Quote-ProcessArgument([string]$Value) {
    # Windows 命令行的双引号与末尾反斜线均按子进程解析规则处理。
    $quoted = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
    $quoted = [regex]::Replace($quoted, '(\\+)$', '$1$1')
    return '"' + $quoted + '"'
}

try {
    if (-not (Test-Path -LiteralPath $taskProfile -PathType Leaf)) {
        Write-Output '{"configured":false,"network_request":false}'
        exit 2
    }
    $taskConfig = Get-Content -LiteralPath $taskProfile -Raw -Encoding UTF8 | ConvertFrom-Json
    $taskUri = $null
    if ($taskConfig.schema -ne 1 -or
        -not [Uri]::TryCreate([string]$taskConfig.base_url, [UriKind]::Absolute, [ref]$taskUri) -or
        $taskUri.Scheme -cne 'https' -or $taskUri.UserInfo -or $taskUri.Query -or $taskUri.Fragment -or
        ([string]$taskConfig.base_url).Contains('?') -or ([string]$taskConfig.base_url).Contains('#') -or
        [string]::IsNullOrWhiteSpace($taskUri.Host) -or
        ([string]$taskConfig.model) -cnotmatch '^gpt-image-[A-Za-z0-9][A-Za-z0-9._-]*$') {
        throw '本地配置未通过字段检查。'
    }
    $taskKeyBytes = [System.Security.Cryptography.ProtectedData]::Unprotect(
        [Convert]::FromBase64String($taskConfig.api_key_dpapi_b64), $null,
        [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    $taskKey = [System.Text.Encoding]::UTF8.GetString($taskKeyBytes)
    if ([string]::IsNullOrWhiteSpace($taskKey) -or $taskKey.Contains("`r") -or $taskKey.Contains("`n")) {
        throw '本地密钥为空或格式无效。'
    }
    $taskEffectiveBase = ([string]$taskConfig.base_url).TrimEnd('/')
    if ($taskUri.AbsolutePath -eq '/') { $taskEffectiveBase += '/v1' }
    if ($Mode -eq 'Preflight') {
        [ordered]@{
            configured = $true
            key_decryption_ok = $true
            base_host = $taskUri.Host
            model = $taskConfig.model
            reference_upload_allowed = [bool]$taskConfig.allow_reference_upload
            python_present = (Test-Path -LiteralPath $taskPython -PathType Leaf)
            bundled_cli_present = (Test-Path -LiteralPath $taskSkill -PathType Leaf)
            network_request = $false
        } | ConvertTo-Json -Compress
        exit 0
    }
    if (-not (Test-Path -LiteralPath $taskPython -PathType Leaf) -or
        -not (Test-Path -LiteralPath $taskSkill -PathType Leaf)) {
        throw '隔离 Python 或技能 CLI 不存在。'
    }
    if ([string]::IsNullOrWhiteSpace($Out)) { throw '必须指定候选输出路径。' }
    $taskOut = [System.IO.Path]::GetFullPath($Out)
    $taskOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $taskRoot 'output/imagegen'))
    if (-not $taskOut.StartsWith($taskOutputRoot + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase)) {
        throw '生图输出必须位于当前项目 output/imagegen 内。'
    }
    $taskArguments = @($taskSkill)
    if ($Mode -eq 'Batch') {
        if (-not (Test-Path -LiteralPath $InputBatch -PathType Leaf)) { throw '批次清单不存在。' }
        foreach ($taskJobLine in [System.IO.File]::ReadAllLines((Resolve-Path -LiteralPath $InputBatch).Path)) {
            if ([string]::IsNullOrWhiteSpace($taskJobLine)) { continue }
            $taskJob = $taskJobLine | ConvertFrom-Json
            if (($taskJob.PSObject.Properties['model'] -and $taskJob.model -cne $taskConfig.model) -or
                ($taskJob.PSObject.Properties['output_format'] -and $taskJob.output_format -cne 'png') -or
                ($taskJob.PSObject.Properties['n'] -and $taskJob.n -ne 1)) {
                throw '批次条目不能改变所选模型、PNG 格式或单项一张的数量。'
            }
            if ($taskJob.PSObject.Properties['out']) {
                $taskJobOut = [string]$taskJob.out
                if ([string]::IsNullOrWhiteSpace($taskJobOut) -or
                    [System.IO.Path]::GetFileName($taskJobOut) -cne $taskJobOut -or
                    [System.IO.Path]::GetExtension($taskJobOut) -ine '.png') {
                    throw '批次文件名必须是输出目录内的单个 PNG 文件名。'
                }
            }
        }
        $taskArguments += @('generate-batch', '--input', $InputBatch, '--out-dir', $taskOut,
            '--concurrency', '1', '--max-attempts', '1')
    } else {
        if (-not (Test-Path -LiteralPath $PromptFile -PathType Leaf)) { throw '提示词文件不存在。' }
        $taskArguments += @($Mode.ToLowerInvariant(), '--prompt-file', $PromptFile, '--out', $taskOut)
    }
    if ($Mode -eq 'Edit') {
        if (-not $taskConfig.allow_reference_upload) { throw '尚未允许发送选定的参考 PNG。' }
        if (-not $Image -or $Image.Count -eq 0) { throw '编辑模式缺少参考 PNG。' }
        $taskReferenceRoot = [System.IO.Path]::GetFullPath(
            (Join-Path $taskRoot 'logs/energy-fuel-rework-20261020'))
        foreach ($taskImagePath in $Image) {
            if (-not (Test-Path -LiteralPath $taskImagePath -PathType Leaf)) {
                throw '参考 PNG 文件不存在。'
            }
            $taskResolvedImage = (Resolve-Path -LiteralPath $taskImagePath).Path
            if (-not $taskResolvedImage.StartsWith($taskReferenceRoot + '\',
                [System.StringComparison]::OrdinalIgnoreCase) -or
                [System.IO.Path]::GetExtension($taskResolvedImage) -ine '.png') {
                throw '参考输入仅允许本批已选定来源目录中的 PNG。'
            }
            $taskPNGStream = [System.IO.File]::OpenRead($taskResolvedImage)
            try {
                $taskSignature = New-Object byte[] 8
                $taskRead = $taskPNGStream.Read($taskSignature, 0, 8)
                if ($taskRead -ne 8 -or
                    [BitConverter]::ToString($taskSignature) -cne '89-50-4E-47-0D-0A-1A-0A') {
                    throw '参考文件没有有效 PNG 签名。'
                }
            } finally { $taskPNGStream.Dispose() }
            $taskArguments += @('--image', $taskResolvedImage)
        }
    }
    $taskArguments += @('--model', [string]$taskConfig.model, '--quality', $Quality,
        '--size', $Size, '--output-format', 'png', '--no-augment')
    if ($DryRun) { $taskArguments += '--dry-run' }
    $taskStart = New-Object System.Diagnostics.ProcessStartInfo
    $taskStart.FileName = $taskPython
    $taskStart.Arguments = (($taskArguments | ForEach-Object { Quote-ProcessArgument $_ }) -join ' ')
    $taskStart.WorkingDirectory = $taskRoot
    $taskStart.UseShellExecute = $false
    $taskStart.CreateNoWindow = $true
    $taskStart.RedirectStandardOutput = $true
    $taskStart.RedirectStandardError = $true
    $taskStart.EnvironmentVariables['OPENAI_API_KEY'] = $taskKey
    $taskStart.EnvironmentVariables['OPENAI_BASE_URL'] = $taskEffectiveBase
    $taskStart.EnvironmentVariables['PYTHONIOENCODING'] = 'utf-8'
    $taskStart.EnvironmentVariables['OPENAI_LOG'] = 'error'
    if (Test-Path -LiteralPath $taskCA -PathType Leaf) {
        $taskStart.EnvironmentVariables['SSL_CERT_FILE'] = $taskCA
    }
    $taskProcess = New-Object System.Diagnostics.Process
    $taskProcess.StartInfo = $taskStart
    [void]$taskProcess.Start()
    [void]$taskStart.EnvironmentVariables.Remove('OPENAI_API_KEY')
    $taskStdout = $taskProcess.StandardOutput.ReadToEndAsync()
    $taskStderr = $taskProcess.StandardError.ReadToEndAsync()
    $taskProcess.WaitForExit()
    $taskOutput = $taskStdout.Result + "`n" + $taskStderr.Result
    $taskOutput = $taskOutput.Replace($taskKey, '[密钥已隐藏]')
    $taskOutput = [regex]::Replace($taskOutput, '(?i)Bearer\s+[^\s"'']+', 'Bearer [已隐藏]')
    Write-Output $taskOutput
    exit $taskProcess.ExitCode
} catch {
    # 不回显配置、服务器响应或异常堆栈，避免中转站将鉴权字段写入错误体。
    Write-Output '{"success":false,"detail":"本地配置或调用检查失败；未回显敏感内容。"}'
    exit 1
} finally {
    if ($taskKeyBytes) { [Array]::Clear($taskKeyBytes, 0, $taskKeyBytes.Length) }
    if ($taskProcess) { $taskProcess.Dispose() }
    $taskKey = $null
    $taskKeyBytes = $null
    $taskConfig = $null
}
