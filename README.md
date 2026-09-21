# Telegram Drive (简体中文深度汉化与体验增强版)

> **银月独立开发工坊 · 车间出品**  
> 基于开源项目 [caamer20/Telegram-Drive](https://github.com/caamer20/Telegram-Drive) (v3.9.0) 进行全链路深度本土化汉化与稳定性增强。

---

## 🌟 核心改进与特性

### 1. 100% 深度全景简体中文
- **彻底消除英文残留**：补齐官方遗留的 **313 处未翻译英文词条**（官方原版在 `copied-english-baseline.json` 中保留了 283 个未翻译基线，包括整套目录同步、外观主题、隐私设置、缓存管理等）。
- **解除前端硬编码**：重构并替换了 `SettingsModal.tsx` 等前端组件中硬编码的分类标题（`Essentials`、`Security & Privacy`、`Connections`、`Advanced`、`Support`）及搜索框占位符。
- **地道中文术语**：遵循现代操作系统与主流网盘使用习惯，摒弃生硬的机器直译，全面本土化校对。

### 2. Windows 平台底层启动崩溃修复 (Bugfix)
- **踩坑突破**：排查并锁定了官方依赖库 `locate-locale-0.2.0` 在 Windows 环境下因写死 10-u16 缓冲区、导致类似 `zh-Hans-HK`（11字符）系统区域设置下发生 `ERROR_INSUFFICIENT_BUFFER` 进而引发 Rust `usize::MAX` 整数下溢崩溃的严重隐患。
- **环境自愈**：提供自动化环境自愈检测，确保程序在任意 Windows 机器上均能极速平稳启动。

### 3. 双轨制交付体系
- **实锤热修注入引擎** (`scripts/patch_installed_app.py`)：
  - 基于 PE 二进制结构分析与 Brotli 高阶压缩切片替换算法。
  - 支持对官方已安装的 `app.exe` 进行无损热修注入，自动创建 `.bak` 备份，毫秒级生效，无需耗费数十小时配置复杂 Rust 编译工具链。
- **源码级工程固化**：
  - 完整规范的 React + TypeScript + Vite + Tauri 源码结构。
  - 符合工坊《车间宪法》的三轨持久化日志体系。

---

## 🚀 极速上手

### 方案 A：一键为本地已安装程序注入汉化（推荐）

如果您电脑上已经安装了官方版 Telegram Drive：

```powershell
# 在本项目根目录下运行：
.\setup.ps1
```

脚本将自动检测您的 Python 环境与已安装的 `app.exe`，创建备份并注入 100% 汉化切片。完成后即可直接启动软件！

### 方案 B：直接运行

```bat
# 双击运行：
run.bat
```

---

## 📁 目录架构

```text
telegram-drive-cn/
├── app/                  # Tauri + React 前端与核心源码
│   ├── src/i18n/         # 国际化语言包（已达 100% 简体中文覆盖率）
│   └── src-tauri/        # Rust 后端与系统集成
├── config/               # 配置文件范例
├── logs/                 # 工业级三轨标准化日志体系
│   ├── latest_run.log    # 单次运行流水账
│   ├── app_YYYY-MM.log   # 历史滚动归档
│   └── error.log         # 崩溃黑匣子
├── scripts/              # 自动化工具链
│   └── patch_installed_app.py # 二进制无损切片热修引擎
├── setup.ps1             # 一键环境检查与汉化安装脚本
├── run.bat               # 极简启动入口
└── README.md             # 本说明文档
```

---

## 🛠️ 常见问题与避坑指南 (FAQ)

### Q1: 启动出现闪退怎么解决？
A: 请检查 Windows 系统区域格式是否包含长后缀（如 `zh-Hans-HK`）。在 PowerShell 中以管理员身份执行 `Set-Culture zh-CN` 即可彻底根治。

### Q2: 出现网络连接超时或无法登录？
A: 
1. 如果已开启全局科学上网（Clash Verge / Mihomo 的 TUN 虚拟网卡模式），请在软件设置中将 **VPN 模式** 保持开启。
2. 也可在设置中的“网络代理”手动填入本机 SOCKS5 代理（如 `127.0.0.1:2080`），点击“测试连接”验证延迟。

### Q3: 还原官方原版英文界面？
A: 补丁引擎在首次注入时已自动生成 `app.exe.bak` 原始备份。只需将 `app.exe.bak` 重命名覆盖回 `app.exe` 即可瞬间无损还原。

---

## 📜 开源协议

本项目遵循原项目的开源许可证 [GPL-3.0 License](LICENSE)。  
感谢原作者 [caamer20](https://github.com/caamer20) 及开源社区贡献者。
