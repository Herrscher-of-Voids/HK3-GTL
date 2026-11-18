#requires -Version 5.1
<#
【文件职责】只在本机窗口收集生图中转站地址、明确的模型名与密码框中的密钥，
用当前 Windows 用户的 DPAPI 加密密钥后保存；不发网络请求，不安装依赖，不枚举模型。
【变更记录 #1】2026-10-20 01:21:56（香港时间，本地中转站配置；文件首次实际写入时间）
删除：无；新增：中文配置窗口、HTTPS/模型校验、可选参考 PNG 上传授权与 DPAPI 凭据落盘。
修改：无既有实现；密钥只短暂存在于输入框和加密过程内存，不写明文或输出日志。
用途：让负责人直接在本机填写自有中转站资料，避免在聊天和项目文件中暴露密钥。
边界：保存不代表连接或生图已验证；参考授权仅适用于选定的 GT/GTL 原图 PNG。
#>
[CmdletBinding()]
param()

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

if ([System.Threading.Thread]::CurrentThread.ApartmentState -ne 'STA') {
    throw '此配置窗口需要 STA：请使用 powershell.exe -STA -File 后接此脚本完整路径。'
}
if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
    throw '未找到当前 Windows 用户的 LOCALAPPDATA，配置窗口未启动。'
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Security
[System.Windows.Forms.Application]::EnableVisualStyles()

$credentialDirectory = Join-Path $env:LOCALAPPDATA 'HK3GTL\credentials'
$credentialPath = Join-Path $credentialDirectory 'image-relay.json'
$form = New-Object System.Windows.Forms.Form
$form.Text = 'HK3GTL · 生图中转站本地配置'
$form.ClientSize = New-Object System.Drawing.Size(660, 448)
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Dpi
$form.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 9)

$heading = New-Object System.Windows.Forms.Label
$heading.Text = '在本机填写资料；此窗口只保存加密配置，不连接中转站。'
$heading.Location = New-Object System.Drawing.Point(20, 18)
$heading.Size = New-Object System.Drawing.Size(620, 26)
$form.Controls.Add($heading)

$baseLabel = New-Object System.Windows.Forms.Label
$baseLabel.Text = 'Base URL（中转站提供的 API 根地址，可含路径）'
$baseLabel.Location = New-Object System.Drawing.Point(20, 55)
$baseLabel.Size = New-Object System.Drawing.Size(620, 24)
$form.Controls.Add($baseLabel)

$baseBox = New-Object System.Windows.Forms.TextBox
$baseBox.Location = New-Object System.Drawing.Point(20, 82)
$baseBox.Size = New-Object System.Drawing.Size(620, 26)
$baseBox.TabIndex = 0
$form.Controls.Add($baseBox)

$modelLabel = New-Object System.Windows.Forms.Label
$modelLabel.Text = 'GPT Image 模型名（必须由中转站确认，以 gpt-image- 开头）'
$modelLabel.Location = New-Object System.Drawing.Point(20, 119)
$modelLabel.Size = New-Object System.Drawing.Size(620, 24)
$form.Controls.Add($modelLabel)

$modelBox = New-Object System.Windows.Forms.TextBox
$modelBox.Location = New-Object System.Drawing.Point(20, 146)
$modelBox.Size = New-Object System.Drawing.Size(620, 26)
$modelBox.TabIndex = 1
$form.Controls.Add($modelBox)

$keyLabel = New-Object System.Windows.Forms.Label
$keyLabel.Text = 'API key（密码框；仅以当前 Windows 用户 DPAPI 密文保存）'
$keyLabel.Location = New-Object System.Drawing.Point(20, 183)
$keyLabel.Size = New-Object System.Drawing.Size(620, 24)
$form.Controls.Add($keyLabel)

$keyBox = New-Object System.Windows.Forms.TextBox
$keyBox.Location = New-Object System.Drawing.Point(20, 210)
$keyBox.Size = New-Object System.Drawing.Size(620, 26)
$keyBox.UseSystemPasswordChar = $true
$keyBox.ShortcutsEnabled = $true
$keyBox.TabIndex = 2
$form.Controls.Add($keyBox)

$referenceCheck = New-Object System.Windows.Forms.CheckBox
$referenceCheck.Text = '允许将本次选定的 GT/GTL 原图 PNG 发送到该中转站，作为参考编辑输入'
$referenceCheck.Location = New-Object System.Drawing.Point(20, 251)
$referenceCheck.Size = New-Object System.Drawing.Size(620, 44)
$referenceCheck.Checked = $false
$referenceCheck.TabIndex = 3
$form.Controls.Add($referenceCheck)

$referenceNote = New-Object System.Windows.Forms.Label
$referenceNote.Text = '仅授权这些选定 PNG；不包含存档、文档、整个模组包或其他文件。未勾选时禁止参考图上传。'
$referenceNote.Location = New-Object System.Drawing.Point(20, 299)
$referenceNote.Size = New-Object System.Drawing.Size(620, 40)
$form.Controls.Add($referenceNote)

$storageNote = New-Object System.Windows.Forms.Label
$storageNote.Text = '配置保存在 LOCALAPPDATA\HK3GTL\credentials\image-relay.json。取消不写入文件；更新已有配置时请重新填写密钥。'
$storageNote.Location = New-Object System.Drawing.Point(20, 345)
$storageNote.Size = New-Object System.Drawing.Size(620, 40)
$form.Controls.Add($storageNote)

$saveButton = New-Object System.Windows.Forms.Button
$saveButton.Text = '保存加密配置'
$saveButton.Location = New-Object System.Drawing.Point(390, 398)
$saveButton.Size = New-Object System.Drawing.Size(136, 32)
$saveButton.TabIndex = 4
$form.Controls.Add($saveButton)

$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Text = '取消'
$cancelButton.Location = New-Object System.Drawing.Point(540, 398)
$cancelButton.Size = New-Object System.Drawing.Size(100, 32)
$cancelButton.TabIndex = 5
$cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.Controls.Add($cancelButton)
$form.CancelButton = $cancelButton
$form.AcceptButton = $saveButton

# 只恢复非秘密字段；不在窗口中解密或回显旧密钥，也不输出读入的原始配置。
if (Test-Path -LiteralPath $credentialPath -PathType Leaf) {
    try {
        $existingConfiguration = Get-Content -LiteralPath $credentialPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($existingConfiguration.schema -eq 1) {
            $baseBox.Text = [string]$existingConfiguration.base_url
            $modelBox.Text = [string]$existingConfiguration.model
            $referenceCheck.Checked = [bool]$existingConfiguration.allow_reference_upload
        }
    } catch {
        # 旧配置无效时保留空白输入；只在用户点击保存后才可能替换。
    } finally {
        $existingConfiguration = $null
    }
}

$saveButton.Add_Click({
    $relayUri = $null
    $baseValue = $baseBox.Text.Trim()
    $modelValue = $modelBox.Text.Trim()
    $keyBytes = $null
    $encryptedBytes = $null
    $temporaryPath = $null
    if (-not [Uri]::TryCreate($baseValue, [UriKind]::Absolute, [ref]$relayUri) -or
        $relayUri.Scheme -cne 'https' -or [string]::IsNullOrWhiteSpace($relayUri.Host) -or
        -not [string]::IsNullOrEmpty($relayUri.UserInfo) -or
        -not [string]::IsNullOrEmpty($relayUri.Query) -or
        -not [string]::IsNullOrEmpty($relayUri.Fragment) -or
        $baseValue.Contains('?') -or $baseValue.Contains('#')) {
        [void][System.Windows.Forms.MessageBox]::Show($form,
            '请输入有效的 HTTPS API 根地址；地址不能包含用户名、密码、查询参数或片段。',
            '地址尚未通过检查', [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning)
        $baseBox.Focus()
        return
    }
    if ($modelValue -cnotmatch '^gpt-image-[A-Za-z0-9][A-Za-z0-9._-]*$') {
        [void][System.Windows.Forms.MessageBox]::Show($form,
            '请填写中转站明确提供的 GPT Image 模型名，必须以 gpt-image- 开头。',
            '模型名尚未通过检查', [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning)
        $modelBox.Focus()
        return
    }
    if ([string]::IsNullOrWhiteSpace($keyBox.Text) -or $keyBox.Text.Contains("`r") -or
        $keyBox.Text.Contains("`n")) {
        [void][System.Windows.Forms.MessageBox]::Show($form,
            '请在密码框中填写非空、单行的 API key。更新已有配置也需要重新填写。',
            '密钥尚未通过检查', [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning)
        $keyBox.Focus()
        return
    }
    try {
        $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($keyBox.Text)
        $encryptedBytes = [System.Security.Cryptography.ProtectedData]::Protect(
            $keyBytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
        $createdAt = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
        $configuration = [ordered]@{
            schema = 1
            base_url = $relayUri.GetLeftPart([UriPartial]::Path).TrimEnd('/')
            model = $modelValue
            api_key_dpapi_b64 = [Convert]::ToBase64String($encryptedBytes)
            created_at = $createdAt
            allow_reference_upload = [bool]$referenceCheck.Checked
        }
        $encryptedJson = $configuration | ConvertTo-Json -Depth 3
        [void][System.IO.Directory]::CreateDirectory($credentialDirectory)
        $temporaryPath = Join-Path $credentialDirectory ('image-relay.' + [Guid]::NewGuid().ToString('N') + '.tmp')
        [System.IO.File]::WriteAllText($temporaryPath, $encryptedJson, (New-Object System.Text.UTF8Encoding($false)))
        if ([System.IO.File]::Exists($credentialPath)) {
            [System.IO.File]::Replace($temporaryPath, $credentialPath, $null)
        } else {
            [System.IO.File]::Move($temporaryPath, $credentialPath)
        }
        $temporaryPath = $null
        $keyBox.Clear()
        [void][System.Windows.Forms.MessageBox]::Show($form, '配置已保存。', '本地配置',
            [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        $form.Close()
    } catch {
        [void][System.Windows.Forms.MessageBox]::Show($form,
            '未能保存加密配置。请确认当前 Windows 用户可使用 DPAPI，且本地凭据目录可写。',
            '配置未保存', [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error)
    } finally {
        if ($null -ne $keyBytes) { [Array]::Clear($keyBytes, 0, $keyBytes.Length) }
        if ($null -ne $encryptedBytes) { [Array]::Clear($encryptedBytes, 0, $encryptedBytes.Length) }
        $keyBytes = $null
        $encryptedBytes = $null
        $configuration = $null
        $encryptedJson = $null
        if ($temporaryPath -and [System.IO.File]::Exists($temporaryPath)) {
            try { [System.IO.File]::Delete($temporaryPath) } catch { }
        }
    }
})

$form.Add_FormClosed({ $keyBox.Clear() })
try {
    [void][System.Windows.Forms.Application]::Run($form)
} finally {
    $keyBox.Clear()
    $form.Dispose()
}
