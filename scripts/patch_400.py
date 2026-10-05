#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive v4.0.0 深度全景汉化、无损性能调优与免赞助补丁引擎 (Patch Engine v6.0)
银月独立开发工坊 · 工业级六轨资产无损切片热修复
"""

import os
import sys
import json
import struct
import shutil
import datetime
import traceback
import brotli

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LATEST_LOG = os.path.join(LOGS_DIR, "latest_run.log")

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)
    try:
        with open(LATEST_LOG, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

# 导入 v3.9.8 精校翻译字典作为基础
sys.path.append(os.path.join(os.path.dirname(__file__)))
from patch_398 import TRANSLATIONS

FULL_OVERRIDES = dict(TRANSLATIONS)
FULL_OVERRIDES.update({
    # 选项卡与导航
    "settings.tab_vpn": "网络与 VPN 调优",
    "settings.tab_webdav": "WebDAV 本地磁盘挂载",
    "settings.rest_api": "REST 本地接口",
    "common.app_title": "Telegram Drive",
    "auth.api_id": "API ID (应用程序编号)",

    # 赞助与授权全景
    "supporter_license.title": "终身免广告支持者授权",
    "supporter_license.nav_title": "赞助与授权",
    "supporter_license.purchased_title": "已激活免广告",
    "supporter_license.manage_license": "恢复或管理授权",
    "supporter_license.active": "终身免广告已生效",
    "supporter_license.inactive": "未激活赞助者授权",
    "supporter_license.checking": "正在检测授权状态...",
    "supporter_license.description": "所有功能在免费版均可完整使用。赞助支持可为已激活设备永久移除所有赞助提示。",
    "supporter_license.ad_free_life": "终身免广告",
    "supporter_license.free_forever": "永久免费版",
    "supporter_license.all_features": "解锁所有核心功能",
    "supporter_license.no_account_subscription": "无需注册第三方账户，零订阅收费",
    "supporter_license.sponsors_labeled": "带标签的赞助内容",
    "supporter_license.sponsors_removed": "永久移除赞助内容",
    "supporter_license.payment_verified": "赞助验证成功，已为您永久移除赞助提示！",
    "supporter_license.purchase_restored": "已成功在此设备上恢复已购授权！",

    # 启动与运行时
    "runtime.startup_initial_label": "正在启动 Telegram Drive",
    "runtime.startup_initial_detail": "正在准备本地运行环境…",
    "runtime.startup_local_label": "检查本地服务环境",
    "runtime.startup_local_detail": "正在校验本地数据库与流媒体运行库…",
    "runtime.startup_session_label": "正在恢复登录会话",
    "runtime.startup_session_detail": "正在读取已保存的 Telegram 账户凭证…",
    "runtime.startup_connect_label": "正在启动 Telegram 核心服务",
    "runtime.startup_connect_detail": "正在初始化安全桌面客户端…",
    "runtime.startup_account_label": "正在验证电报账户",
    "runtime.startup_account_detail": "正在与 Telegram 官方服务器确认会话…",
    "runtime.startup_sponsor_label": "正在完成安全自检",
    "runtime.startup_sponsor_detail": "正在完成本地环境与权限检测…",
    "runtime.startup_empty_label": "准备就绪，请登录",
    "runtime.startup_empty_detail": "未检测到已保存的会话，请先登录电报账号。",
    "runtime.startup_invalid_label": "登录凭据需要重新验证",
    "runtime.startup_invalid_detail": "保存的登录凭据已过期或失效，请重新登录。",

    # 帮助与常见问题
    "help_topics.storage_question": "我的文件存储在哪里？",
    "help_topics.storage_answer": "文件作为消息保存在您的 Telegram 我的云盘 (收藏夹) 或私密频道中。本软件不设任何第三方云存储服务器，完全安全私密。",
    "help_topics.limits_question": "实际使用有什么限制？",
    "help_topics.limits_answer": "Telegram 单文件上限为 2 GB（大会员支持更高）。超大文件夹初次索引需要少量时间，界面会实时显示同步进度。",
    "help_topics.protection_question": "“端到端加密存储”有什么用？",
    "help_topics.protection_answer": "在上传前在本地加密文件内容。请务必牢记您的密钥与恢复包，Telegram 官方也无法解密被保护的文件。",
    "help_topics.sharing_question": "分享功能是如何工作的？",
    "help_topics.sharing_answer": "支持 Telegram 频道链接、本地密码保护分享直链或 WebDAV/REST 挂载，本地直链需保持电脑开机。",
    "help_topics.guest_question": "为什么访客模式连接 WebDAV 显示为空？",
    "help_topics.guest_answer": "WebDAV 挂载必须使用包含完整 Token 的 URL 路径，匿名或访客登录无权访问。",
    "help_topics.more": "需要更多技术支持？",
    "help_topics.support": "访问 GitHub 反馈问题",

    # UI 常用文案
    "ui_copy.help_faq": "使用帮助与常见问题",
    "ui_copy.close_help": "关闭帮助",
    "ui_copy.keyboard_shortcuts": "快捷键指南",
    "ui_copy.close_shortcuts": "关闭快捷键指南",
    "ui_copy.global_scope": "所有云盘文件夹",
    "ui_copy.current_scope": "当前文件夹 / 视图",
    "ui_copy.understood": "我已知晓",
    "ui_copy.nav_essentials": "基础设置",
    "ui_copy.nav_connections": "连接与同步",
    "ui_copy.nav_security": "安全与隐私",
    "ui_copy.nav_support": "关于与支持",
    "ui_copy.security_center": "安全中心",
    "ui_copy.how_it_works": "工作原理说明",
    "ui_copy.dark": "深色模式",
    "ui_copy.light": "浅色模式",
    "ui_copy.vault": "加密保险库",
    "ui_copy.recovery": "灾难恢复",
    "ui_copy.recovery_verified": "恢复演练已验证通过",
    "ui_copy.unlocked_session": "当前会话已解锁",

    # 高级网络说明
    "advanced_copy.proxy_description": "通过 SOCKS5 或 HTTP 代理路由网络流量",
    "advanced_copy.rest_description": "本地 RESTful API 自动化控制接口与密钥管理",
    "advanced_copy.vpn_description": "网络长连接保持与高延迟环境优化",
    "advanced_copy.vpn_title": "网络优化器",
    "advanced_copy.webdav_description": "WebDAV 本地磁盘挂载与网络驱动器映射",

    # 上传选择
    "upload_choice_copy.question": "请选择这 {{count}} 个文件的存储模式：",
    "upload_choice_copy.description": "您可以直接原样上传，或在上传前使用专属加密保护。",
    "upload_choice_copy.store": "普通极速存储",
    "upload_choice_copy.plain_description": "正常上传，兼具最高兼容性与极速分享。",
    "upload_choice_copy.protect": "端到端加密存储",
    "upload_choice_copy.protect_description": "上传前通过端到端密钥加密，云端无人能偷窥。",
})

MODAL_REPLACEMENTS = [
    ('children:"Where your data goes"', 'children:"您的数据流向说明"'),
    ('children:"Telegram Drive has no account server of its own. Each destination below is separated by purpose."', 'children:"Telegram Drive 没有任何自建账户服务器。以下每个目的地均按用途严格隔离。"'),
    ('children:"Power-user connections are grouped here so everyday settings stay calm and focused. Use the settings search to find any option by name."', 'children:"高级用户连接选项已汇总于此，使日常设置保持简洁专注。您可通过搜索快速定位任意选项。"'),
    ('children:"REST API, WebDAV, proxy, VPN, and network tuning"', 'children:"REST API、WebDAV、网络代理、VPN 与底层传输调优"'),
    ('children:"Privacy policy summary:"', 'children:"隐私政策摘要："'),
    ('children:"Crash-only reporting"', 'children:"仅限崩溃日志上报"'),
    ('children:"Send anonymous crash reports"', 'children:"发送匿名崩溃报告"'),
    ('children:"Optional reports help diagnose unexpected app crashes. Normal usage, analytics, advertising activity, and file operations are never reported."', 'children:"可选报告有助于诊断应用意外崩溃。日常使用、统计分析、广告活动和文件操作绝不会被上报。"'),
    ('children:"Never sends file names, paths, contents, Telegram messages, credentials, or personal identifiers. Turning this off also clears reports waiting to be sent."', 'children:"绝不会发送文件名、路径、内容、Telegram 消息、凭据或个人身份信息。关闭此项还会清空待发送的报告。"'),
    ('children:"Use WebDAV, not SMB."', 'children:"请使用 WebDAV，而非 SMB。"'),
    ('Default restores the Quiet Utility theme. System follows your device, while presets and custom themes override these standard modes.', '默认模式将恢复极简主题。跟随系统将匹配设备外观，预设与自定义主题将覆盖这些标准模式。'),
    ('Connect with the complete generated', '请使用生成的完整'),
    ("URL. Finder's Guest/anonymous login has no token and will show an empty location; no guest account is created.", 'URL 连接。访客/匿名登录无 Token，将显示为空目录；软件不设访客账户。'),
]

DD_REPLACEMENTS = [
    ('children:"This folder is empty"', 'children:"此文件夹为空"'),
    ('children:"Drag and drop files here, or click the button below to upload from your computer."', 'children:"将文件拖拽至此处，或点击下方按钮从电脑上传。"'),
    ('children:"Used this week:"', 'children:"本周已用流量:"'),
    ('children:"All transfers complete"', 'children:"所有传输任务已完成"'),
    ('children:"Cancel all"', 'children:"全部取消"'),
    ('children:"Clear finished"', 'children:"清除已完成任务"'),
    ('children:"Error loading files"', 'children:"文件列表加载失败"'),
    ('children:"Your files are ready. Finished items can be cleared whenever you like."', 'children:"您的文件已就绪。已完成的项目可随时清除。"'),
    ('children:"This creates a private Telegram channel that Telegram Drive presents as a folder. Its files remain in your Telegram account."', 'children:"此操作将在您的 Telegram 账户中创建一个私密频道，并在本软件中作为文件夹呈现。文件将完整保存在您的电报账户中。"'),
]

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

def align_configurations():
    """彻底锁死用户配置：极致网络、长连接保活心跳、单队列防止丢包、锁定 zh-CN、关闭自动更新"""
    appdata = os.path.expandvars(r"%APPDATA%\com.cameronamer.telegramdrive")
    os.makedirs(appdata, exist_ok=True)

    settings_file = os.path.join(appdata, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            s = data.setdefault("settings", {})
            s["language"] = "zh-CN"
            s["autoUpdate"] = False
            s["keepAliveIntervalSec"] = 15     # 15秒长连接心跳，彻底防代理节点切断
            s["maxConcurrentUploads"] = 1       # 单并发，大文件独占稳定通道
            s["maxConcurrentDownloads"] = 2
            s["retryAttempts"] = 5              # 失败自动重试5次
            s["performanceMode"] = True         # 开启低功耗性能模式
            s["floodWaitRespect"] = True
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log("Aligned settings.json: language='zh-CN', autoUpdate=False, keepAlive=15s, maxUploads=1", "SUCCESS")
        except Exception as e:
            log(f"Failed to align settings.json: {e}", "WARNING")

    net_file = os.path.join(appdata, "network_settings.json")
    try:
        net_cfg = {
            "proxy": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 7897,
                "proxy_type": "socks5",
                "username": None,
                "password": None
            },
            "vpn": {
                "enabled": True,
                "preferred_dc": "auto",
                "timeout_multiplier": 4,
                "retry_attempts": 5,
                "retry_base_backoff_sec": 1.0,
                "retry_max_backoff_sec": 30,
                "bandwidth_limit_up_kbs": 0,
                "bandwidth_limit_down_kbs": 0,
                "chunk_size_kb": 512,
                "keep_alive_interval_sec": 15,
                "bulk_archive_max_mb": 0,
                "adaptive_polling": True
            }
        }
        with open(net_file, "w", encoding="utf-8") as f:
            json.dump(net_cfg, f, indent=2, ensure_ascii=False)
        log("Aligned network_settings.json: SOCKS5 127.0.0.1:7897, keep_alive=15s, chunk=512KB", "SUCCESS")
    except Exception as e:
        log(f"Failed to align network_settings.json: {e}", "WARNING")

def run_patch():
    target_app_path = r"D:\app\Telegram Drive\app.exe"
    if not os.path.exists(target_app_path):
        log(f"Target executable not found at: {target_app_path}", "ERROR")
        return False

    bak = target_app_path + ".v400.bak"
    if not os.path.exists(bak):
        shutil.copyfile(target_app_path, bak)
        log(f"Created pristine backup: {bak}", "CLEAN")

    log(f"Loading binary from pristine backup: {bak}", "INFO")
    with open(bak, "rb") as f:
        data = bytearray(f.read())
    log(f"Loaded binary into memory: {len(data)} bytes", "INFO")

    # 1. Patch Slice 1: zh-CN-CkbYkfWF.json
    zh_marker = b"/assets/zh-CN-CkbYkfWF.json"
    zh_pos = data.find(zh_marker)
    if zh_pos == -1:
        raise RuntimeError("v4.0.0 zh-CN marker not found in binary!")
    zh_slot_len = 16291
    zh_table_entry = 42480520
    zh_start = zh_pos + len(zh_marker)

    tkeys_marker = b"/assets/translation-keys-DEga68nQ.json"
    tkeys_pos = data.find(tkeys_marker)
    tkeys = json.loads(brotli.decompress(bytes(data[tkeys_pos + len(tkeys_marker) : tkeys_pos + len(tkeys_marker) + 7950])).decode('utf-8'))['keys']

    raw_zh_bytes = brotli.decompress(bytes(data[zh_start:zh_start + zh_slot_len]))
    zh_dict = json.loads(raw_zh_bytes.decode('utf-8'))
    zh_vals = list(zh_dict['values'])

    for idx, key in enumerate(tkeys):
        if key in FULL_OVERRIDES:
            zh_vals[idx] = FULL_OVERRIDES[key]

    zh_dict['values'] = zh_vals
    zh_encoded = json.dumps(zh_dict, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    comp_zh = brotli.compress(zh_encoded, quality=11)
    log(f"[1/5] Compressed zh-CN: {len(zh_encoded)} raw -> {len(comp_zh)} brotli bytes (slot: {zh_slot_len})", "INFO")
    if len(comp_zh) > zh_slot_len:
        raise ValueError(f"zh-CN exceeds slot: {len(comp_zh)} > {zh_slot_len}")

    data[zh_start:zh_start + len(comp_zh)] = comp_zh
    data[zh_start + len(comp_zh):zh_start + zh_slot_len] = b'\x00' * (zh_slot_len - len(comp_zh))
    data[zh_table_entry:zh_table_entry + 8] = struct.pack('<Q', len(comp_zh))
    log(f"[1/5] zh-CN table entry updated at {zh_table_entry}: len={len(comp_zh)}", "SUCCESS")

    # 2. Patch Slice 2: SettingsModal-43sao1kq.js
    modal_marker = b"/assets/SettingsModal-43sao1kq.js"
    modal_pos = data.find(modal_marker)
    if modal_pos == -1:
        raise RuntimeError("v4.0.0 SettingsModal marker not found!")
    modal_slot_len = 27919
    modal_table_entry = 42482632
    modal_start = modal_pos + len(modal_marker)

    raw_modal_js = brotli.decompress(bytes(data[modal_start:modal_start + modal_slot_len])).decode('utf-8')
    mod_modal = raw_modal_js
    for old, new in MODAL_REPLACEMENTS:
        if old in mod_modal:
            mod_modal = mod_modal.replace(old, new)

    comp_modal = brotli.compress(mod_modal.encode('utf-8'), quality=11)
    log(f"[2/5] Compressed SettingsModal: {len(mod_modal)} raw -> {len(comp_modal)} brotli bytes (slot: {modal_slot_len})", "INFO")
    if len(comp_modal) > modal_slot_len:
        raise ValueError(f"SettingsModal exceeds slot: {len(comp_modal)} > {modal_slot_len}")

    data[modal_start:modal_start + len(comp_modal)] = comp_modal
    data[modal_start + len(comp_modal):modal_start + modal_slot_len] = b'\x00' * (modal_slot_len - len(comp_modal))
    data[modal_table_entry:modal_table_entry + 8] = struct.pack('<Q', len(comp_modal))
    log(f"[2/5] SettingsModal table entry updated at {modal_table_entry}: len={len(comp_modal)}", "SUCCESS")

    # 3. Patch Slice 3: DesktopDashboard-mGTjIwIz.js
    dd_marker = b"/assets/DesktopDashboard-mGTjIwIz.js"
    dd_pos = data.find(dd_marker)
    if dd_pos == -1:
        raise RuntimeError("v4.0.0 DesktopDashboard marker not found!")
    dd_slot_len = 76845
    dd_table_entry = 42480488
    dd_start = dd_pos + len(dd_marker)

    raw_dd_js = brotli.decompress(bytes(data[dd_start:dd_start + dd_slot_len])).decode('utf-8')
    mod_dd = raw_dd_js
    for old, new in DD_REPLACEMENTS:
        if old in mod_dd:
            mod_dd = mod_dd.replace(old, new)

    # 斩断广告横幅组件
    target_qf = 'function qf({suppressed:e=!1,onSupport:t,onManualDismiss:n,previewContent:r}){'
    if target_qf in mod_dd:
        mod_dd = mod_dd.replace(target_qf, target_qf + 'return null;')
        log("[KILL] Neutralized qf Ad Banner component with 'return null'", "CLEAN")

    # 斩断 SupporterOfferDialog 动态挂载
    target_th = 'b&&s.jsx(mt,{children:s.jsx(Th,{trigger:b,'
    if target_th in mod_dd:
        mod_dd = mod_dd.replace(target_th, '!1&&s.jsx(mt,{children:s.jsx(Th,{trigger:b,')
        log("[KILL] Neutralized Th SupporterOfferDialog mount with '!1&&...'", "CLEAN")

    comp_dd = brotli.compress(mod_dd.encode('utf-8'), quality=11)
    log(f"[3/5] Compressed DesktopDashboard: {len(mod_dd)} raw -> {len(comp_dd)} brotli bytes (slot: {dd_slot_len})", "INFO")
    if len(comp_dd) > dd_slot_len:
        raise ValueError(f"DesktopDashboard exceeds slot: {len(comp_dd)} > {dd_slot_len}")

    data[dd_start:dd_start + len(comp_dd)] = comp_dd
    data[dd_start + len(comp_dd):dd_start + dd_slot_len] = b'\x00' * (dd_slot_len - len(comp_dd))
    data[dd_table_entry:dd_table_entry + 8] = struct.pack('<Q', len(comp_dd))
    log(f"[3/5] DesktopDashboard table entry updated at {dd_table_entry}: len={len(comp_dd)}", "SUCCESS")

    # 4. Patch Slice 4: SupporterOfferDialog-pvEusOCY.js
    supp_marker = b"/assets/SupporterOfferDialog-pvEusOCY.js"
    supp_pos = data.find(supp_marker)
    if supp_pos != -1:
        supp_slot_len = 1679
        supp_table_entry = 42481320
        supp_start = supp_pos + len(supp_marker)
        raw_supp_js = brotli.decompress(bytes(data[supp_start:supp_start + supp_slot_len])).decode('utf-8')
        mod_supp = raw_supp_js
        target_fn = 'function v({trigger:r,presentation:n="dialog",onClose:s,onOpenSupporter:p}){'
        if target_fn in mod_supp:
            mod_supp = mod_supp.replace(target_fn, target_fn + 'return null;')
            log("[KILL] Neutralized SupporterOfferDialog v component with 'return null'", "CLEAN")

        comp_supp = brotli.compress(mod_supp.encode('utf-8'), quality=11)
        if len(comp_supp) <= supp_slot_len:
            data[supp_start:supp_start + len(comp_supp)] = comp_supp
            data[supp_start + len(comp_supp):supp_start + supp_slot_len] = b'\x00' * (supp_slot_len - len(comp_supp))
            data[supp_table_entry:supp_table_entry + 8] = struct.pack('<Q', len(comp_supp))
            log(f"[4/5] SupporterOfferDialog table entry updated at {supp_table_entry}: len={len(comp_supp)}", "SUCCESS")

    # 5. Patch Slice 5: index-Bo5-zB0o.js
    idx_marker = b"/assets/index-Bo5-zB0o.js"
    idx_pos = data.find(idx_marker)
    if idx_pos == -1:
        raise RuntimeError("v4.0.0 index marker not found!")
    idx_slot_len = 150588
    idx_table_entry = 42481576
    idx_start = idx_pos + len(idx_marker)

    raw_idx_js = brotli.decompress(bytes(data[idx_start:idx_start + idx_slot_len])).decode('utf-8')
    mod_idx = raw_idx_js

    target_gd = 'function gD(n){return n.state!=="loading"&&!n.ad_free}'
    if target_gd in mod_idx:
        mod_idx = mod_idx.replace(target_gd, 'function gD(n){return!1/*====================*/&&!n.ad_free}')
        log("[KILL] Disabled gD sponsor check in index-Bo5-zB0o.js", "CLEAN")

    target_yd = 'function yD(n){return n.state==="inactive"&&!n.ad_free&&!n.recovery_code_saved}'
    if target_yd in mod_idx:
        mod_idx = mod_idx.replace(target_yd, 'function yD(n){return!1/*==========================================*/&&!n.ad_free}')
        log("[KILL] Disabled yD sponsor check in index-Bo5-zB0o.js", "CLEAN")

    comp_idx = brotli.compress(mod_idx.encode('utf-8'), quality=11)
    log(f"[5/5] Compressed index JS: {len(mod_idx)} raw -> {len(comp_idx)} brotli bytes (slot: {idx_slot_len})", "INFO")
    if len(comp_idx) > idx_slot_len:
        raise ValueError(f"index exceeds slot: {len(comp_idx)} > {idx_slot_len}")

    data[idx_start:idx_start + len(comp_idx)] = comp_idx
    data[idx_start + len(comp_idx):idx_start + idx_slot_len] = b'\x00' * (idx_slot_len - len(comp_idx))
    data[idx_table_entry:idx_table_entry + 8] = struct.pack('<Q', len(comp_idx))
    log(f"[5/5] index table entry updated at {idx_table_entry}: len={len(comp_idx)}", "SUCCESS")

    # 边界断言自检
    assert data[zh_start + zh_slot_len] == 0x2f, "zh boundary corrupted!"
    assert data[modal_start + modal_slot_len] == 0x2f, "modal boundary corrupted!"
    assert data[dd_start + dd_slot_len] == 0x2f, "dd boundary corrupted!"
    assert data[supp_start + supp_slot_len] == 0x2f, "supp boundary corrupted!"
    assert data[idx_start + idx_slot_len] == 0x2f, "idx boundary corrupted!"

    # 写入二进制文件
    with open(target_app_path, "wb") as f:
        f.write(data)
    log(f"Successfully injected all patches into: {target_app_path}", "SUCCESS")

    # 同步工具库
    tool_lib_target = r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe"
    if os.path.exists(os.path.dirname(tool_lib_target)):
        shutil.copyfile(target_app_path, tool_lib_target)
        log(f"Synchronized patched v4.0.0 binary to Tool Library: {tool_lib_target}", "SUCCESS")

    # 对齐用户配置与清空 WebView2 缓存
    align_configurations()
    purge_webview_cache()
    log("Configurations aligned and WebView2 cache purged. Ready to launch!", "SUCCESS")
    return True

if __name__ == "__main__":
    try:
        ok = run_patch()
        sys.exit(0 if ok else 1)
    except Exception as e:
        log(f"Fatal error: {e}\n{traceback.format_exc()}", "ERROR")
        sys.exit(1)
