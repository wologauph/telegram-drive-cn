#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive 深度汉化补丁注入引擎 (Patch Engine)
银月独立开发工坊 · 工业级三轨日志与无损热修复
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
    # Write to latest_run.log
    with open(LATEST_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    # Write to monthly archive log
    with open(MONTH_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")
    if level == "ERROR":
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

def run_patch(target_app_path=None):
    # Initialize latest_run.log (overwrite mode)
    with open(LATEST_LOG, "w", encoding="utf-8") as f:
        f.write(f"=== Telegram Drive Patch Engine Run: {NOW.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    if not target_app_path:
        default_paths = [
            r"D:\app\Telegram Drive\app.exe",
            r"D:\我的电脑工具库\02_网络与传输工具\Telegram-Drive-CN\app.exe",
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

        # Load pristine source data for decompressing original assets
        source_data = data
        if os.path.exists(backup_path):
            with open(backup_path, "rb") as f:
                source_data = f.read()
            log("Loaded pristine backup for asset extraction", "INFO")

        # 3. Load full translated zh-CN.json
        zh_json_path = os.path.join(PROJECT_ROOT, "app", "src", "i18n", "locales", "zh-CN.json")
        with open(zh_json_path, "r", encoding="utf-8") as f:
            zh_content = json.load(f)
        raw_zh = json.dumps(zh_content, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        comp_zh = brotli.compress(raw_zh, quality=11)
        log(f"Compressed zh-CN dictionary: {len(raw_zh)} raw -> {len(comp_zh)} brotli bytes", "INFO")

        # 4. Locate zh-CN slice in binary
        zh_marker = b'/assets/zh-CN-CSiX_qds.json'
        zh_pos = data.find(zh_marker)
        if zh_pos == -1:
            raise RuntimeError("zh-CN asset marker not found in binary!")
        zh_start = zh_pos + len(zh_marker)
        orig_zh_len = 16133
        if len(comp_zh) > orig_zh_len:
            raise ValueError(f"Compressed zh-CN ({len(comp_zh)}) exceeds allocated slot ({orig_zh_len})!")

        # 5. Extract and patch SettingsModal JS
        modal_marker = b'assets/SettingsModal-B1qI0t1k.js'
        modal_pos = data.find(modal_marker)
        if modal_pos == -1:
            raise RuntimeError("SettingsModal asset marker not found in binary!")
        modal_start = modal_pos + len(modal_marker)
        orig_modal_len = 29303

        raw_modal_js = brotli.decompress(bytes(source_data[modal_start:modal_start + orig_modal_len])).decode('utf-8')

        replacements = [
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
        for old, new in replacements:
            if old in modified_modal_js:
                modified_modal_js = modified_modal_js.replace(old, new)
            else:
                log(f"Modal string skipped or already patched: {old[:30]}...", "WARNING")

        comp_modal = brotli.compress(modified_modal_js.encode('utf-8'), quality=11)
        log(f"Compressed SettingsModal: {len(modified_modal_js)} raw -> {len(comp_modal)} brotli bytes (slot: {orig_modal_len})", "INFO")
        if len(comp_modal) > orig_modal_len:
            raise ValueError(f"Compressed SettingsModal ({len(comp_modal)}) exceeds allocated slot ({orig_modal_len})!")

        # 6. Inject slices and zero-pad slots
        data[zh_start:zh_start + len(comp_zh)] = comp_zh
        data[zh_start + len(comp_zh):zh_start + orig_zh_len] = b'\x00' * (orig_zh_len - len(comp_zh))

        data[modal_start:modal_start + len(comp_modal)] = comp_modal
        data[modal_start + len(comp_modal):modal_start + orig_modal_len] = b'\x00' * (orig_modal_len - len(comp_modal))

        # 7. Update central asset length table
        ZH_TABLE_ENTRY = 38446664
        data[ZH_TABLE_ENTRY:ZH_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_zh))

        MODAL_TABLE_ENTRY = 38445864
        data[MODAL_TABLE_ENTRY:MODAL_TABLE_ENTRY + 8] = struct.pack('<Q', len(comp_modal))

        log(f"Asset table entries updated: zh-CN={len(comp_zh)}, SettingsModal={len(comp_modal)}", "INFO")

        # 8. Self-verification
        dec_zh = brotli.decompress(bytes(data[zh_start:zh_start + len(comp_zh)]))
        test_zh = json.loads(dec_zh.decode('utf-8'))
        assert test_zh['settings']['tab_sync'] == "目录自动同步"
        assert test_zh['settings']['reset_defaults'] == "恢复默认设置"

        dec_modal = brotli.decompress(bytes(data[modal_start:modal_start + len(comp_modal)])).decode('utf-8')
        assert 'placeholder:"搜索设置..."' in dec_modal
        assert '[["基础设置",' in dec_modal
        log("In-memory self-verification PASSED 100%!", "SUCCESS")

        # 9. Write out binary
        with open(target_app_path, "wb") as f:
            f.write(data)
        log(f"Successfully injected patches into: {target_app_path}", "SUCCESS")
        return True

    except Exception as e:
        log(f"Exception during patch execution: {e}\n{traceback.format_exc()}", "ERROR")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_patch(target)
    sys.exit(0 if success else 1)
