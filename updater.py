import sys
import requests
from pathlib import Path

URL_VERSION = "https://raw.githubusercontent.com/SaintHazzard/Script-filtrado-dinamicas/main/version.json"
VERSION_LOCAL = "1.0.2"

def verificar_actualizacion():
    try:
        resp = requests.get(URL_VERSION)
        data = resp.json()
        if data["version"] != VERSION_LOCAL:
            print(f"🔄 Nueva versión disponible: {data['version']}")
            return data
        else:
            print("✅ Ya tenés la última versión.")
            return None
    except Exception as e:
        print(f"⚠️ Error al buscar actualización: {e}")
        return None

def descargar_actualizacion(url, version):
    print(f"⬇️ Descargando nueva versión: v{version}...")
    nombre_exe = f"consolidado-dinamicas-v{version}.exe"
    temp_path = Path(nombre_exe)

    r = requests.get(url, stream=True)
    with open(temp_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Descarga completada: {nombre_exe}")
    return temp_path

def main():
    data = verificar_actualizacion()
    if data:
        descargar_actualizacion(data["url"], data["version"])
        print("ℹ️ La nueva versión fue descargada. Cerrar esta y abrir la nueva manualmente.")
        input("🔘 Presioná Enter para salir...")
        sys.exit()
    else:
        print("👍 No hay actualizaciones.")
        input("🔘 Presioná Enter para cerrar...")


if __name__ == "__main__":
    main()
