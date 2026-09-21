@echo off
chcp 65001 >nul
title Telegram Drive (汉化版)

set "APP_DIR=D:\app\Telegram Drive"
if exist "%APP_DIR%\app.exe" (
    start "" "%APP_DIR%\app.exe"
    exit /b 0
)

set "TOOL_DIR=D:\我的电脑工具库\02_网络与传输工具\Telegram-Drive-CN"
if exist "%TOOL_DIR%\app.exe" (
    start "" "%TOOL_DIR%\app.exe"
    exit /b 0
)

echo [错误] 未找到已安装的 Telegram Drive 主程序！
pause
