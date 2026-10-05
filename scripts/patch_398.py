#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Drive v3.9.8 深度全景汉化与免赞助补丁引擎 (Patch Engine v5.0)
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

NOW = datetime.datetime.now()
LATEST_LOG = os.path.join(LOGS_DIR, "latest_run.log")

def log(msg, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {msg}"
    print(formatted)
    with open(LATEST_LOG, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

# =========================================================================
# 1. 313 个官方英文及损坏键位的 100% 纯正简体中文映射字典
# =========================================================================
TRANSLATIONS = {
    "common.app_title": "Telegram Drive",
    "common.start": "开始使用",
    "common.settings": "偏好设置",
    "common.light_mode": "浅色模式",
    "common.dark_mode": "深色模式",
    "common.switch_light": "切换浅色模式",
    "common.switch_dark": "切换深色模式",
    "common.expand_sidebar": "展开侧边栏",
    "common.collapse_sidebar": "折叠侧边栏",
    "common.groups": "文件夹分组",
    "common.all": "全部",
    "common.unassigned": "未分组",
    "common.hide_groups": "隐藏分组",
    "common.show_groups": "显示分组",
    "common.save": "保存",
    "common.create_group": "创建分组",
    "common.edit_group_name": "编辑分组名称",
    "common.new_group_name": "新分组名称",
    "common.theme_color": "主题颜色",
    "common.delete_group": "删除分组",
    "common.enter_group_name": "输入分组名称...",
    "common.hide_groups_desc": "在侧边栏中切换是否显示文件夹分组",

    # 设置分组导航大类 (彻底修复左侧栏英文标题)
    "settings.group_essentials": "基础设置",
    "settings.group_security_privacy": "安全与隐私",
    "settings.group_connections": "连接与同步",
    "settings.group_advanced": "高级网络",
    "settings.group_support": "关于与支持",

    # 选项卡标题修复
    "settings.tab_general": "通用设置",
    "settings.tab_themes": "个性主题",
    "settings.tab_privacy": "安全与隐私",
    "settings.tab_encryption": "端到端加密",
    "settings.tab_sharing": "分享管理",
    "settings.tab_advanced": "高级网络与系统集成",
    "settings.tab_vpn": "网络与 VPN 调优",
    "settings.tab_proxy": "网络代理",
    "settings.tab_webdav": "WebDAV 本地磁盘挂载",
    "settings.tab_about": "关于软件",

    # 赞助者全景翻译 (彻底清除官方损坏乱码)
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

    # 目录自动同步核心
    "settings.tab_sync": "目录自动同步",
    "settings.sync.title": "目录自动同步",
    "settings.sync.description": "自动将本地文件夹与指定的 Telegram 频道保持单向或双向同步。",
    "settings.sync.toggle": "启用目录自动同步",
    "settings.sync.select_folder": "选择本地文件夹",
    "settings.sync.folder_added": "已成功添加同步文件夹",
    "settings.sync.off_by_default": "目录同步默认处于关闭状态",
    "settings.sync.onboarding": "在您主动开启前不会同步任何数据。超过 2GB 的文件将自动跳过，当突发大量文件被删除时将自动暂停同步以保护云端资产。",
    "settings.sync.folder_mapper": "目录映射关系",
    "settings.sync.mapper_description": "将本地文件夹映射到已有的 Telegram 频道。",
    "settings.sync.remove": "移除同步文件夹",
    "settings.sync.add_folder": "添加同步文件夹",
    "settings.sync.select_channel": "选择 Telegram 频道",
    "settings.sync.no_channels": "在创建同步映射之前，请先刷新您的 Telegram 文件夹列表。",

    # 设置视窗各面板
    "settings.rest_api": "REST 本地接口",
    "settings.tab_vpn": "网络与 VPN 调优",
    "settings.transfers": "传输设置",
    "settings.max_uploads_desc": "最大并行上传任务数 (建议设为 1 以确保大文件稳定不丢包)",
    "settings.max_downloads_desc": "最大并行下载任务数",
    "settings.zip_folders_desc": "上传前将整个文件夹打包压缩为 .zip",
    "settings.performance_compatibility": "性能与兼容性",
    "settings.performance_mode_desc": "关闭磨砂毛玻璃与高开销动画，大幅降低 CPU 与显卡占用",
    "settings.language_region": "语言与区域",
    "settings.app_language": "界面语言",
    "settings.choose_language": "选择您的首选界面语言",
    "settings.enable_api_server_desc": "启动后台轻量 API 接口，便于通过脚本或第三方程序管理文件",
    "settings.api_running": "服务正在运行于端口 {{port}}",
    "settings.api_stopped": "仅限本机访问 (127.0.0.1)",
    "settings.api_key_configured": "访问密钥已配置",
    "settings.api_key_unset": "尚未设置访问密钥",
    "settings.regenerate": "重新生成",
    "settings.generate": "生成密钥",
    "settings.api_copy_alert": "请立即复制并妥善保管 — 此密钥关闭后将不再显示",
    "settings.storage": "本地存储与缓存",
    "settings.transcode_cache_desc": "在线播放 HLS 流媒体切片所允许占用的最大磁盘空间",
    "settings.proxy_config": "网络代理配置",
    "settings.enable_proxy_desc": "通过本地代理服务器路由软件网络流量",
    "settings.socks5_desc": "SOCKS5 代理协议 (推荐，性能更优)",
    "settings.host_desc": "本地代理监听地址 (通常为 127.0.0.1)",
    "settings.port_desc": "有效端口范围：1–65535 (如 Clash 默认 7897 或 7890)",
    "settings.optional": "可选",
    "settings.proxy_reconnect_note": "⚠️ 代理设置修改后需要重新连接才能生效。",
    "settings.reconnecting": "正在重新连接代理...",
    "settings.reconnect_now": "立即重新连接",
    "settings.vpn_optimizer": "网络优化器",
    "settings.vpn_mode": "网络长连接优化模式",
    "settings.vpn_mode_desc": "针对高延迟或代理连接深度优化，防止大文件传输途中被掐断",
    "settings.timeout_multiplier": "超时等待倍率",
    "settings.timeout_multiplier_desc": "成倍增加网络请求等待超时时间，显著降低网络抖动报错",
    "settings.retry_attempts": "失败重试次数",
    "settings.retry_attempts_desc": "网络请求中断或失败时的自动重试次数",
    "settings.retry_backoff": "重试退避间隔",
    "settings.base_delay": "基础退避等待",
    "settings.max_delay": "最大退避等待",
    "settings.adaptive_polling": "自适应网络轮询",
    "settings.adaptive_polling_desc": "根据网络状态自动动态调整会话保活与更新轮询间隔",
    "settings.min_interval": "最小轮询间隔",
    "settings.max_interval": "最大轮询间隔",
    "settings.preferred_dc": "首选 Telegram 数据中心",
    "settings.preferred_dc_desc": "优先连接的 Telegram 官方接入点 (自动或固定 DC)",
    "settings.dc_fallback_attempts": "数据中心切换重试",
    "settings.dc_fallback_desc": "当前节点连接失败时尝试备用数据中心的次数",
    "settings.respect_flood": "遵循官方频控等待 (Flood Wait)",
    "settings.respect_flood_desc": "遭遇 Telegram 官方限频时自动休眠等待，绝不强行并发导致封禁",
    "settings.peer_cache_size": "节点缓存容量",
    "settings.peer_cache_desc": "本地缓存的频道与对等实体解析条数",
    "settings.bandwidth_throttle": "传输带宽限制",
    "settings.upload_limit": "上传速度上限",
    "settings.download_limit": "下载速度上限",
    "settings.unlimited": "不限速 (极致全速)",
    "settings.transfer_chunk_size": "传输分片切片大小",
    "settings.chunk_size_desc": "分片大小 (推荐 512 KB，兼具速度与稳定性)",
    "settings.keep_alive": "长连接保活心跳 (Keep-Alive)",
    "settings.keep_alive_desc": "定时发送保活心跳包，彻底防止代理节点在长传长下中因空闲切断连接",
    "settings.off": "关闭",
    "settings.bulk_archive_limit": "批量打包内存上限",
    "settings.bulk_archive_desc": "API 文件批量打包下载时允许占用的最大内存空间",
    "settings.auto_detect_vpn": "自动检测代理状态",
    "settings.vpn_detected": "已检测到网络代理接口",
    "settings.no_vpn_detected": "未检测到代理接口",
    "settings.checking": "正在检测中...",
    "settings.shared_links": "已分享链接 ({{count}})",
    "settings.refresh_links": "刷新链接列表",
    "settings.ip_override": "Tailscale / 局域网 IP 覆盖",
    "settings.ip_override_desc": "复制分享链接时自动将 '127.0.0.1:14201' 替换为此 IP 或域名。",
    "settings.no_active_links": "暂无生效中的分享链接",
    "settings.no_active_links_desc": "在任意文件上右键点击并选择“创建分享链接”即可添加。",
    "settings.protected": "密码保护",
    "settings.public": "公开访问",
    "settings.expired": "已过期",
    "settings.expires_at": "有效期至：{{date}}",
    "settings.never_expires": "永久有效",
    "settings.copy_share_link": "复制分享链接",
    "settings.revoke_link": "撤销此链接",
    "settings.copy_diagnostics": "复制网络诊断信息",
    "settings.reset_defaults": "恢复默认设置",
    "settings.done": "完成保存",
    "settings.auto": "自动",
    "settings.clear_local_cache": "清理本地缓存",
    "settings.clear_local_cache_desc": "清除本地缓存的缩略图、预览文件和临时传输分片",
    "settings.clear_cache_title": "确认清理本地缓存",
    "settings.clear_cache_desc": "此操作将清除所有已缓存的本地预览和临时文件。您在 Telegram 云端的文件绝不会受到任何影响。",
    "settings.clear": "立即清理",
    "settings.cache_cleared": "本地缓存已成功清理",
    "settings.cache_clear_failed": "清理本地缓存失败",
    "settings.clearing": "正在清理中...",
    "settings.transcode_cache": "视频转码缓存",
    "settings.clear_transcode_title": "清除所有转码缓存",
    "settings.clear_transcode_message": "这将删除所有已转码的 HLS 视频变体及缓存的原件。后续若需播放 HLS 将重新转码。",
    "settings.clear_all": "清除全部",
    "settings.failed_prefix": "失败：{{error}}",
    "settings.clear_variants_for": "清除 {{key}} 的所有转码版本",
    "settings.original": "原始文件",
    "settings.no_transcoded_cached": "暂无已缓存的转码视频",
    "settings.updates": "版本更新",
    "settings.check_for_updates": "检查最新版本",
    "settings.check_updates_desc": "检查是否有新的版本可用",
    "settings.update_restart": "更新并重启软件",
    "settings.check_now": "立即检查",
    "settings.update_available_toast": "发现新版本 v{{version}} 可用！",
    "settings.latest_version_toast": "当前已是最新版本",
    "settings.update_prod_only_toast": "检查更新仅在正式版中可用",
    "settings.update_check_failed_toast": "检查更新失败：{{error}}",
    "settings.update_failed_toast": "版本更新失败：{{error}}",
    "settings.load_shares_failed": "加载分享列表失败：{{error}}",
    "settings.revoke_link_title": "撤销分享链接",
    "settings.revoke_link_desc": "确定要撤销此链接吗？撤销后任何人都无法再通过此链接下载该文件。",
    "settings.link_revoked": "分享链接已成功撤销",
    "settings.link_revoke_failed": "撤销分享链接失败：{{error}}",
    "settings.port_range_error": "端口必须在 1024 到 65535 之间",
    "settings.api_server_started": "API 本地服务已启动",
    "settings.api_server_stopped": "API 本地服务已停止",
    "settings.api_update_failed": "更新 API 配置失败：{{error}}",
    "settings.api_port_updated": "API 端口已修改为 {{port}}",
    "settings.api_port_update_failed": "修改端口失败：{{error}}",
    "settings.generate_api_key_title": "生成 API 密钥",
    "settings.regenerate_api_key_desc": "这将作废您当前的 API 密钥并生成新密钥。所有现有自动化集成将立即失效。",
    "settings.generate_api_key_desc": "生成用于 REST API 接口调用的安全认证密钥。",
    "settings.api_key_generated": "API 密钥生成成功",
    "settings.api_key_generate_failed": "生成密钥失败：{{error}}",
    "settings.copy_clipboard_failed": "复制到剪贴板失败",
    "settings.restart_app_toast": "重启软件后此更改将正式生效",
    "settings.offline": "离线",
    "settings.reconnect_success_toast": "已通过新代理设置成功重新连接",
    "settings.reconnect_failed_toast": "重新连接失败 — 请检查代理参数",
    "settings.reconnect_failed_err_toast": "重新连接失败：{{error}}",
    "settings.diagnostics_copied": "诊断报告已成功复制到剪贴板",
    "settings.diagnostics_copy_failed": "复制诊断报告失败：{{error}}",
    "settings.connection_diagnostics": "网络连接诊断",
    "settings.not_tested": "未测试",
    "settings.testing": "正在测试中...",
    "settings.check_ping": "测延迟 (Ping)",
    "settings.excellent": "极佳",
    "settings.good": "良好",
    "settings.slow": "较慢",
    "settings.up_down_since_connected": "本次连接上传 / 下载总流量",
    "settings.shared_files": "已分享文件 ({{count}})",
    "settings.clear_shared_files": "清空所有分享文件",
    "settings.select_app_language": "选择界面语言",
    "settings.clear_all_transcoded_cache": "清除所有转码缓存",
    "settings.socks5_desc_mobile": "SOCKS5 代理 (不支持 MTProto)",
    "settings.http_bridge_desc": "通过本地 SOCKS5 桥接隧道提供 HTTP/HTTPS 代理。",
    "settings.proxy_status_checking": "检测中...",
    "settings.proxy_status_connected": "已连通",
    "settings.proxy_status_unreachable": "不可达",
    "settings.proxy_testing": "正在测试...",
    "settings.test_connection": "测试连通性",
    "settings.proxy_test_success": "代理连接测试成功，通道畅通！",
    "settings.proxy_test_failed": "代理流量测试失败，请检查节点是否可用。",
    "settings.proxy_status_off": "已关闭",
    "settings.live_state": "实时网络状态监听",
    "settings.live_state_desc": "定时检测网络连通性并实时显示延迟",
    "settings.tab_themes": "个性主题",
    "settings.presets": "预设主题",
    "settings.custom_themes": "自定义主题",
    "settings.create_theme": "新建自定义主题",
    "settings.edit_theme": "编辑主题",
    "settings.theme_name": "主题名称",
    "settings.base_mode": "基础模式",
    "settings.delete_theme": "删除主题",
    "settings.delete_theme_confirm": "确定要删除此自定义主题吗？",
    "settings.reset_default": "恢复默认配色",
    "settings.color_bg": "背景色",
    "settings.color_surface": "卡片表面",
    "settings.color_primary": "主强调色",
    "settings.color_secondary": "次强调色",
    "settings.color_text": "主文本色",
    "settings.color_subtext": "次级文本色",
    "settings.tab_webdav": "WebDAV 本地磁盘挂载",
    "settings.webdav_title": "WebDAV 本地磁盘挂载服务",
    "settings.webdav_description": "在 Windows 文件资源管理器、Mac 访客或其他 WebDAV 客户端中像本地硬盘一样挂载浏览 Telegram Drive。",
    "settings.webdav_local_only": "该服务仅监听本机回路 (127.0.0.1)，安全隔离无外网暴露风险。",
    "settings.enable_webdav": "启用 WebDAV 本地挂载服务",
    "settings.webdav_running": "服务正在运行于端口 {{port}}",
    "settings.webdav_stopped": "服务已停止",
    "settings.webdav_port_desc": "本地监听端口 (1024–65535)",
    "settings.webdav_allow_changes": "允许读写修改文件",
    "settings.webdav_allow_changes_desc": "允许挂载的本地客户端上传、重命名、移动和删除未加密文件。关闭此项以保持只读模式以确保安全。",
    "settings.webdav_connection_link": "WebDAV 挂载直链",
    "settings.webdav_link_configured": "专属安全挂载直链已就绪。若遗失可随时重新生成。",
    "settings.webdav_link_unset": "请在启用服务前先生成专属挂载直链。",
    "settings.webdav_copy_alert": "请立即复制并保存 — 该专属直链关闭后将不再显示",
    "settings.webdav_link_generated": "已成功生成 WebDAV 挂载直链",
    "settings.webdav_generate_failed": "生成 WebDAV 直链失败：{{error}}",
    "settings.webdav_update_failed": "更新 WebDAV 设置失败：{{error}}",
    "settings.webdav_port_updated": "WebDAV 端口已更新为 {{port}}",
    "settings.webdav_started": "WebDAV 本地服务已启动",
    "settings.webdav_stopped_toast": "WebDAV 本地服务已关闭",
    "settings.webdav_read_only": "当前权限：只读模式",
    "settings.webdav_changes_enabled": "当前权限：允许读写修改",
    "settings.webdav_last_error": "服务运行异常",
    "settings.webdav_mobile_unavailable": "WebDAV 挂载功能仅在 Windows、macOS 和 Linux 桌面客户端可用。",
    "settings.webdav_regenerate_title": "确认重新生成 WebDAV 直链？"  ,
    "settings.webdav_regenerate_desc": "当前的挂载链接将立即失效。您需要在所有已连接的 WebDAV 客户端中更新为新链接。",
    "settings.webdav_enable_changes_title": "允许通过 WebDAV 修改文件？",
    "settings.webdav_enable_changes_confirm": "已连接的客户端将能够上传、重命名、移动和删除未加密文件。加密文件不受影响。",

    # 文件列表管理
    "files.folder_settings": "文件夹设置",
    "files.download_all": "下载全部文件",
    "files.download_folder": "下载整个文件夹",
    "files.remote_upload": "离线远程上传",
    "files.remote_upload_url": "离线远程上传 (URL 链接)",
    "files.switch_list": "切换为列表视图",
    "files.switch_grid": "切换为网格视图",
    "files.toggle_layout": "切换布局排版",
    "files.download_selected": "下载所选文件",
    "files.move_to": "移动到...",
    "files.move_to_group": "移动到分组",

    # 分享弹窗
    "share.title": "分享文件",
    "share.sharing_file": "正在分享文件",
    "share.password_protection": "设置访问密码保护",
    "share.enter_password": "输入提取密码",
    "share.expiration": "有效期限",
    "share.one_hour": "1 小时",
    "share.one_day": "1 天",
    "share.seven_days": "7 天",
    "share.never": "永久有效",
    "share.custom_hours": "自定义小时数",
    "share.hours_from_now": "小时后过期",
    "share.generate_link": "生成分享直链",
    "share.link_created": "分享链接创建成功！",
    "share.share_via": "分享至...",
    "share.share_externally": "局域网 / Tailscale 外部分享",
    "share.tailscale_help": "如需与同一局域网或 Tailscale 虚拟网内的好友共享，请在下方输入本机的 IP 地址或主机名：",
    "share.done": "完成",

    # 认证向导与帮助
    "auth.desktop_required": "请在桌面客户端中运行",
    "auth.desktop_required_desc": "您当前正在浏览器中查看开发预览页。本程序依赖底层系统与 Rust 运行库，无法在普通浏览器中独立运行。",
    "auth.open_window_prompt": "请直接从系统任务栏或托盘打开 Telegram Drive 窗口继续使用。",
    "auth.too_many_requests": "操作过于频繁 (Too Many Requests)",
    "auth.flood_wait_msg": "Telegram 官方服务器已对当前操作临时限频。",
    "auth.please_wait": "请耐心等待倒计时结束后再试。",
    "auth.timer_reset_warning": "切勿强行关闭或重启软件，否则等待计时将被重置重新计算。",
    "auth.api_credentials": "官方 API 开发者凭据",
    "auth.api_id": "API ID",
    "auth.api_hash": "API Hash",
    "auth.configure": "配置并保存",
    "auth.how_to_get_credentials": "如何免费获取我的 API 凭据？",
    "auth.dev_mode": "开发者模式",
    "auth.phone_number": "手机号码",
    "auth.qr_code": "扫码登录",
    "auth.continue": "继续",
    "auth.back_to_config": "返回配置",
    "auth.scan_qr": "使用 Telegram 手机 App 扫码登录",
    "auth.qr_instructions": "打开手机 Telegram > 设置 > 设备 > 关联桌面设备",
    "auth.waiting_for_scan": "等待扫码中...",
    "auth.refresh_qr": "刷新二维码",
    "auth.telegram_code": "Telegram 验证码",
    "auth.change_phone": "更换手机号码",
    "auth.two_factor_enabled": "您的账户已开启两步验证。请输入您的云端两步密码继续。",
    "auth.cloud_password": "两步验证云端密码",
    "auth.password_placeholder": "输入您的两步验证密码",
    "auth.back_to_code": "返回验证码输入",
    "auth.donate": "赞助支持",
    "auth.getting_started": "新手使用指南",
    "auth.close_help": "关闭帮助",
    "auth.privacy_note": "您的登录凭据直接加密保存在本地设备中，绝不经由任何第三方服务器中转。所有数据直接与 Telegram 官方服务器加密传输。",

    # 同步状态与冲突
    "sync.status.disabled": "目录自动同步已停用",
    "sync.status.syncing": "目录正在自动同步中...",
    "sync.status.synced": "所有目录均已同步至最新",
    "sync.status.conflicts": "目录同步需要您处理冲突",
    "sync.conflict.title": "检测到文件同步冲突",
    "sync.conflict.keep_local": "保留本地版本",
    "sync.conflict.keep_remote": "保留云端版本",
    "sync.conflict.keep_both": "双版本同时保留",
    "sync.error.mass_deletion": "同步保护暂停：云端检测到大量文件被删除。",

    # 赞助拦截纯净文案
    "ads.sponsored": "赞助内容",
    "ads.sponsor_message": "来自赞助商的一则消息",
    "ads.sponsor_support_desc": "感谢您的理解与支持，赞助使 Telegram Drive 得以永久免费维护。",
    "ads.continue_to_files": "直接前往我的云盘",
    "ads.browser_note": "赞助页面将在系统默认浏览器中打开。该提示仅在首次展示一次。",
    "ads.close_ad": "关闭提示",
    "supporter_offer.price": "$5"
}

# =========================================================================
# 2. SettingsModal.tsx 硬编码替换规则
# =========================================================================
MODAL_REPLACEMENTS = [
    ('placeholder:"Search settings"', 'placeholder:"搜索设置..."'),
    ('[["Essentials",', '[["基础设置",'),
    ('["Security & Privacy",', '["安全与隐私",'),
    ('["Connections",', '["连接与同步",'),
    ('["Advanced",', '["高级网络",'),
    ('["Support",', '["关于与支持",'),
    (',"General transfers language updates"]', ',"通用设置 传输速度 语言切换"]'),
    (',"Appearance colors themes"]', ',"界面外观 主题配色 浅色深色"]'),
    (',"Privacy telemetry crash reports consent"]', ',"隐私保护 崩溃报告 同意选项"]'),
    (',"Encryption vault security auto lock"]', ',"端到端加密 保险库 自动加锁"]'),
    (',"Folder sync local directories Telegram channels"]', ',"目录自动同步 本地文件夹 频道映射"]'),
    (',"Sharing links local server"]', ',"分享链接 本地直链服务"]'),
    (',"REST API proxy VPN WebDAV network integration Finder token port"]', ',"REST 本地接口 代理设置 VPN 网络优化 WebDAV 挂载"]'),
    (',"About diagnostics version updates"]', ',"关于软件 连接诊断 版本更新"]'),
    ('children:"Advanced"', 'children:"高级网络与系统集成"'),
    ('children:"Power-user connections are grouped here so everyday settings stay calm and focused. Use the settings search to find any option by name."', 'children:"面向高阶玩家的连接与集成选项聚合于此，让日常设置保持清爽专注。您也可以使用顶部的搜索框快速定位任何选项。"'),
    ('["REST API","Local automation endpoint and API key"', '["REST 本地接口","本地自动化接口端点与 API 密钥"'),
    ('["WebDAV","Finder and file-manager access"', '["WebDAV 本地磁盘挂载","文件资源管理器及本地虚拟盘访问"'),
    ('["Proxy","SOCKS5 and HTTP bridge settings"', '["网络代理 (Proxy)","SOCKS5 代理及 HTTP 桥接配置"'),
    ('["VPN & network","Retries, bandwidth, and data-center tuning"', '["网络与 VPN 调优","重试机制、带宽限制与 Telegram 数据中心调优"'),
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
    ('title:"Before enabling WebDAV access"', 'title:"开启 WebDAV 本地挂载须知"'),
    ('children:"Use WebDAV, not SMB."', 'children:"请使用 WebDAV 协议挂载，不支持 SMB。"'),
    ('"Understand WebDAV permissions"', '"了解 WebDAV 权限范围"'),
    ('title:"Before enabling REST access"', 'title:"开启 REST 本地自动化须知"'),
    ('"Understand REST permissions"', '"了解 REST 权限范围"'),
    ('confirmText:"I understand — enable"', 'confirmText:"我已充分理解 — 立即开启"'),
    ('"aria-label":"Close local access explanation"', '"aria-label":"关闭说明"'),
    ('title:"Copy to clipboard"', 'title:"复制到剪贴板"'),
    ('"Periodically check connectivity and display latency"', '"定时检测网络连通性并显示延迟"'),
]

# =========================================================================
# 3. HelpCenterDialog.tsx 常见问题替换
# =========================================================================
HELP_REPLACEMENTS = [
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

# =========================================================================
# 4. DesktopDashboard.tsx 界面与弹窗切除
# =========================================================================
DD_REPLACEMENTS = [
    ('children:"This folder is empty"', 'children:"此文件夹为空"'),
    ('children:"Drag and drop files here, or click the button below to upload from your computer."', 'children:"将文件拖拽至此处，或点击下方按钮从电脑上传。"'),
    ('children:["Tip: Use ",', 'children:["提示：使用 ",'),
    ('" to search"]', '" 快速搜索"]'),
    ('children:s.jsx("span",{children:"Used this week:"})', 'children:s.jsx("span",{children:"本周已用流量:"})'),
    ('body:"Saved Messages is your home storage. Telegram Drive reads and writes files directly through your Telegram session."', 'body:"我的云盘 (收藏夹) 是您的基础存储空间。Telegram Drive 直接通过您的 Telegram 官方会话读写文件。"'),
    ('[s.jsx(oa,{className:"h-4 w-4 text-app-accent"}),"Create a folder"]', '[s.jsx(oa,{className:"h-4 w-4 text-app-accent"}),"创建文件夹"]'),
    ('placeholder:"e.g. Project files"', 'placeholder:"例如：影视大片、项目资料、日常相册..."'),
    ('children:"This creates a private Telegram channel that Telegram Drive presents as a folder. Its files remain in your Telegram account."', 'children:"此操作将在您的 Telegram 账户中创建一个私密频道，并在本软件中作为文件夹呈现。文件将完整保存在您的电报账户中。"'),
    ('children:a?"Creating…":"Create private folder"', 'children:a?"正在创建…":"创建私密文件夹"'),
    ('className:"h-3.5 w-3.5 text-app-text-secondary"}),"Keyboard shortcuts"]', 'className:"h-3.5 w-3.5 text-app-text-secondary"}),"快捷键指南"]'),
    ('className:"h-3.5 w-3.5 text-app-text-secondary"}),"Help & FAQ"]', 'className:"h-3.5 w-3.5 text-app-text-secondary"}),"使用帮助与常见问题"]'),
    ('[s.jsx(xl,{className:"h-4 w-4 text-app-accent"}),"Keyboard shortcuts"]', '[s.jsx(xl,{className:"h-4 w-4 text-app-accent"}),"快捷键指南"]'),
    ('"aria-label":"Close shortcut reference"', '"aria-label":"关闭快捷键指南"'),
    ('["⌘/Ctrl F","Search files"]', '["⌘/Ctrl F","快速搜索文件"]'),
    ('["⌘/Ctrl A","Select all files"]', '["⌘/Ctrl A","全选所有文件"]'),
    ('["Enter","Open the selected file"]', '["Enter","打开选中的文件"]'),
    ('["F2","Rename the selected file"]', '["F2","重命名选中的文件"]'),
    ('["⌘/Ctrl D","Download selection"]', '["⌘/Ctrl D","下载选中文件"]'),
    ('["⌘/Ctrl ⇧ S","Share selection"]', '["⌘/Ctrl ⇧ S","生成分享链接"]'),
    ('["Delete / Backspace","Delete selection"]', '["Delete / Backspace","删除选中文件"]'),
    ('["Esc","Close the active dialog or clear selection"]', '["Esc","关闭弹窗或取消全选"]'),
    ('["?","Show this shortcut reference"]', '["?","显示快捷键参考指南"]'),
    ('children:"All Telegram Drive folders"', 'children:"所有云盘文件夹"'),
    ('children:"All transfers complete"', 'children:"所有传输任务已完成"'),
    ('children:"All types"', 'children:"全部文件类型"'),
    ('children:"Archives"', 'children:"压缩包文件"'),
    ('children:"Audio"', 'children:"音频与音乐"'),
    ('children:"Cancel all"', 'children:"取消全部传输"'),
    ('children:"Clear finished"', 'children:"清除已完成任务"'),
    ('children:"Documents"', 'children:"办公与电子书"'),
    ('children:"Downloads"', 'children:"下载队列"'),
    ('children:"Uploads"', 'children:"上传队列"'),
    ('children:"Images"', 'children:"图片与相册"'),
    ('children:"Videos"', 'children:"视频大片"'),
    ('children:"Other"', 'children:"其他文件"'),
    ('children:"Last 7 days"', 'children:"最近 7 天"'),
    ('children:"Last 30 days"', 'children:"最近 30 天"'),
    ('children:"Last year"', 'children:"过去一年"'),
    ('children:"Under 10 MB"', 'children:"10 MB 以下"'),
    ('children:"Reset filters"', 'children:"重置所有筛选"'),
    ('children:"Sort files"', 'children:"文件排序"'),
    ('children:"Error loading files"', 'children:"文件列表加载失败"'),
    ('children:"Generating share links..."', 'children:"正在生成分享直链..."'),
    ('children:"Understood"', 'children:"我已知晓"'),
]

# =========================================================================
# 5. index-BTm7tAhC.js 开机自检与电报握手
# =========================================================================
INDEX_REPLACEMENTS = [
    ('children:["How should we store ",a.count===1?"this file":`these ${a.count} files`,"?"]', 'children:["请选择",a.count===1?"此文件":`这 ${a.count} 个文件`,"的存储模式："]'),
    ('children:"You can keep the original file, or protect it with Telegram Drive encryption before upload."', 'children:"您可以直接原样上传，或在上传前使用专属加密保护。"'),
    ('children:"Store"', 'children:"普通极速存储"'),
    ('children:"Upload normally for maximum compatibility and easy sharing."', 'children:"正常上传，兼具最高兼容性与极速分享。"'),
    ('children:"Store & protect"', 'children:"端到端加密存储"'),
    ('children:"Encrypt before upload using your configured protection settings."', 'children:"上传前通过端到端密钥加密，云端无人能偷窥。"'),
    ('label:"Checking local services",detail:"Verifying the database and streaming runtime…"', 'label:"检查本地服务环境",detail:"正在校验本地数据库与流媒体运行库…"'),
    ('label:"Restoring your session",detail:"Reading the saved Telegram account…"', 'label:"正在恢复登录会话",detail:"正在读取已保存的 Telegram 账户凭证…"'),
    ('label:"Ready to sign in",detail:"The saved session needs attention."', 'label:"准备就绪，请登录",detail:"保存的会话需要重新验证。"'),
    ('label:"Ready to sign in",detail:"No saved session was found."', 'label:"准备就绪，请登录",detail:"未检测到已保存的会话，请先登录。"'),
    ('label:"Starting Telegram",detail:"Initializing the secure desktop client…"', 'label:"正在启动 Telegram 核心服务",detail:"正在初始化安全桌面客户端…"'),
    ('label:"Checking your account",detail:"Confirming the session with Telegram…"', 'label:"正在验证电报账户",detail:"正在与 Telegram 官方服务器确认会话…"'),
    ('label:"Checking sponsor access",detail:"Finishing your local access checks…"', 'label:"正在完成安全校验",detail:"正在完成本地环境与权限检测…"'),
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
            s["keepAliveIntervalSec"] = 30     # 30秒长连接心跳，防大文件断流
            s["maxConcurrentUploads"] = 1       # 单并发，大文件独占稳定通道
            s["maxConcurrentDownloads"] = 2
            s["retryAttempts"] = 5              # 失败自动重试5次
            s["performanceMode"] = True         # 开启低功耗性能模式
            s["floodWaitRespect"] = True
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log("Aligned settings.json: language='zh-CN', autoUpdate=False, keepAlive=30s, maxUploads=1", "SUCCESS")
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
                "keep_alive_interval_sec": 30,
                "bulk_archive_max_mb": 0,
                "adaptive_polling": True
            }
        }
        with open(net_file, "w", encoding="utf-8") as f:
            json.dump(net_cfg, f, indent=2, ensure_ascii=False)
        log("Aligned network_settings.json: SOCKS5 127.0.0.1:7897, keep_alive=30s, chunk=512KB", "SUCCESS")
    except Exception as e:
        log(f"Failed to align network_settings.json: {e}", "WARNING")

def run_patch():
    target_app_path = r"D:\app\Telegram Drive\app.exe"
    if not os.path.exists(target_app_path):
        log(f"Target executable not found at: {target_app_path}", "ERROR")
        return False

    bak = target_app_path + ".v398.bak"
    if not os.path.exists(bak):
        shutil.copyfile(target_app_path, bak)
        log(f"Created pristine backup: {bak}", "CLEAN")

    log(f"Loading binary from pristine backup: {bak}", "INFO")
    with open(bak, "rb") as f:
        data = bytearray(f.read())
    log(f"Loaded binary into memory: {len(data)} bytes", "INFO")

    # 1. Patch Slice 1: zh-CN-Cp_y0Z7o.json
    zh_marker = b"/assets/zh-CN-Cp_y0Z7o.json"
    zh_pos = data.find(zh_marker)
    if zh_pos == -1:
        raise RuntimeError("zh-CN marker not found in binary!")
    zh_slot_len = 18493
    zh_table_entry = 38518680
    zh_start = zh_pos + len(zh_marker)

    raw_zh_bytes = brotli.decompress(bytes(data[zh_start:zh_start + zh_slot_len]))
    zh_dict = json.loads(raw_zh_bytes.decode('utf-8'))
    
    # 覆盖所有 313 个翻译
    for k, v in TRANSLATIONS.items():
        parts = k.split('.')
        cur = zh_dict
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = v

    zh_encoded = json.dumps(zh_dict, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    comp_zh = brotli.compress(zh_encoded, quality=11)
    log(f"[1/6] Compressed zh-CN: {len(zh_encoded)} raw -> {len(comp_zh)} brotli bytes (slot: {zh_slot_len})", "INFO")
    if len(comp_zh) > zh_slot_len:
        raise ValueError(f"zh-CN exceeds slot: {len(comp_zh)} > {zh_slot_len}")

    data[zh_start:zh_start + len(comp_zh)] = comp_zh
    data[zh_start + len(comp_zh):zh_start + zh_slot_len] = b'\x00' * (zh_slot_len - len(comp_zh))
    data[zh_table_entry:zh_table_entry + 8] = struct.pack('<Q', len(comp_zh))
    log(f"[1/6] zh-CN table entry updated at {zh_table_entry}: len={len(comp_zh)}", "SUCCESS")

    # 2. Patch Slice 2: SettingsModal-DtYCi5g8.js
    modal_marker = b"/assets/SettingsModal-DtYCi5g8.js"
    modal_pos = data.find(modal_marker)
    if modal_pos == -1:
        raise RuntimeError("SettingsModal marker not found!")
    modal_slot_len = 27259
    modal_table_entry = 38517752
    modal_start = modal_pos + len(modal_marker)

    raw_modal_js = brotli.decompress(bytes(data[modal_start:modal_start + modal_slot_len])).decode('utf-8')
    mod_modal = raw_modal_js
    for old, new in MODAL_REPLACEMENTS:
        if old in mod_modal:
            mod_modal = mod_modal.replace(old, new)
        else:
            log(f"[WARNING] Modal replacement pattern not found: {old[:35]}", "WARNING")

    comp_modal = brotli.compress(mod_modal.encode('utf-8'), quality=11)
    log(f"[2/6] Compressed SettingsModal: {len(mod_modal)} raw -> {len(comp_modal)} brotli bytes (slot: {modal_slot_len})", "INFO")
    if len(comp_modal) > modal_slot_len:
        raise ValueError(f"SettingsModal exceeds slot: {len(comp_modal)} > {modal_slot_len}")

    data[modal_start:modal_start + len(comp_modal)] = comp_modal
    data[modal_start + len(comp_modal):modal_start + modal_slot_len] = b'\x00' * (modal_slot_len - len(comp_modal))
    data[modal_table_entry:modal_table_entry + 8] = struct.pack('<Q', len(comp_modal))
    log(f"[2/6] SettingsModal table entry updated at {modal_table_entry}: len={len(comp_modal)}", "SUCCESS")

    # 3. Patch Slice 3: HelpCenterDialog-Cmcett2L.js
    help_marker = b"/assets/HelpCenterDialog-Cmcett2L.js"
    help_pos = data.find(help_marker)
    if help_pos == -1:
        raise RuntimeError("HelpCenterDialog marker not found!")
    help_slot_len = 1277
    help_table_entry = 38518392
    help_start = help_pos + len(help_marker)

    raw_help_js = brotli.decompress(bytes(data[help_start:help_start + help_slot_len])).decode('utf-8')
    mod_help = raw_help_js
    for old, new in HELP_REPLACEMENTS:
        if old in mod_help:
            mod_help = mod_help.replace(old, new)

    comp_help = brotli.compress(mod_help.encode('utf-8'), quality=11)
    log(f"[3/6] Compressed HelpCenter: {len(mod_help)} raw -> {len(comp_help)} brotli bytes (slot: {help_slot_len})", "INFO")
    if len(comp_help) > help_slot_len:
        raise ValueError(f"HelpCenter exceeds slot: {len(comp_help)} > {help_slot_len}")

    data[help_start:help_start + len(comp_help)] = comp_help
    data[help_start + len(comp_help):help_start + help_slot_len] = b'\x00' * (help_slot_len - len(comp_help))
    data[help_table_entry:help_table_entry + 8] = struct.pack('<Q', len(comp_help))
    log(f"[3/6] HelpCenter table entry updated at {help_table_entry}: len={len(comp_help)}", "SUCCESS")

    # 4. Patch Slice 4: DesktopDashboard-9eAxEZHg.js
    dd_marker = b"/assets/DesktopDashboard-9eAxEZHg.js"
    dd_pos = data.find(dd_marker)
    if dd_pos == -1:
        raise RuntimeError("DesktopDashboard marker not found!")
    dd_slot_len = 75573
    dd_table_entry = 38517656
    dd_start = dd_pos + len(dd_marker)

    raw_dd_js = brotli.decompress(bytes(data[dd_start:dd_start + dd_slot_len])).decode('utf-8')
    mod_dd = raw_dd_js
    for old, new in DD_REPLACEMENTS:
        if old in mod_dd:
            mod_dd = mod_dd.replace(old, new)

    # 赞助弹窗与横幅永久封杀
    if 'C=!e&&Ji(a);' in mod_dd:
        mod_dd = mod_dd.replace('C=!e&&Ji(a);', 'C=!1;/*===*/')
        log("[KILL] Neutralized sponsor banner in DesktopDashboard (C=!1)", "CLEAN")
    elif 'C=!e&&Ji(a)' in mod_dd:
        mod_dd = mod_dd.replace('C=!e&&Ji(a)', 'C=!1/*===*/')
        log("[KILL] Neutralized sponsor banner in DesktopDashboard (C=!1)", "CLEAN")

    dialog_target = 'return s.jsx("div",{className:"fixed inset-0 z-[260]'
    if dialog_target in mod_dd:
        mod_dd = mod_dd.replace(dialog_target, 'return null;/*d*/s.jsx("div",{className:"fixed inset-0 z-[260]')
        log("[KILL] Neutralized supporter dialog in DesktopDashboard (return null)", "CLEAN")

    comp_dd = brotli.compress(mod_dd.encode('utf-8'), quality=11)
    log(f"[4/6] Compressed DesktopDashboard: {len(mod_dd)} raw -> {len(comp_dd)} brotli bytes (slot: {dd_slot_len})", "INFO")
    if len(comp_dd) > dd_slot_len:
        raise ValueError(f"DesktopDashboard exceeds slot: {len(comp_dd)} > {dd_slot_len}")

    data[dd_start:dd_start + len(comp_dd)] = comp_dd
    data[dd_start + len(comp_dd):dd_start + dd_slot_len] = b'\x00' * (dd_slot_len - len(comp_dd))
    data[dd_table_entry:dd_table_entry + 8] = struct.pack('<Q', len(comp_dd))
    log(f"[4/6] DesktopDashboard table entry updated at {dd_table_entry}: len={len(comp_dd)}", "SUCCESS")

    # 5. Patch Slice 5: index-BTm7tAhC.js
    idx_marker = b"/assets/index-BTm7tAhC.js"
    idx_pos = data.find(idx_marker)
    if idx_pos == -1:
        raise RuntimeError("index marker not found!")
    idx_slot_len = 162044
    idx_table_entry = 38518840
    idx_start = idx_pos + len(idx_marker)

    raw_idx_js = brotli.decompress(bytes(data[idx_start:idx_start + idx_slot_len])).decode('utf-8')
    mod_idx = raw_idx_js
    for old, new in INDEX_REPLACEMENTS:
        if old in mod_idx:
            mod_idx = mod_idx.replace(old, new)

    # 封杀赞助校验函数
    if 'function uM(n){return n.state!=="loading"&&!n.ad_free}' in mod_idx:
        mod_idx = mod_idx.replace('function uM(n){return n.state!=="loading"&&!n.ad_free}', 'function uM(n){return!1/*====================*/&&!n.ad_free}')
        log("[KILL] Disabled uM sponsor check in index-BTm7tAhC.js", "CLEAN")

    if 'function cM(n){return n.state==="inactive"&&!n.ad_free&&!n.recovery_code_saved}' in mod_idx:
        mod_idx = mod_idx.replace('function cM(n){return n.state==="inactive"&&!n.ad_free&&!n.recovery_code_saved}', 'function cM(n){return!1/*==========================================*/&&!n.ad_free}')
        log("[KILL] Disabled cM sponsor check in index-BTm7tAhC.js", "CLEAN")

    comp_idx = brotli.compress(mod_idx.encode('utf-8'), quality=11)
    log(f"[5/6] Compressed index JS: {len(mod_idx)} raw -> {len(comp_idx)} brotli bytes (slot: {idx_slot_len})", "INFO")
    if len(comp_idx) > idx_slot_len:
        raise ValueError(f"index exceeds slot: {len(comp_idx)} > {idx_slot_len}")

    data[idx_start:idx_start + len(comp_idx)] = comp_idx
    data[idx_start + len(comp_idx):idx_start + idx_slot_len] = b'\x00' * (idx_slot_len - len(comp_idx))
    data[idx_table_entry:idx_table_entry + 8] = struct.pack('<Q', len(comp_idx))
    log(f"[5/6] index table entry updated at {idx_table_entry}: len={len(comp_idx)}", "SUCCESS")

    # 6. Patch Slice 6: zh-TW-Dub-WoN6.json
    tw_marker = b"/assets/zh-TW-Dub-WoN6.json"
    tw_pos = data.find(tw_marker)
    if tw_pos == -1:
        raise RuntimeError("zh-TW marker not found!")
    tw_slot_len = 18633
    tw_table_entry = 38517848
    tw_start = tw_pos + len(tw_marker)

    raw_tw = brotli.decompress(bytes(data[tw_start:tw_start + tw_slot_len])).decode('utf-8')
    mod_tw = raw_tw.replace('"saved_messages":"Saved Messages"', '"saved_messages":"我的雲端硬碟 (收藏夾)"')
    mod_tw = mod_tw.replace('"disabled":"Folder Sync disabled"', '"disabled":"目錄自動同步已停用"')
    mod_tw = mod_tw.replace('"syncing":"Folder Sync running"', '"syncing":"目錄同步正在運行中..."')
    mod_tw = mod_tw.replace('"synced":"Folders synced"', '"synced":"所有資料夾均已同步最新"')
    mod_tw = mod_tw.replace('"conflicts":"Folder Sync needs attention"', '"conflicts":"目錄同步需要您處理衝突"')

    comp_tw = brotli.compress(mod_tw.encode('utf-8'), quality=11)
    log(f"[6/6] Compressed zh-TW: {len(mod_tw)} raw -> {len(comp_tw)} brotli bytes (slot: {tw_slot_len})", "INFO")
    if len(comp_tw) > tw_slot_len:
        raise ValueError(f"zh-TW exceeds slot: {len(comp_tw)} > {tw_slot_len}")

    data[tw_start:tw_start + len(comp_tw)] = comp_tw
    data[tw_start + len(comp_tw):tw_start + tw_slot_len] = b'\x00' * (tw_slot_len - len(comp_tw))
    data[tw_table_entry:tw_table_entry + 8] = struct.pack('<Q', len(comp_tw))
    log(f"[6/6] zh-TW table entry updated at {tw_table_entry}: len={len(comp_tw)}", "SUCCESS")

    # 边界断言自检
    assert data[zh_start + zh_slot_len] == 0x2f, "zh-CN boundary corrupted!"
    assert data[modal_start + modal_slot_len] == 0x2f, "SettingsModal boundary corrupted!"
    assert data[help_start + help_slot_len] == 0x2f, "HelpCenter boundary corrupted!"
    assert data[dd_start + dd_slot_len] == 0x2f, "DesktopDashboard boundary corrupted!"
    assert data[idx_start + idx_slot_len] == 0x2f, "index boundary corrupted!"
    assert data[tw_start + tw_slot_len] == 0x2f, "zh-TW boundary corrupted!"

    # 回读解压自检断言
    test_zh = json.loads(brotli.decompress(bytes(data[zh_start:zh_start + len(comp_zh)])).decode('utf-8'))
    assert test_zh["settings"]["tab_sync"] == "目录自动同步", "zh-CN verification failed!"
    assert test_zh["settings"]["sync"]["title"] == "目录自动同步", "zh-CN sync title verification failed!"
    assert test_zh["settings"]["keep_alive"] == "长连接保活心跳 (Keep-Alive)", "zh-CN keep_alive failed!"
    log("All 6 slices in-memory self-verification & boundary checks PASSED 100%!", "SUCCESS")

    # 写入二进制文件
    with open(target_app_path, "wb") as f:
        f.write(data)
    log(f"Successfully injected all 6 patches into: {target_app_path}", "SUCCESS")

    # 同步工具库
    tool_lib_target = r"D:\我的电脑工具库\03_系统与网络法宝\Telegram-Drive-CN\Telegram-Drive-CN.exe"
    if os.path.exists(os.path.dirname(tool_lib_target)):
        shutil.copyfile(target_app_path, tool_lib_target)
        log(f"Synchronized patched v3.9.8 binary to Tool Library: {tool_lib_target}", "SUCCESS")

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
