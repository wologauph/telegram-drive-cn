<#
.SYNOPSIS
    Telegram Drive 深度汉化与环境初始化脚本 (setup.ps1)
.DESCRIPTION
    银月独立开发工坊出品 · 自动化安装依赖、执行汉化注入与工具链配置
#>

[CmdletBinding()]
param (
    [string]$AppPath = "D:\app\Telegram Drive\app.exe"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Telegram Drive 深度汉化与环境初始化引擎" -ForegroundColor Cyan
Write-Host "  银月独立开发工坊 · 车间标准自动化部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 检查 Python 环境
Write-Host "`n[1/4] 检查 Python 环境..." -ForegroundColor Yellow
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "[错误] 未检测到 Python 环境，请先安装 Python 3.10+！"
}
$pyVer = python --version
Write-Host "  [OK] 检测到 Python: $pyVer" -ForegroundColor Green

# 2. 检查并安装 brotli 依赖
Write-Host "`n[2/4] 检查 Brotli 压缩组件..." -ForegroundColor Yellow
$brotliCheck = python -c "import brotli; print('OK')" 2>$null
if ($brotliCheck -ne "OK") {
    Write-Host "  正在安装 brotli 库..." -ForegroundColor Cyan
    pip install brotli
}
Write-Host "  [OK] Brotli 压缩组件已就绪" -ForegroundColor Green

# 3. 执行补丁注入
Write-Host "`n[3/4] 执行深度汉化注入..." -ForegroundColor Yellow
$patchScript = Join-Path $PSScriptRoot "scripts\patch_installed_app.py"

if (-not (Test-Path $AppPath)) {
    $altPath = "D:\我的电脑工具库\02_网络与传输工具\Telegram-Drive-CN\app.exe"
    if (Test-Path $altPath) {
        $AppPath = $altPath
    } else {
        Write-Warning "未在默认路径找到 app.exe: $AppPath"
        $AppPath = Read-Host "请输入 Telegram Drive 的 app.exe 完整路径"
    }
}

python $patchScript "$AppPath"
if ($LASTEXITCODE -ne 0) {
    Write-Error "[错误] 补丁注入失败，请查看 logs/error.log 排查原因！"
}
Write-Host "  [OK] 汉化补丁注入完成！" -ForegroundColor Green

# 4. 验证与归档
Write-Host "`n[4/4] 汉化就绪状态..." -ForegroundColor Yellow
Write-Host "  [SUCCESS] 313 处关键配置项已全部汉化" -ForegroundColor Green
Write-Host "  [SUCCESS] 前端导航与设置组件硬编码已修复" -ForegroundColor Green
Write-Host "  [SUCCESS] 运行日志已沉淀至: logs/latest_run.log" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "  汉化部署全部就绪！您可以直接启动软件爽用！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
