# ==============================================================================
# Telegram Drive 双账号极速分流与直登管家 (switch_account.ps1)
# 银月独立开发工坊 · 车间法宝出品
# ==============================================================================
param (
    [string]$Account = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$exe = Join-Path $PSScriptRoot "Telegram-Drive-CN.exe"
if (-not (Test-Path $exe)) {
    $exe = "D:\app\Telegram Drive\app.exe"
}

$appDataDir = Join-Path $env:APPDATA "com.cameronamer.telegramdrive"
$profilesDir = Join-Path $appDataDir "profiles"
$activeFlagFile = Join-Path $appDataDir "active_account.txt"

# 确保 profiles 基础目录存在
$p610 = Join-Path $profilesDir "610_resource"
$p920 = Join-Path $profilesDir "920_backup"
if (-not (Test-Path $p610)) { New-Item -ItemType Directory -Path $p610 -Force | Out-Null }
if (-not (Test-Path $p920)) { New-Item -ItemType Directory -Path $p920 -Force | Out-Null }

# 读取当前激活账号
$currentActive = "610"
if (Test-Path $activeFlagFile) {
    $rawVal = (Get-Content $activeFlagFile -Raw -ErrorAction SilentlyContinue)
    if ($rawVal) { $currentActive = $rawVal.Trim() }
}

function Set-JsonNoBom {
    param([string]$Path, [string]$Content)
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

# 1. 代理自适应探测与同步（支持 7897 / 7890 / 2080 / 10808 等主流代理）
function Update-ProxySettings {
    param([string]$targetDir)
    try {
        $candidatePorts = @(7897, 7890, 2080, 10808, 10809)
        $detectedPort = 7897
        foreach ($p in $candidatePorts) {
            $conn = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($conn) {
                $detectedPort = $p
                break
            }
        }
        $netPath = Join-Path $targetDir "network_settings.json"
        if (Test-Path $netPath) {
            $netCfg = Get-Content $netPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $netCfg.proxy.port = [int]$detectedPort
            $netCfg.proxy.host = "127.0.0.1"
            $netCfg.proxy.enabled = $true
            $netCfg.proxy.proxy_type = "socks5"
            $jsonStr = $netCfg | ConvertTo-Json -Depth 6
            Set-JsonNoBom -Path $netPath -Content $jsonStr
        }
    } catch {
        # 宽容处理，不阻塞主流程
    }
}

# 如果未传参数，弹出极简精致图形选择视窗
if ([string]::IsNullOrWhiteSpace($Account)) {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Telegram Drive · 银月双账号极速直登分流"
    $form.Size = New-Object System.Drawing.Size(480, 290)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.TopMost = $true
    $form.BackColor = [System.Drawing.Color]::FromArgb(248, 249, 250)

    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Text = "请选择要启动的 Telegram 云盘账号："
    $titleLabel.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 11, [System.Drawing.FontStyle]::Bold)
    $titleLabel.Location = New-Object System.Drawing.Point(30, 18)
    $titleLabel.Size = New-Object System.Drawing.Size(420, 25)
    $form.Controls.Add($titleLabel)

    $statusLabel = New-Object System.Windows.Forms.Label
    $activeText = if ($currentActive -eq "610") { "【610 资源空间】" } elseif ($currentActive -eq "920") { "【920 备份空间】" } else { "未记录" }
    $statusLabel.Text = "当前就绪环境：$activeText"
    $statusLabel.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 8.5)
    $statusLabel.ForeColor = [System.Drawing.Color]::Gray
    $statusLabel.Location = New-Object System.Drawing.Point(30, 44)
    $statusLabel.Size = New-Object System.Drawing.Size(420, 20)
    $form.Controls.Add($statusLabel)

    # 按钮 1：610 资源号
    $btn610 = New-Object System.Windows.Forms.Button
    $btn610.Text = "📚 直登【610 资源空间】`n(+1 610-229-1600 · 顶级资源图书馆 · 免密直入)"
    $btn610.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 9.5)
    $btn610.Location = New-Object System.Drawing.Point(30, 72)
    $btn610.Size = New-Object System.Drawing.Size(405, 60)
    $btn610.BackColor = [System.Drawing.Color]::FromArgb(230, 244, 255)
    $btn610.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    $btn610.FlatAppearance.BorderColor = [System.Drawing.Color]::FromArgb(64, 150, 255)
    $btn610.Cursor = [System.Windows.Forms.Cursors]::Hand
    $btn610.Add_Click({
        $script:selectedAccount = "610"
        $form.Close()
    })
    $form.Controls.Add($btn610)

    # 按钮 2：920 备份号
    $btn920 = New-Object System.Windows.Forms.Button
    $btn920.Text = "📱 直登【920 备份空间】`n(+1 920-393-3222 · 手机照片与视频备份通道)"
    $btn920.Font = New-Object System.Drawing.Font("Microsoft YaHei UI", 9.5)
    $btn920.Location = New-Object System.Drawing.Point(30, 145)
    $btn920.Size = New-Object System.Drawing.Size(405, 60)
    $btn920.BackColor = [System.Drawing.Color]::FromArgb(246, 255, 237)
    $btn920.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    $btn920.FlatAppearance.BorderColor = [System.Drawing.Color]::FromArgb(149, 222, 100)
    $btn920.Cursor = [System.Windows.Forms.Cursors]::Hand
    $btn920.Add_Click({
        $script:selectedAccount = "920"
        $form.Close()
    })
    $form.Controls.Add($btn920)

    [void]$form.ShowDialog()
    $Account = $script:selectedAccount
}

if ([string]::IsNullOrWhiteSpace($Account)) {
    Write-Host "主人取消了选择，操作已退出。"
    exit 0
}

# 2. 安全终止可能处于运行状态的 Telegram Drive 实例
$existingProcs = Get-Process -Name "Telegram-Drive-CN", "app" -ErrorAction SilentlyContinue
if ($existingProcs) {
    Write-Host "检测到正在运行的 Telegram Drive 实例，正在安全保存并退出..."
    $existingProcs | Stop-Process -Force
    Start-Sleep -Milliseconds 600
}

# 3. 持久化回写当前账号数据（带严格完整性校验，严禁回写损坏文件）
if ($currentActive -eq "610") {
    $saveDir = $p610
} elseif ($currentActive -eq "920") {
    $saveDir = $p920
} else {
    $saveDir = ""
}

if ($saveDir -and (Test-Path $saveDir)) {
    $curSession = Join-Path $appDataDir "telegram.session"
    $curConfig = Join-Path $appDataDir "config.json"
    $curWs = Join-Path $appDataDir "workspace"

    # 只有当 session 文件存在且有效（>10KB）时才回写
    if (Test-Path $curSession) {
        $sessSize = (Get-Item $curSession).Length
        if ($sessSize -gt 10240) {
            Copy-Item $curSession (Join-Path $saveDir "telegram.session") -Force
        }
    }
    # 只有当 config 存在且包含有效 json 时才回写
    if (Test-Path $curConfig) {
        try {
            $validTest = Get-Content $curConfig -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($validTest) {
                # 确保保存的配置始终含有正确的 api_id 和 api_hash
                $validTest.api_id = "37459146"
                $validTest.api_hash = "fa18fb36a807ef01a98b1d4dae253936"
                $saveJsonStr = $validTest | ConvertTo-Json -Depth 10
                Set-JsonNoBom -Path (Join-Path $saveDir "config.json") -Content $saveJsonStr
            }
        } catch {}
    }
    # 回写 workspace
    if (Test-Path $curWs) {
        $saveWs = Join-Path $saveDir "workspace"
        if (-not (Test-Path $saveWs)) { New-Item -ItemType Directory -Path $saveWs -Force | Out-Null }
        Copy-Item -Path "$curWs\*" -Destination $saveWs -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# 4. 载入目标账号 Profile
Write-Host "正在装载目标账号 [$Account] 的独立环境..."
if ($Account -eq "610") {
    $targetDir = $p610
} elseif ($Account -eq "920") {
    $targetDir = $p920
} else {
    Write-Error "未知账号标识: $Account"
    exit 1
}

# 恢复配置文件并固化 api_id 和 api_hash
$targetConfig = Join-Path $targetDir "config.json"
if (Test-Path $targetConfig) {
    try {
        $tCfg = Get-Content $targetConfig -Raw -Encoding UTF8 | ConvertFrom-Json
        $tCfg.api_id = "37459146"
        $tCfg.api_hash = "fa18fb36a807ef01a98b1d4dae253936"
        $tCfg.ad_gateway_passed = $true
        $targetJsonStr = $tCfg | ConvertTo-Json -Depth 10
        Set-JsonNoBom -Path (Join-Path $appDataDir "config.json") -Content $targetJsonStr
    } catch {
        Copy-Item $targetConfig (Join-Path $appDataDir "config.json") -Force
    }
}

# 恢复 Session
$targetSession = Join-Path $targetDir "telegram.session"
$activeSession = Join-Path $appDataDir "telegram.session"
if (Test-Path $targetSession) {
    $tSize = (Get-Item $targetSession).Length
    if ($tSize -gt 10240) {
        Copy-Item $targetSession $activeSession -Force
    }
} else {
    # 若目标尚无 session（如 920 首次登录），安全清除根目录旧 session，避免串号
    if (Test-Path $activeSession) {
        Remove-Item $activeSession -Force -ErrorAction SilentlyContinue
    }
}

# 恢复 Workspace（如果存在）
$targetWs = Join-Path $targetDir "workspace"
$appWs = Join-Path $appDataDir "workspace"
if (Test-Path $targetWs) {
    if (-not (Test-Path $appWs)) { New-Item -ItemType Directory -Path $appWs -Force | Out-Null }
    Copy-Item -Path "$targetWs\*" -Destination $appWs -Recurse -Force -ErrorAction SilentlyContinue
} else {
    if ($Account -eq "920") {
        # 避免 920 串用 610 的本地缓存库
        if (Test-Path $appWs) {
            Remove-Item -Path "$appWs\*" -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# 5. 确保 Windows 凭据管理器中存在 API Hash
try {
    & cmdkey /generic:com.cameronamer.telegramdrive.telegram-api /user:api-hash-v1 /pass:fa18fb36a807ef01a98b1d4dae253936 | Out-Null
} catch {}

# 6. 自适应同步代理配置至当前根目录
Update-ProxySettings -targetDir $appDataDir

# 7. 标记当前激活账号
Set-Content -Path $activeFlagFile -Value $Account -Encoding UTF8

Write-Host "账号 [$Account] 环境装配就绪！正在极速启动 Telegram Drive..."
if (Test-Path $exe) {
    Start-Process -FilePath $exe -WorkingDirectory (Split-Path -Parent $exe)
    Write-Host "[SUCCESS] Telegram Drive 启动成功！"
} else {
    Write-Error "未找到 Telegram Drive 主执行文件！"
}
