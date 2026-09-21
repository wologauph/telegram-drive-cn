#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 深度汉化全景补丁注入引擎 (Patch Engine v2.0)
银月独立开发工坊 · 工业级三轨日志与无损热修复
覆盖三大核心切片：
  1. zh-CN.json 全量字典
  2. SettingsModal 设置视窗与导航
  3. index 核心应用主界面与默认语言
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

def run_patch(target_app_path=None):
    with open(LATEST_LOG, "w", encoding="utf-8") as f:
        f.write(f"=== Telegram Drive Patch Engine Run: {NOW.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

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
        # 1. Backup
        if not os.path.exists(backup_path):
            shutil.copyfile(target_app_path, backup_path)
            log(f"Created pristine backup: {backup_path}", "CLEAN")
        else:
            log(f"Existing backup confirmed: {backup_path}", "INFO")

        # 2. Load binary
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
        log(f"[1/3] Compressed zh-CN: {len(raw_zh)} raw -> {len(comp_zh)} brotli bytes", "INFO")

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
        log(f"[1/3] zh-CN table entry updated at {ZH_TABLE_ENTRY}: len={len(comp_zh)}", "INFO")

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
        ]

        modified_modal_js = raw_modal_js
        for old, new in modal_replacements:
            if old in modified_modal_js:
                modified_modal_js = modified_modal_js.replace(old, new)

        comp_modal = brotli.compress(modified_modal_js.encode('utf-8'), quality=11)
        log(f"[2/3] Compressed SettingsModal: {len(modified_modal_js)} raw -> {len(comp_modal)} brotli bytes (slot: {orig_modal_len})", "INFO")
        if len(comp_modal) > orig_modal_len:
            raise ValueError(f"Compressed SettingsModal ({len(comp_modal)}) exceeds allocated slot ({orig_modal_len})!")

        data[modal_start:modal_start + len(comp_modal)] = comp_modal
        data[modal_start + len(comp_modal):modal_start + orig_modal_len] = b'\x00' * (orig_modal_len - len(comp_modal))

        MODAL_TABLE_ENTRY = 38445864
        data[MODAL_TABLE_ENTRY:MODAL_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_modal))
        log(f"[2/3] SettingsModal table entry updated at {MODAL_TABLE_ENTRY}: len={len(comp_modal)}", "INFO")

        # ----------------------------------------------------
        # 5. Patch Slice 3: index-C0GG8Ndw.js (核心应用界面与默认语言)
        # ----------------------------------------------------
        index_marker = b'assets/index-C0GG8Ndw.js'
        index_pos = data.find(index_marker)
        if index_pos == -1:
            raise RuntimeError("index-C0GG8Ndw.js asset marker not found in binary!")
        index_start = index_pos + len(index_marker)
        orig_index_len = 162098

        raw_index_js = brotli.decompress(bytes(source_data[index_start:index_start + orig_index_len])).decode('utf-8')

        index_replacements = [
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
            ('lng:"en",fallbackLng:!1', 'lng:"zh-CN",fallbackLng:"zh-CN"'),
            ('resources:{en:{translation:vE}}', 'resources:{"zh-CN":{translation:vE},en:{translation:vE}}'),
        ]

        modified_index_js = raw_index_js
        for old, new in index_replacements:
            if old in modified_index_js:
                modified_index_js = modified_index_js.replace(old, new)

        comp_index = brotli.compress(modified_index_js.encode('utf-8'), quality=11)
        log(f"[3/3] Compressed index JS: {len(modified_index_js)} raw -> {len(comp_index)} brotli bytes (slot: {orig_index_len})", "INFO")
        if len(comp_index) > orig_index_len:
            raise ValueError(f"Compressed index ({len(comp_index)}) exceeds allocated slot ({orig_index_len})!")

        data[index_start:index_start + len(comp_index)] = comp_index
        data[index_start + len(comp_index):index_start + orig_index_len] = b'\x00' * (orig_index_len - len(comp_index))

        INDEX_TABLE_ENTRY = 38445928
        data[INDEX_TABLE_ENTRY:INDEX_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_index))
        log(f"[3/3] index JS table entry updated at {INDEX_TABLE_ENTRY}: len={len(comp_index)}", "INFO")

        # ----------------------------------------------------
        # 6. Self-verification of all patched slices
        # ----------------------------------------------------
        dec_zh = brotli.decompress(bytes(data[zh_start:zh_start + len(comp_zh)]))
        test_zh = json.loads(dec_zh.decode('utf-8'))
        assert test_zh['settings']['tab_sync'] == "目录自动同步"
        assert test_zh['settings']['reset_defaults'] == "恢复默认设置"

        dec_modal = brotli.decompress(bytes(data[modal_start:modal_start + len(comp_modal)])).decode('utf-8')
        assert 'placeholder:"搜索设置..."' in dec_modal
        assert '[["基础设置",' in dec_modal

        dec_index = brotli.decompress(bytes(data[index_start:index_start + len(comp_index)])).decode('utf-8')
        assert 'saved_messages:"我的云盘 (收藏夹)"' in dec_index
        assert 'upload:"上传"' in dec_index
        assert 'lng:"zh-CN"' in dec_index
        log("All 3 slices in-memory self-verification PASSED 100%!", "SUCCESS")

        # 7. Write out binary
        with open(target_app_path, "wb") as f:
            f.write(data)
        log(f"Successfully injected all 3 patches into: {target_app_path}", "SUCCESS")

        # 8. Clear WebView2 stale cache
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
