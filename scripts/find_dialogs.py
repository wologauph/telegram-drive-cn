import brotli
import re

with open(r'D:\app\Telegram Drive\app.exe', 'rb') as f:
    data = f.read()

pos = 37871053 + len(b'/assets/DesktopDashboard-9eAxEZHg.js')
dd_js = brotli.decompress(data[pos:pos+70649]).decode('utf-8')

print("Dynamic imports in DesktopDashboard:")
for m in re.finditer(r'import\("([^"]+)"\)', dd_js):
    print(" ", m.group(1))

print("Modal or Dialog components in DesktopDashboard:")
for m in re.finditer(r'<([A-Z][a-zA-Z0-9]*Dialog|[A-Z][a-zA-Z0-9]*Modal)', dd_js):
    print(" ", m.group(1))

# Let's inspect index-BTm7tAhC.js dynamic imports as well
pos_idx = 38352911 + len(b'/assets/index-BTm7tAhC.js')
idx_js = brotli.decompress(data[pos_idx:pos_idx+150165]).decode('utf-8')
print("Dynamic imports in index-BTm7tAhC:")
for m in re.finditer(r'import\("([^"]+)"\)', idx_js):
    print(" ", m.group(1))

print("Modal or Dialog components in index-BTm7tAhC:")
for m in re.finditer(r'<([A-Z][a-zA-Z0-9]*Dialog|[A-Z][a-zA-Z0-9]*Modal)', idx_js):
    print(" ", m.group(1))
