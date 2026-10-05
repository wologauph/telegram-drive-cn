import brotli
import struct

with open(r'D:\app\Telegram Drive\app.exe', 'rb') as f:
    data = bytearray(f.read())

modal_marker = b'/assets/SettingsModal-DtYCi5g8.js'
start = data.find(modal_marker) + len(modal_marker)
len_val = struct.unpack('<Q', data[38517752:38517760])[0]
dec_modal = brotli.decompress(data[start:start+len_val]).decode('utf-8')

modal_repls = [
    ('["system",bt,"System"]', '["system",bt,"跟随系统"]'),
    ('{defaultValue:"Default"}', '{defaultValue:"默认"}'),
    ('children:"Vault"', 'children:"保险库"'),
    ('children:"Recovery"', 'children:"恢复备份"'),
    ('children:"Protection"', 'children:"加密保护"'),
    ('children:["How it works ",', 'children:["工作原理 ",'),
    ('children:R?"当前会话已解锁":q?"Locked":"Not configured"', 'children:R?"当前会话已解锁":q?"已锁定":"未配置"'),
    ('children:r.vaultRecoveryDrillCompleted?"恢复演练已通过验证":"Action required"', 'children:r.vaultRecoveryDrillCompleted?"恢复演练已通过验证":"需尽快处理"')
]
for o, n in modal_repls:
    assert o in dec_modal, f'Missing in modal: {o}'
    dec_modal = dec_modal.replace(o, n)

comp_modal = brotli.compress(dec_modal.encode('utf-8'), quality=11)
print(f'SettingsModal compressed: {len(comp_modal)} bytes (slot: 27259) - OK:', len(comp_modal) <= 27259)

dd_marker = b'/assets/DesktopDashboard-9eAxEZHg.js'
start_dd = data.find(dd_marker) + len(dd_marker)
len_val_dd = struct.unpack('<Q', data[38517656:38517664])[0]
dec_dd = brotli.decompress(data[start_dd:start_dd+len_val_dd]).decode('utf-8')

dd_repls = [
    ('t?"Why is this file protected?":"How file protection works"', 't?"为什么此文件受到加密保护？":"文件加密保护机制说明"'),
    ('"aria-label":"Close protection explanation"', '"aria-label":"关闭说明"'),
    ('children:"Protection happens on this device before upload. Telegram stores an authenticated encrypted envelope rather than the original file bytes."', 'children:"加密保护在文件上传前于本设备本地完成。Telegram 云端仅存储经身份验证的加密密文信封，绝无原始文件明文字节。"'),
    ('children:"The app verifies integrity before presenting plaintext. Vault keys remain local and can be automatically locked."', 'children:"软件在呈现明文之前会严格校验数据完整性。保险库密钥始终保存在本地，并支持自动锁定。"'),
    ('s.jsx("strong",{className:"text-app-text",children:"Limitations:"})," Telegram cannot recover your key. Protected previews, streaming, third-party WebDAV clients, and share recipients may require the vault to be unlocked or a separate password link."', 's.jsx("strong",{className:"text-app-text",children:"使用限制说明："})," Telegram 官方无法为您找回加密密钥。受保护的预览、流媒体播放、第三方 WebDAV 客户端以及分享接收者可能需要先解锁保险库，或使用独立的密码提取直链。"'),
    ('s.jsx("strong",{className:"text-app-text",children:"Current state:"})," ",r?"The file is protected and its key is not currently available.":t==="encrypted_corrupt"?"Integrity verification failed. The app will not return unauthenticated bytes.":"The file is protected and its key is currently available for this session."', 's.jsx("strong",{className:"text-app-text",children:"当前加密状态："})," ",r?"此文件受保护，当前会话暂未提供其解密密钥。":t==="encrypted_corrupt"?"完整性校验失败。软件绝不会返回未经身份验证的字节。":"此文件受保护，其解密密钥在当前会话中可用。"')
]
for o, n in dd_repls:
    assert o in dec_dd, f'Missing in DD: {o}'
    dec_dd = dec_dd.replace(o, n)

comp_dd = brotli.compress(dec_dd.encode('utf-8'), quality=11)
print(f'DesktopDashboard compressed: {len(comp_dd)} bytes (slot: 75573) - OK:', len(comp_dd) <= 75573)
