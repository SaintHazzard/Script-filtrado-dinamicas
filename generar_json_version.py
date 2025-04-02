import json
from pathlib import Path

VERSION = "1.0.0"
REPO = "SaintHazzard/Script-filtrado-dinamicas"

nombre_exe = f"consolidado-dinamicas-v{VERSION}.exe"
url = f"https://github.com/{REPO}/releases/download/v{VERSION}/{nombre_exe}"

data = {
    "version": VERSION,
    "url": url
}

with open("version.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ version.json generado con versión {VERSION}")
