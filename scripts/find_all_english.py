import brotli
import re

with open(r'D:\app\Telegram Drive\app.exe', 'rb') as f:
    data = f.read()

pos = 37949039 + len(b'/assets/SettingsModal-DtYCi5g8.js')
modal = brotli.decompress(data[pos:pos+25738]).decode('utf-8')

print("All English sentences in SettingsModal:")
matches = re.findall(r'"([A-Z][^"]{15,180})"', modal)
for m in sorted(set(matches)):
    if ' ' in m and not m.startswith('http') and not m.startswith('quiet') and not m.startswith('fixed'):
        print("  -", m)
