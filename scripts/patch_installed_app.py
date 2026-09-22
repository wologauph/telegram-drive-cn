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
            # 基础与分类导航 (截图 1/3)
            ('placeholder:"Search settings"', 'placeholder:"搜索设置..."'),
            ('[["Essentials",', '[["基础设置",'),
            ('["Security & Privacy",', '["安全与隐私",'),
            ('["Connections",', '["连接与同步",'),
            ('["Advanced",', '["高级网络",'),
            ('["Support",', '["关于与支持",'),
            ('_==="privacy"?"Privacy":_==="advanced"?"Advanced":t(`settings.tab_${_}`)', '_==="privacy"?"隐私遥测":_==="advanced"?"高级集成":t(`settings.tab_${_}`)'),
            ('j==="privacy"?"Privacy, crash reporting & supporter license":j==="advanced"?"Advanced connections and integrations":t(`settings.tab_${j}`)', 'j==="privacy"?"隐私保护、崩溃报告与支持者选项":j==="advanced"?"高级网络连接与系统集成":t(`settings.tab_${j}`)'),

            # 高级集成看板与卡片 (截图 3/4)
            ('children:"Advanced"', 'children:"高级网络与系统集成"'),
            ('children:"Power-user connections are grouped here so everyday settings stay calm and focused. Use the settings search to find any option by name."', 'children:"面向高阶玩家的连接与集成选项聚合于此，让日常设置保持清爽专注。您也可以使用顶部的搜索框快速定位任何选项。"'),
            ('["REST API","Local automation endpoint and API key"', '["REST API","本地自动化接口端点与 API 密钥"'),
            ('["WebDAV","Finder and file-manager access"', '["WebDAV 本地磁盘挂载","文件资源管理器及本地虚拟盘访问"'),
            ('["Proxy","SOCKS5 and HTTP bridge settings"', '["网络代理 (Proxy)","SOCKS5 代理及 HTTP 桥接配置"'),
            ('["VPN & network","Retries, bandwidth, and data-center tuning"', '["VPN 与网络调优","重试机制、带宽限制与 Telegram 数据中心调优"'),

            # 隐私遥测与数据流向 (截图 1/2/5)
            ('children:"Where your data goes"', 'children:"数据流向透明说明"'),
            ('children:"Telegram Drive has no account server of its own. Each destination below is separated by purpose."', 'children:"Telegram Drive 本身不设立任何用户账户服务器。下述各项数据去向严格按用途独立隔离。"'),
            ('["This device","Settings, queue state, thumbnails, and encrypted vault material stay local."', '["本机存储","软件设置、传输队列状态、缩略图缓存及端到端加密密钥等均严格保存在本地。"'),
            ('["Telegram","Folder channels and uploaded file messages go directly to your Telegram account."', '["Telegram 官方云端","文件夹频道与上传的文件消息直接存入您的 Telegram 官方账户。"'),
            ('["Sponsors","Sponsor content loads only in labeled ad areas. File activity is never sent to sponsors."', '["赞助者内容","赞助内容仅在明确标注的广告区域加载。文件传输活动绝不会发送给赞助商。"'),
            ('["Crash reports","Only after consent: app version, platform, error type, and sanitized function names."', '["崩溃报告","仅在征得同意后上传：应用版本、操作系统平台、错误类型及脱敏后的函数名。"'),
            ('children:[e.jsx("strong",{className:"text-app-text",children:"Privacy policy summary:"})," Telegram Drive does not sell personal data, inspect file contents for analytics, or operate a cloud account database. Revoking a share or disabling a local server stops that access immediately."]', 'children:[e.jsx("strong",{className:"text-app-text",children:"隐私政策概要："})," Telegram Drive 绝不出售个人数据、绝不分析审查文件内容、亦不维护第三方云账户数据库。撤销分享或关闭本地服务将立即终止访问权限。"]'),
            ('children:"Crash-only reporting"', 'children:"仅限崩溃的错误反馈"'),
            ('children:"Optional reports help diagnose unexpected app crashes. Normal usage, analytics, advertising activity, and file operations are never reported."', 'children:"可选报告有助于排查意外闪退问题。日常使用、统计分析、广告活动及文件操作绝不上报。"'),
            ('children:"Send anonymous crash reports"', 'children:"发送匿名崩溃报告"'),
            ('"aria-label":"Send anonymous crash reports"', '"aria-label":"发送匿名崩溃报告"'),
            ('children:"Never sends file names, paths, contents, Telegram messages, credentials, or personal identifiers. Turning this off also clears reports waiting to be sent."', 'children:"绝不发送文件名、路径、文件内容、电报消息、登录凭证或个人标识。关闭此项还将清空等待发送的待办报告。"'),

            # 加密设置云同步 (截图 1/2)
            ('children:"Encrypted settings sync"', 'children:"加密设置云同步"'),
            ('children:"Manually move safe app preferences between devices through your own Telegram Saved Messages. Telegram Drive operates no sync server."', 'children:"通过您自己的 Telegram 我的云盘 (收藏夹) 安全跨设备同步偏好设置。本工具不运行任何中心化同步服务器。"'),
            ('"aria-label":"Enable encrypted settings sync"', '"aria-label":"启用加密设置云同步"'),
            ('children:[e.jsx("strong",{className:"text-app-text",children:"Your passphrase cannot be recovered."})," It is used locally and is never stored or uploaded. The encrypted Telegram message may be visible in Saved Messages. Passwords, API/WebDAV keys, proxy details, supporter activation, crash consent, and file data are always excluded."]', 'children:[e.jsx("strong",{className:"text-app-text",children:"您的同步口令无法通过任何途径找回。"})," 口令仅在本地用于加解密，绝不会被存储或上传。加密同步消息可能会显示在您的“我的云盘 (收藏夹)”中。密码、API/WebDAV 密钥、代理信息、赞助授权、崩溃反馈选项与文件本体均已被严格排除，不参与同步。"]'),
            ('children:"Sync passphrase"', 'children:"同步口令密码"'),
            ('placeholder:"At least 12 characters"', 'placeholder:"至少 12 个字符"'),
            ('"Upload this device"', '"上传此设备配置"'),
            ('"Download and apply"', '"下载并应用云端配置"'),
            ('"aria-label":"Refresh settings sync status"', '"aria-label":"刷新设置同步状态"'),
            ('title:"Replace the settings backup?"', 'title:"是否覆盖云端已有备份？"'),
            ('message:"The latest encrypted backup came from another device. Uploading will replace it with this device’s current safe preferences."', 'message:"云端最新的加密备份来自其他设备。继续上传将以此设备的当前安全配置覆盖云端已有备份。"'),
            ('confirmText:"Replace backup"', 'confirmText:"覆盖云端备份"'),
            ('title:"Apply settings from Telegram?"', 'title:"应用来自 Telegram 的云端配置？"'),
            ('message:"Synced display, transfer, network-tuning, and encryption preferences will replace their local values. Credentials and activation data are not changed."', 'message:"同步的显示、传输、网络调优及加密偏好将替换本地数值。登录凭据和授权信息不会改变。"'),
            ('confirmText:"Apply settings"', 'confirmText:"应用配置"'),
            ('"Encrypted settings uploaded to Telegram Saved Messages."', '"加密设置已成功备份至 Telegram 我的云盘 (收藏夹)。"'),
            ('"Encrypted settings downloaded and applied."', '"云端加密设置已成功下载并应用。"'),
            ('"No encrypted settings backup was found in the latest 1,000 Saved Messages."', '"在最近 1,000 条收藏夹消息中未发现加密的设置备份。"'),
            ('h.current_device?" · uploaded by this device":" · uploaded by another device"', 'h.current_device?" · 由此设备上传":" · 由其他设备上传"'),
            ('`Latest backup: ${', '`最新备份时间: ${'),

            # 赞助与授权状态 (截图 1/2)
            ('children:"Lifetime Ad-Free Supporter License"', 'children:"终身免赞助广告支持者授权"'),
            ('children:"Every feature stays available in the free version. This optional license only removes sponsor placements on activated supported devices."', 'children:"免费版本已解锁全部核心功能。此可选赞助授权仅用于在已激活设备上移除赞助展示。"'),
            ('"No supporter license is active"', '"未激活赞助者授权"'),
            ('"Checking activation"', '"正在检测激活状态"'),
            ('"Lifetime ad-free access is active"', '"终身免广告授权已生效"'),
            ('"Activation revoked"', '"激活授权已被撤销"'),
            ('"Activation needs to be refreshed"', '"激活授权需要刷新"'),
            ('"Activation service unavailable"', '"激活验证服务暂不可用"'),
            ('"Previous purchase found on this device"', '"检测到此设备先前的购买记录"'),
            ('children:I}),e.jsx("span",{className:"mt-1 block",children:s.message})', 'children:I}),e.jsx("span",{className:"mt-1 block",children:s.message==="No verified supporter activation is stored on this device."?"当前设备尚未检测到已激活的赞助凭证。":s.message})'),
            ('children:"Normal Telegram Drive updates reuse this device’s secure credential automatically—no reactivation or repeat payment is required."', 'children:"Telegram Drive 的常规更新会自动沿用此设备的安全凭证——无需重新激活或重复付款。"'),
            ('children:"You already have purchase history on this device. Refresh or restore below; do not pay again."', 'children:"此设备已有购买记录。请在下方刷新或恢复授权，切勿重复付款。"'),
            ('children:"Ad-free for life"', 'children:"终身无广告"'),
            ('children:"One payment. No subscription. No sponsor ads."', 'children:"一次性支持，绝无订阅套路，彻底告别赞助展示。"'),
            ('children:"Verified for up to three supported devices total across desktop and Android. Normal app updates are included."', 'children:"支持在电脑与安卓端共计最多 3 台设备上激活。享受后续所有常规更新。"'),
            ('children:"Free forever"', 'children:"永久免费版"'),
            ('"Every app feature"', '"包含所有软件功能"'),
            ('"No supporter account or subscription"', '"无需注册赞助账户，零订阅收费"'),
            ('"Labeled sponsor placements"', '"包含带标签的赞助内容展示"'),
            ('children:"$5 lifetime supporter"', 'children:"终身支持者权益"'),
            ('Sponsor placements removed', '永久移除所有赞助提示与广告位'),
            ('Normal updates stay activated', '软件后续升级自动保持激活'),
            ('children:"How activation works"', 'children:"激活流程说明"'),
            ('Pay with PayPal', '通过 PayPal 安全支付'),
            ('Return to the app', '返回软件视窗'),
            ('Save your recovery code', '妥善保管恢复码'),
            ('Checkout opens securely in your browser.', '将在系统默认浏览器中安全打开支付页面。'),
            ('Keep Telegram Drive open while payment is verified.', '支付验证期间请保持 Telegram Drive 运行。'),
            ('Use it after a reinstall or on another device.', '重装系统或迁移到其他设备时凭此恢复。'),
            ('children:[e.jsx("strong",{className:"text-app-text",children:"Private and predictable:"})," PayPal processes the payment. Telegram Drive does not receive or store your card details or PayPal email, and there is no recurring charge."]', 'children:[e.jsx("strong",{className:"text-app-text",children:"隐私与明细保障："})," 付款全流程由 PayPal 处理。Telegram Drive 绝不收集或储存您的银行卡与邮箱信息，且没有任何自动续费机制。"]'),
            ('children:"Save this recovery code now"', 'children:"请立即保存此恢复码"'),
            ('children:"It is stored in this device’s secure credential manager, but you should also keep an offline copy. Telegram Drive does not store your email and cannot reconstruct a lost code."', 'children:"该码已加密保存在本机安全管理器中，但仍建议您在离线处备份一份。由于不收集邮箱，若恢复码遗失将无法人工补发。"'),
            ('children:"Waiting for PayPal confirmation"', 'children:"正在等待 PayPal 确认到账"'),
            ('children:"Keep this app open after approving payment. Verification normally updates automatically; use “Check payment” if it does not."', 'children:"授权付款后请保持本应用开启。系统通常会自动完成校验；若未刷新可手动点击“检查支付状态”。"'),
            ('"Important purchase and refund information"', '"重要购买与退款政策"'),
            ('children:"Refunds are not automatic and are not guaranteed except where required by law. A refund, reversal, chargeback, or upheld dispute revokes ad-free access. Payment and activation depend on PayPal, internet access, and secure credential storage; keep your recovery code."', 'children:"除法律另有强制规定外，退款并非自动受理且不作承诺。若发生退款、拒付、撤单或纠纷成立，免广告权益将被撤销。激活依赖于网络畅通与本地安全存储，请务必妥善保存您的恢复码。"'),
            ('children:"Supporter Terms"', 'children:"支持者条款"'),
            ('eckout…":v?"Checkout opened":"Get lifetime ad-free · $5"', 'eckout…":v?"结账页面已在浏览器中打开":"获取终身免赞助广告支持 · 赞助支持"'),
            ('children:"Check payment"', 'children:"检查支付状态"'),
            ('children:"Refresh verification"', 'children:"刷新授权凭证"'),
            ('children:"Read full terms"', 'children:"查阅完整条款"'),
            ('children:"Activation help"', 'children:"激活常见疑问"'),
            ('children:"Already supported? Restore with a recovery code"', 'children:"已经是支持者？使用恢复码恢复权益"'),
            ('children:"Normal updates do not need this code. Use it after a reinstall or on another device; restoration requires the current terms and counts toward the three-device limit."', 'children:"常规升级无需此码。在电脑重装或在另一台设备上启用时使用；恢复授权计入 3 台设备限额。"'),
            ('children:"Restore purchase"', 'children:"恢复已购授权"'),
            ('children:"If activation is delayed, check payment once, then open Activation help. Never post your recovery code or payment identifiers in a public issue, and do not pay a second time."', 'children:"若激活延迟，请点击一次“检查支付状态”；若仍未生效请查看帮助。切勿在公开平台透露您的恢复码，且无需二次付款。"'),

            # WebDAV 与 REST API 弹窗及说明
            ('title:"Before enabling WebDAV access"', 'title:"开启 WebDAV 本地挂载须知"'),
            ('g?"How WebDAV access works":"How REST access works"', 'g?"WebDAV 本地挂载机制说明":"REST API 访问机制说明"'),
            ('children:"Use WebDAV, not SMB."', 'children:"请使用 WebDAV 协议挂载，不支持 SMB。"'),
            ('"Understand WebDAV permissions"', '"了解 WebDAV 权限范围"'),
            ('title:"Before enabling REST access"', 'title:"开启 REST 本地自动化须知"'),
            ('"Understand REST permissions"', '"了解 REST 权限范围"'),
            ('confirmText:"I understand — enable"', 'confirmText:"我已充分理解 — 立即开启"'),
            ('"aria-label":"Close local access explanation"', '"aria-label":"关闭说明"'),
            ('title:"Copy to clipboard"', 'title:"复制到剪贴板"'),

            # 网络诊断与测试
            ('"Periodically check connectivity and display latency"', '"定时检测网络连通性并显示延迟"'),
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
        assert '数据流向透明说明' in dec_modal
        assert '高级网络与系统集成' in dec_modal
        assert '当前设备尚未检测到已激活的赞助凭证。' in dec_modal

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
