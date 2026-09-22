#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 深度汉化全景补丁注入引擎 (Patch Engine v3.0 · 全链路彻底汉化)
银月独立开发工坊 · 工业级三轨日志与无损切片热修复
覆盖全应用六大核心资产切片：
  1. zh-CN.json: 全量 1,110 个键位纯正简体中文本地化
  2. SettingsModal: 设置视窗全景（分类、安全隐私、网络同步、密钥恢复）
  3. HelpCenterDialog: 帮助中心与常见问题深度汉化
  4. index: 启动开机自检、Telegram 官方会话握手进度与默认语言
  5. DesktopDashboard: 主面板空状态提示、广告倒计时赞助提示、本周流量、以及收藏夹动态映射
  6. zh-TW.json: 繁体补齐（防止切换后遗漏英文）
"""

import os
import sys
import json
import struct
import shutil
import datetime
import traceback

try:
    import brotli
except ImportError:
    print("[ERROR] brotli module not found! Please run: pip install brotli")
    sys.exit(1)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

NOW = datetime.datetime.now()
MONTH_STR = NOW.strftime("%Y-%m")
LATEST_LOG = os.path.join(LOGS_DIR, "latest_run.log")
MONTH_LOG = os.path.join(LOGS_DIR, f"app_{MONTH_STR}.log")
ERROR_LOG = os.path.join(LOGS_DIR, "error.log")

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)
    with open(LATEST_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    with open(MONTH_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    if level == "ERROR":
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

def purge_webview_cache():
    try:
        cache_dirs = [
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\Code Cache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\DawnGraphiteCache"),
            os.path.expandvars(r"%LOCALAPPDATA%\com.cameronamer.telegramdrive\EBWebView\Default\GPUCache"),
        ]
        for c in cache_dirs:
            if os.path.exists(c):
                shutil.rmtree(c, ignore_errors=True)
                log(f"Purged stale WebView2 cache: {c}", "CLEAN")
    except Exception as e:
        log(f"Notice while purging cache: {e}", "WARNING")

def align_user_language_to_zh_cn():
    """将用户的 settings.json 语言设为 zh-CN，确保无缝进入全汉化环境"""
    settings_file = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive\settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "settings" in data and data["settings"].get("language") != "zh-CN":
                data["settings"]["language"] = "zh-CN"
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                log("Aligned user language to 'zh-CN' in settings.json", "SUCCESS")
        except Exception as e:
            log(f"Failed to align settings.json language: {e}", "WARNING")

def run_patch(target_app_path=None):
    with open(LATEST_LOG, "w", encoding="utf-8") as f:
        f.write(f"=== Telegram Drive Patch Engine v3.0 Run: {NOW.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    if not target_app_path:
        default_paths = [
            r"D:\app\Telegram Drive\app.exe",
            r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\app.exe",
            r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe",
        ]
        for p in default_paths:
            if os.path.exists(p):
                target_app_path = p
                break

    if not target_app_path or not os.path.exists(target_app_path):
        log(f"Target executable not found at: {target_app_path}", "ERROR")
        return False

    log(f"Target binary identified: {target_app_path}", "INFO")
    backup_path = target_app_path + ".bak"

    try:
        # 1. 备份源文件
        if not os.path.exists(backup_path):
            shutil.copyfile(target_app_path, backup_path)
            log(f"Created pristine backup: {backup_path}", "CLEAN")
        else:
            log(f"Existing backup confirmed: {backup_path}", "INFO")

        # 2. 读取二进制数据
        with open(target_app_path, "rb") as f:
            data = bytearray(f.read())
        log(f"Loaded binary into memory: {len(data)} bytes", "INFO")

        source_data = data
        if os.path.exists(backup_path):
            with open(backup_path, "rb") as f:
                source_data = f.read()
            log("Loaded pristine backup for original asset extraction", "INFO")

        # ----------------------------------------------------
        # 3. Patch Slice 1: zh-CN.json
        # ----------------------------------------------------
        zh_json_path = os.path.join(PROJECT_ROOT, "app", "src", "i18n", "locales", "zh-CN.json")
        with open(zh_json_path, "r", encoding="utf-8") as f:
            zh_content = json.load(f)
        raw_zh = json.dumps(zh_content, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        comp_zh = brotli.compress(raw_zh, quality=11)
        log(f"[1/6] Compressed zh-CN: {len(raw_zh)} raw -> {len(comp_zh)} brotli bytes (slot: 16133)", "INFO")

        zh_marker = b'/assets/zh-CN-CSiX_qds.json'
        zh_pos = data.find(zh_marker)
        if zh_pos == -1:
            raise RuntimeError("zh-CN asset marker not found in binary!")
        zh_start = zh_pos + len(zh_marker)
        orig_zh_len = 16133
        if len(comp_zh) > orig_zh_len:
            raise ValueError(f"Compressed zh-CN ({len(comp_zh)}) exceeds allocated slot ({orig_zh_len})!")

        data[zh_start:zh_start + len(comp_zh)] = comp_zh
        data[zh_start + len(comp_zh):zh_start + orig_zh_len] = b'\x00' * (orig_zh_len - len(comp_zh))

        ZH_TABLE_ENTRY = 38446664
        data[ZH_TABLE_ENTRY:ZH_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_zh))
        log(f"[1/6] zh-CN table entry updated at {ZH_TABLE_ENTRY}: len={len(comp_zh)}", "INFO")

        # ----------------------------------------------------
        # 4. Patch Slice 2: SettingsModal-B1qI0t1k.js
        # ----------------------------------------------------
        modal_marker = b'assets/SettingsModal-B1qI0t1k.js'
        modal_pos = data.find(modal_marker)
        if modal_pos == -1:
            raise RuntimeError("SettingsModal asset marker not found in binary!")
        modal_start = modal_pos + len(modal_marker)
        orig_modal_len = 29303

        raw_modal_js = brotli.decompress(bytes(source_data[modal_start:modal_start + orig_modal_len])).decode('utf-8')

        modal_replacements = [
            ('placeholder:"Search settings"', 'placeholder:"搜索设置..."'),
            ('[["Essentials",', '[["基础设置",'),
            ('["Security & Privacy",', '["安全与隐私",'),
            ('["Connections",', '["连接与同步",'),
            ('["Advanced",', '["高级网络",'),
            ('["Support",', '["关于与支持",'),
            ('_==="privacy"?"Privacy":_==="advanced"?"Advanced":t(`settings.tab_${_}`)', '_==="privacy"?"隐私遥测":_==="advanced"?"高级集成":t(`settings.tab_${_}`)'),
            ('j==="privacy"?"Privacy, crash reporting & supporter license":j==="advanced"?"Advanced connections and integrations":t(`settings.tab_${j}`)', 'j==="privacy"?"隐私保护、崩溃报告与支持者选项":j==="advanced"?"高级网络连接与系统集成":t(`settings.tab_${j}`)'),
            ('"How REST access works"', '"REST API 访问机制说明"'),
            ('"How WebDAV access works"', '"WebDAV 本地挂载机制说明"'),
            ('"Close local access explanation"', '"关闭说明"'),
            ('"Test Connection"', '"测试网络连接"'),
            ('"Live Connection Monitoring"', '"网络连接实时监控"'),
            ('"SOCKS5 and HTTP bridge settings"', '"SOCKS5 代理及 HTTP 桥接配置"'),
            ('"Send anonymous crash reports"', '"发送匿名崩溃报告协助改进"'),
            ('"Crash-only reporting"', '"仅崩溃异常时上报"'),
            ('"Pay with PayPal"', '"通过 PayPal 赞助"'),
            ('"Restore purchase"', '"恢复赞助状态"'),
            ('"Ad-free for life"', '"永久免除赞助提示"'),
            ('"Free forever"', '"永久免费开源"'),
            ('"Sponsor placements removed"', '"已去除全部赞助展示"'),
            ('"Create recovery bundle"', '"创建恢复密钥包"'),
            ('"No encrypted settings backup was found in the latest 1,000 Saved Messages."', '"在最近 1000 条收藏夹消息中未找到加密设置备份。"'),
            ('"Encrypted settings uploaded to Telegram Saved Messages."', '"加密设置已成功上传至 Telegram 我的云盘 (收藏夹)。"'),
            ('"REST API, WebDAV, proxy, VPN, and network tuning"', '"REST API、WebDAV、代理、VPN 及网络高级调优"'),
            ('"Retries, bandwidth, and data-center tuning"', '"重试机制、带宽限制与 Telegram 数据中心调优"'),
            ('"Free and supporter license comparison"', '"免费版与赞助者授权对比"'),
            ('"One payment. No subscription. No sponsor ads."', '"一次性赞助，无订阅制，永久免除赞助广告。"'),
            ('"Finder and file-manager access"', '"文件资源管理器及 WebDAV 本地访问"'),
            ('"Folder channels and uploaded file messages go directly to your Telegram account."', '"文件夹频道和上传的文件消息直接存入您的 Telegram 官方账户。"'),
            ('"Settings, queue state, thumbnails, and encrypted vault material stay local."', '"软件设置、传输队列、缩略图和端到端加密密钥均保存在本地。"'),
            ('"Where your data goes"', '"您的数据流向说明"'),
            ('"Private and predictable:"', '"隐私与可预测性："'),
            ('"Protected-file limitation:"', '"加密保护文件限制："'),
            ('"Understand REST permissions"', '"了解 REST 权限范围"'),
            ('"Understand WebDAV permissions"', '"了解 WebDAV 权限范围"'),
            ('"Use WebDAV, not SMB."', '"请使用 WebDAV 协议挂载，不支持 SMB。"'),
            ('"Save this recovery code now"', '"请立即妥善保存此恢复代码"'),
            ('"Recovery drill passed. Your vault setup is complete."', '"恢复演练通过！您的端到端加密金库配置完成。"'),
            ('"Periodically check connectivity and display latency"', '"定时检测网络连通性并显示延迟"'),
            ('"No supporter license is active"', '"未激活赞助者授权"'),
            ('"Lifetime Ad-Free Supporter License"', '"终身免赞助广告支持者授权"'),
            ('"Apply settings from Telegram?"', '"是否应用来自 Telegram 的云端设置？"'),
            ('"Enable encrypted settings sync"', '"启用加密设置云同步"'),
            ('"Encrypted settings sync"', '"加密设置云同步"'),
            ('"Sync passphrase"', '"同步口令密码"'),
            ('"Refresh settings sync status"', '"刷新设置同步状态"'),
            ('"Download and apply"', '"下载并应用云端设置"'),
            ('"Replace the settings backup?"', '"是否覆盖云端已有设置备份？"'),
            ('"VPN & network"', '"VPN 与网络"'),
            ('"Checkout opened"', '"已在浏览器中打开结账页面"'),
            ('"Checkout opens securely in your browser."', '"结账页面将在系统默认浏览器中安全打开。"'),
            ('"Keep Telegram Drive open while payment is verified."', '"支付验证期间请保持 Telegram Drive 运行。"'),
            ('"Payment verified. Ad-free supporter access is active."', '"赞助验证成功！已为您永久去除赞助提示。"'),
        ]

        modified_modal_js = raw_modal_js
        for old, new in modal_replacements:
            if old in modified_modal_js:
                modified_modal_js = modified_modal_js.replace(old, new)

        comp_modal = brotli.compress(modified_modal_js.encode('utf-8'), quality=11)
        log(f"[2/6] Compressed SettingsModal: {len(modified_modal_js)} raw -> {len(comp_modal)} brotli bytes (slot: {orig_modal_len})", "INFO")
        if len(comp_modal) > orig_modal_len:
            raise ValueError(f"Compressed SettingsModal ({len(comp_modal)}) exceeds allocated slot ({orig_modal_len})!")

        data[modal_start:modal_start + len(comp_modal)] = comp_modal
        data[modal_start + len(comp_modal):modal_start + orig_modal_len] = b'\x00' * (orig_modal_len - len(comp_modal))

        MODAL_TABLE_ENTRY = 38445864
        data[MODAL_TABLE_ENTRY:MODAL_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_modal))
        log(f"[2/6] SettingsModal table entry updated at {MODAL_TABLE_ENTRY}: len={len(comp_modal)}", "INFO")

        # ----------------------------------------------------
        # 5. Patch Slice 3: HelpCenterDialog-C3f8Qzc5.js (帮助中心 Q&A)
        # ----------------------------------------------------
        help_marker = b'assets/HelpCenterDialog-C3f8Qzc5.js'
        help_pos = data.find(help_marker)
        if help_pos == -1:
            raise RuntimeError("HelpCenterDialog asset marker not found in binary!")
        help_start = help_pos + len(help_marker)
        orig_help_len = 1276

        raw_help_js = brotli.decompress(bytes(source_data[help_start:help_start + orig_help_len])).decode('utf-8')
        help_replacements = [
            ('Where are my files stored?', '我的文件存储在哪里？'),
            ('Files are Telegram messages in Saved Messages or private channels created as folders. Telegram Drive does not operate a separate cloud storage account.', '文件作为消息保存在您的 Telegram 我的云盘 (收藏夹) 或私密频道中。本工具不设第三方云存储服务器。'),
            ('What are the practical limits?', '实际使用有什么限制？'),
            ('A single Telegram object is limited to 2 GB in this app. Very large folders may take time to index; the live message count shows sync progress.', 'Telegram 单文件上限为 2 GB（大会员支持更高）。超大文件夹初次索引需要少量时间，界面会实时显示同步进度。'),
            ('What does Store & protect do?', '“端到端加密存储”有什么用？'),
            ('It encrypts file bytes locally before upload. Keep your vault passphrase and recovery bundle safe: Telegram cannot recover protected files for you.', '在上传前在本地加密文件内容。请务必牢记您的密钥与恢复包，Telegram 官方也无法解密被保护的文件。'),
            ('How does sharing work?', '分享功能是如何工作的？'),
            ('Choose a Telegram channel link, a local password-protected link, or WebDAV/REST. Local servers and capability URLs must be enabled explicitly.', '支持 Telegram 频道链接、本地密码保护分享直链或 WebDAV/REST 挂载，本地直链需保持电脑开机。'),
            ('Why does Finder Guest show an empty folder?', '为什么访客模式连接 WebDAV 显示为空？'),
            ('WebDAV access is granted by the token embedded in the complete /dav/<token>/ URL. Guest or anonymous login has no token-scoped access.', 'WebDAV 挂载必须使用包含完整 Token 的 URL 路径，匿名或访客登录无权访问。'),
            ('"Help & FAQ"', '"使用帮助与常见问题"'),
            ('"Close Help and FAQ"', '"关闭帮助"'),
            ('"Need more help?"', '"需要更多技术支持？"'),
            ('"Open support issues"', '"访问 GitHub 反馈问题"'),
        ]
        modified_help_js = raw_help_js
        for old, new in help_replacements:
            if old in modified_help_js:
                modified_help_js = modified_help_js.replace(old, new)

        comp_help = brotli.compress(modified_help_js.encode('utf-8'), quality=11)
        log(f"[3/6] Compressed HelpCenter: {len(modified_help_js)} raw -> {len(comp_help)} brotli bytes (slot: {orig_help_len})", "INFO")
        if len(comp_help) > orig_help_len:
            raise ValueError(f"Compressed HelpCenter ({len(comp_help)}) exceeds slot {orig_help_len}!")

        data[help_start:help_start + len(comp_help)] = comp_help
        data[help_start + len(comp_help):help_start + orig_help_len] = b'\x00' * (orig_help_len - len(comp_help))

        HELP_TABLE_ENTRY = 38445896
        data[HELP_TABLE_ENTRY:HELP_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_help))
        log(f"[3/6] HelpCenter table entry updated at {HELP_TABLE_ENTRY}: len={len(comp_help)}", "INFO")

        # ----------------------------------------------------
        # 6. Patch Slice 4: index-C0GG8Ndw.js (核心应用界面与开机自检进度)
        # ----------------------------------------------------
        index_marker = b'assets/index-C0GG8Ndw.js'
        index_pos = data.find(index_marker)
        if index_pos == -1:
            raise RuntimeError("index-C0GG8Ndw.js asset marker not found in binary!")
        index_start = index_pos + len(index_marker)
        orig_index_len = 162098

        raw_index_js = brotli.decompress(bytes(source_data[index_start:index_start + orig_index_len])).decode('utf-8')

        index_replacements = [
            # 基础导航与通用菜单
            ('logout:"Log Out"', 'logout:"退出登录"'),
            ('search_placeholder:"Search files..."', 'search_placeholder:"搜索文件..."'),
            ('sync:"Sync"', 'sync:"同步"'),
            ('upload:"Upload"', 'upload:"上传"'),
            ('folders:"Folders"', 'folders:"文件夹"'),
            ('create_folder:"Create Folder"', 'create_folder:"新建文件夹"'),
            ('saved_messages:"Saved Messages"', 'saved_messages:"我的云盘 (收藏夹)"'),
            ('preferences:"Preferences"', 'preferences:"偏好设置"'),
            ('about:"About"', 'about:"关于软件"'),
            ('diagnostics:"Connection Diagnostics"', 'diagnostics:"网络连接诊断"'),
            ('status:"Status"', 'status:"状态"'),
            ('ping:"Ping to Telegram"', 'ping:"Telegram 延迟"'),
            ('usage:"Data Usage (Session)"', 'usage:"本次会话流量"'),
            ('proxy:"Proxy"', 'proxy:"网络代理"'),
            ('enable_proxy:"Enable Proxy"', 'enable_proxy:"启用代理"'),
            ('proxy_type:"Proxy Type"', 'proxy_type:"代理类型"'),
            ('host:"Host"', 'host:"主机地址"'),
            ('port:"Port"', 'port:"端口"'),
            ('username:"Username"', 'username:"用户名"'),
            ('password:"Password"', 'password:"密码"'),
            ('theme:"Theme"', 'theme:"主题外观"'),
            ('close:"Close"', 'close:"关闭"'),
            ('files:"Files"', 'files:"云盘文件"'),
            ('transfers:"Transfers"', 'transfers:"传输管理"'),
            ('expand_sidebar:"Expand Sidebar"', 'expand_sidebar:"展开侧栏"'),
            ('collapse_sidebar:"Collapse Sidebar"', 'collapse_sidebar:"折叠侧栏"'),
            ('groups:"Groups"', 'groups:"文件夹分组"'),
            ('all:"All"', 'all:"全部"'),
            ('unassigned:"Unassigned"', 'unassigned:"未分组"'),
            ('hide_groups:"Hide Groups"', 'hide_groups:"隐藏分组"'),
            ('show_groups:"Show Groups"', 'show_groups:"显示分组"'),
            ('save:"Save"', 'save:"保存"'),
            ('create_group:"Create Group"', 'create_group:"创建分组"'),
            ('edit_group_name:"Edit Group Name"', 'edit_group_name:"编辑分组"'),
            ('new_group_name:"New Group Name"', 'new_group_name:"新分组名"'),
            ('theme_color:"Theme Color"', 'theme_color:"主题色"'),
            ('delete_group:"Delete Group"', 'delete_group:"删除分组"'),
            ('enter_group_name:"Enter group name..."', 'enter_group_name:"输入分组名称..."'),
            ('light_mode:"Light Mode"', 'light_mode:"浅色模式"'),
            ('dark_mode:"Dark Mode"', 'dark_mode:"深色模式"'),
            ('switch_light:"Switch to Light Mode"', 'switch_light:"切换浅色模式"'),
            ('switch_dark:"Switch to Dark Mode"', 'switch_dark:"切换深色模式"'),
            ('children:["How should we store ",a.count===1?"this file":`these ${a.count} files`,"?"]', 'children:["请选择",a.count===1?"此文件":`这 ${a.count} 个文件`,"的存储模式："]'),
            ('children:"You can keep the original file, or protect it with Telegram Drive encryption before upload."', 'children:"您可以直接原样上传，或在上传前使用专属加密保护。"'),
            ('children:"Store"', 'children:"普通极速存储"'),
            ('children:"Upload normally for maximum compatibility and easy sharing."', 'children:"正常上传，兼具最高兼容性与极速分享。"'),
            ('children:"Store & protect"', 'children:"端到端加密存储"'),
            ('children:"Encrypt before upload using your configured protection settings."', 'children:"上传前通过端到端密钥加密，云端无人能偷窥。"'),
            # 开机自检与 Telegram 握手全流程 (截图 1)
            ('label:"Checking local services",detail:"Verifying the database and streaming runtime…"', 'label:"检查本地服务环境",detail:"正在校验本地数据库与流媒体运行库…"'),
            ('label:"Restoring your session",detail:"Reading the saved Telegram account…"', 'label:"正在恢复登录会话",detail:"正在读取已保存的 Telegram 账户凭证…"'),
            ('label:"Ready to sign in",detail:"The saved session needs attention."', 'label:"准备就绪，请登录",detail:"保存的会话需要重新验证。"'),
            ('label:"Ready to sign in",detail:"No saved session was found."', 'label:"准备就绪，请登录",detail:"未检测到已保存的会话，请先登录。"'),
            ('label:"Starting Telegram",detail:"Initializing the secure desktop client…"', 'label:"正在启动 Telegram 核心服务",detail:"正在初始化安全桌面客户端…"'),
            ('label:"Checking your account",detail:"Confirming the session with Telegram…"', 'label:"正在验证电报账户",detail:"正在与 Telegram 官方服务器确认会话…"'),
            ('label:"Checking sponsor access",detail:"Finishing your local access checks…"', 'label:"正在完成安全校验",detail:"正在完成本地环境与权限检测…"'),
        ]

        modified_index_js = raw_index_js
        for old, new in index_replacements:
            if old in modified_index_js:
                modified_index_js = modified_index_js.replace(old, new)

        comp_index = brotli.compress(modified_index_js.encode('utf-8'), quality=11)
        log(f"[4/6] Compressed index JS: {len(modified_index_js)} raw -> {len(comp_index)} brotli bytes (slot: {orig_index_len})", "INFO")
        if len(comp_index) > orig_index_len:
            raise ValueError(f"Compressed index ({len(comp_index)}) exceeds allocated slot ({orig_index_len})!")

        data[index_start:index_start + len(comp_index)] = comp_index
        data[index_start + len(comp_index):index_start + orig_index_len] = b'\x00' * (orig_index_len - len(comp_index))

        INDEX_TABLE_ENTRY = 38445928
        data[INDEX_TABLE_ENTRY:INDEX_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_index))
        log(f"[4/6] index JS table entry updated at {INDEX_TABLE_ENTRY}: len={len(comp_index)}", "INFO")

        # ----------------------------------------------------
        # 7. Patch Slice 5: DesktopDashboard-DLH80hbX.js (主界面核心看板、空状态与赞助提示)
        # ----------------------------------------------------
        dd_marker = b'assets/DesktopDashboard-DLH80hbX.js'
        dd_pos = data.find(dd_marker)
        if dd_pos == -1:
            raise RuntimeError("DesktopDashboard asset marker not found in binary!")
        dd_start = dd_pos + len(dd_marker)
        orig_dd_len = 75096

        raw_dd_js = brotli.decompress(bytes(source_data[dd_start:dd_start + orig_dd_len])).decode('utf-8')

        dd_replacements = [
            # 空状态提示 (截图 3)
            ('children:"This folder is empty"', 'children:"此文件夹为空"'),
            ('children:"Drag and drop files here, or click the button below to upload from your computer."', 'children:"将文件拖拽至此处，或点击下方按钮从电脑上传。"'),
            ('children:["Tip: Use ",', 'children:["提示：使用 ",'),
            ('" to search"]', '" 快速搜索"]'),
            # 赞助提示弹窗 (截图 2)
            ('k==="loading"?"Loading…":`Closes in ${q}s`', 'k==="loading"?"正在加载…":`倒计时 ${q} 秒`'),
            ('"aria-label":"Remove ads forever for $5 once",children:[r.jsx(La,{className:"h-3.5 w-3.5","aria-hidden":"true"}),"Remove ads forever · $5 once"]', '"aria-label":"永久免除赞助提示",children:[r.jsx(La,{className:"h-3.5 w-3.5","aria-hidden":"true"}),"永久免除赞助提示 · 赞助支持"]'),
            ('k==="loading"?"Advertisement loading":`Advertisement closes in ${q} seconds`', 'k==="loading"?"赞助展示加载中":`赞助提示将于 ${q} 秒后自动关闭`'),
            # 流量小部件 (截图 3)
            ('children:r.jsx("span",{children:"Used this week:"})', 'children:r.jsx("span",{children:"本周已用流量:"})'),
            # 功能引导与收藏夹说明
            ('body:"Saved Messages is your home storage. Telegram Drive reads and writes files directly through your Telegram session."', 'body:"我的云盘 (收藏夹) 是您的基础存储空间。Telegram Drive 直接通过您的 Telegram 官方会话读写文件。"'),
            # 侧边栏与标题栏动态将 "Saved Messages" 统一映射为 "我的云盘 (收藏夹)"
            ('label:M("common.saved_messages")', 'label:M("common.saved_messages")==="Saved Messages"?"我的云盘 (收藏夹)":M("common.saved_messages")'),
            ('label:j.name', 'label:j.name==="Saved Messages"?"我的云盘 (收藏夹)":j.name'),
            ('Wi=d===null?n("common.saved_messages"):i.find(D=>D.id===d)?.name||n("common.folders")', 'Wi=d===null?(n("common.saved_messages")==="Saved Messages"?"我的云盘 (收藏夹)":n("common.saved_messages")):(i.find(D=>D.id===d)?.name==="Saved Messages"?"我的云盘 (收藏夹)":i.find(D=>D.id===d)?.name)||n("common.folders")'),
        ]

        modified_dd_js = raw_dd_js
        for old, new in dd_replacements:
            if old in modified_dd_js:
                modified_dd_js = modified_dd_js.replace(old, new)
            else:
                log(f"Warning: replacement pattern not found in DesktopDashboard: {old[:40]}", "WARNING")

        comp_dd = brotli.compress(modified_dd_js.encode('utf-8'), quality=11)
        log(f"[5/6] Compressed DesktopDashboard: {len(modified_dd_js)} raw -> {len(comp_dd)} brotli bytes (slot: {orig_dd_len})", "INFO")
        if len(comp_dd) > orig_dd_len:
            raise ValueError(f"Compressed DesktopDashboard ({len(comp_dd)}) exceeds slot {orig_dd_len}!")

        data[dd_start:dd_start + len(comp_dd)] = comp_dd
        data[dd_start + len(comp_dd):dd_start + orig_dd_len] = b'\x00' * (orig_dd_len - len(comp_dd))

        DD_TABLE_ENTRY = 38446440
        data[DD_TABLE_ENTRY:DD_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_dd))
        log(f"[5/6] DesktopDashboard table entry updated at {DD_TABLE_ENTRY}: len={len(comp_dd)}", "INFO")

        # ----------------------------------------------------
        # 8. Patch Slice 6: zh-TW-DOxb0aRJ.json (繁体补齐防漏)
        # ----------------------------------------------------
        zhtw_marker = b'assets/zh-TW-DOxb0aRJ.json'
        zhtw_pos = data.find(zhtw_marker)
        if zhtw_pos == -1:
            raise RuntimeError("zh-TW asset marker not found in binary!")
        zhtw_start = zhtw_pos + len(zhtw_marker)
        orig_zhtw_len = 16271

        raw_zhtw = brotli.decompress(bytes(source_data[zhtw_start:zhtw_start + orig_zhtw_len])).decode('utf-8')
        raw_zhtw = raw_zhtw.replace('"saved_messages":"Saved Messages"', '"saved_messages":"我的雲端硬碟 (收藏夾)"')
        raw_zhtw = raw_zhtw.replace('"disabled":"Folder Sync disabled"', '"disabled":"目錄自動同步已停用"')
        raw_zhtw = raw_zhtw.replace('"syncing":"Folder Sync running"', '"syncing":"目錄同步正在運行中..."')
        raw_zhtw = raw_zhtw.replace('"synced":"Folders synced"', '"synced":"所有資料夾均已同步最新"')
        raw_zhtw = raw_zhtw.replace('"conflicts":"Folder Sync needs attention"', '"conflicts":"目錄同步需要您處理衝突"')

        comp_zhtw = brotli.compress(raw_zhtw.encode('utf-8'), quality=11)
        log(f"[6/6] Compressed zh-TW: {len(raw_zhtw)} raw -> {len(comp_zhtw)} brotli bytes (slot: {orig_zhtw_len})", "INFO")
        if len(comp_zhtw) > orig_zhtw_len:
            raise ValueError(f"Compressed zh-TW ({len(comp_zhtw)}) exceeds slot {orig_zhtw_len}!")

        data[zhtw_start:zhtw_start + len(comp_zhtw)] = comp_zhtw
        data[zhtw_start + len(comp_zhtw):zhtw_start + orig_zhtw_len] = b'\x00' * (orig_zhtw_len - len(comp_zhtw))

        ZHTW_TABLE_ENTRY = 38447432
        data[ZHTW_TABLE_ENTRY:ZHTW_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_zhtw))
        log(f"[6/6] zh-TW table entry updated at {ZHTW_TABLE_ENTRY}: len={len(comp_zhtw)}", "INFO")

        # ----------------------------------------------------
        # 9. 内存自检闭环 (In-memory self-verification)
        # ----------------------------------------------------
        dec_zh = brotli.decompress(bytes(data[zh_start:zh_start + len(comp_zh)]))
        test_zh = json.loads(dec_zh.decode('utf-8'))
        assert test_zh['common']['saved_messages'] == "我的云盘 (收藏夹)"
        assert test_zh['sync']['status']['disabled'] == "目录自动同步已停用"

        dec_modal = brotli.decompress(bytes(data[modal_start:modal_start + len(comp_modal)])).decode('utf-8')
        assert 'placeholder:"搜索设置..."' in dec_modal
        assert '[["基础设置",' in dec_modal

        dec_help = brotli.decompress(bytes(data[help_start:help_start + len(comp_help)])).decode('utf-8')
        assert '我的文件存储在哪里？' in dec_help

        dec_index = brotli.decompress(bytes(data[index_start:index_start + len(comp_index)])).decode('utf-8')
        assert '正在验证电报账户' in dec_index
        assert 'saved_messages:"我的云盘 (收藏夹)"' in dec_index

        dec_dd = brotli.decompress(bytes(data[dd_start:dd_start + len(comp_dd)])).decode('utf-8')
        assert '此文件夹为空' in dec_dd
        assert '本周已用流量:' in dec_dd
        assert '永久免除赞助提示' in dec_dd

        dec_zhtw = brotli.decompress(bytes(data[zhtw_start:zhtw_start + len(comp_zhtw)])).decode('utf-8')
        assert '我的雲端硬碟 (收藏夾)' in dec_zhtw
        assert '目錄自動同步已停用' in dec_zhtw

        # 边界与相邻资源完整性校验 (确保绝不越界覆写任何相邻资源)
        assert data[help_start + orig_help_len] == 0x2f, "HelpCenter boundary corrupted next asset!"
        assert data[dd_start + orig_dd_len] == 0x2f, "DesktopDashboard boundary corrupted next asset!"
        assert data[zhtw_start + orig_zhtw_len] == 0x2f, "zh-TW boundary corrupted next asset!"

        log("All 6 slices in-memory self-verification & boundary checks PASSED 100%!", "SUCCESS")

        # 10. 写入目标可执行文件
        with open(target_app_path, "wb") as f:
            f.write(data)
        log(f"Successfully injected all 6 patches into: {target_app_path}", "SUCCESS")

        # 11. 同步到工具库
        tool_lib_target = r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe"
        if os.path.exists(os.path.dirname(tool_lib_target)):
            shutil.copyfile(target_app_path, tool_lib_target)
            log(f"Synchronized patched binary to Tool Library: {tool_lib_target}", "SUCCESS")

        # 12. 语言自动对齐到 zh-CN
        align_user_language_to_zh_cn()

        # 13. 清理 Chromium / WebView2 运行时缓存
        purge_webview_cache()
        log("WebView2 cache completely purged. Fresh launch guaranteed!", "SUCCESS")
        return True

    except Exception as e:
        log(f"Exception during patch execution: {e}\n{traceback.format_exc()}", "ERROR")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_patch(target)
    sys.exit(0 if success else 1)
