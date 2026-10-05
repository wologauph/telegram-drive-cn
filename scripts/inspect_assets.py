import brotli
import re

with open(r'D:\app\Telegram Drive\app.exe', 'rb') as f:
    data = f.read()

pattern = rb'(\/?assets\/[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)'
assets = []
for m in re.finditer(pattern, data):
    assets.append((m.start(), m.group().decode()))

assets.sort()
print(f'Total assets found: {len(assets)}')

for i in range(len(assets)):
    pos, name = assets[i]
    m_len = len(name.encode('utf-8'))
    next_pos = assets[i+1][0] if i+1 < len(assets) else pos + 500000
    comp_slice = data[pos+m_len:next_pos]
    try:
        dec = brotli.decompress(comp_slice).decode('utf-8', errors='ignore')
        matches = []
        for word in ['Supporter', 'Lifetime', 'Where your data goes', 'Encrypted settings', 'WebDAV', 'REST API', 'Essentials']:
            if word in dec:
                matches.append(word)
        if matches:
            print(f'Match in {name}: found {matches}')
    except:
        pass
