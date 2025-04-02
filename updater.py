import requests
import os
import sys
from pathlib import Path

URL_VERSION = "https://raw.githubusercontent.com/SaintHazzard/Script-filtrado-dinamicas/main/version.json"
# se debe cambiar la version en el json tambien
# para que funcione el updater.py
VERSION_LOCAL = "1.0.0"

def verificar_actualizacion():
    try:
        data = requests.get(URL_VERSION).json()
        if data["version"] != VERSION_LOCAL:
            print(f"🔄 Nueva versión disponible: {data['version']}")
            return data["url"]
        else:
            print("✅ Ya tenés la última versión.")
            return None
    except Exception as e:
        print(f"⚠️ Error al buscar actualización: {e}")
        return None

def descargar_actualizacion(url):
    print("⬇️ Descargando nueva versión...")
    r = requests.get(url, stream=True)
    temp_path = Path("main_new.exe")

    with open(temp_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print("✅ Descarga completada.")
    return temp_path

def reemplazar_y_ejecutar(nuevo_exe):
    actual_exe = Path(sys.executable)

    # Eliminar el actual
    os.remove(actual_exe)

    # Renombrar el nuevo como el original
    nuevo_exe.rename(actual_exe)

    print("🚀 Aplicación actualizada. Reiniciando...")
    os.startfile(actual_exe)
    sys.exit()

def main():
    url = verificar_actualizacion()
    if url:
        nuevo_exe = descargar_actualizacion(url)
        reemplazar_y_ejecutar(nuevo_exe)
    else:
        print("👍 No hay actualizaciones.")

if __name__ == "__main__":
    main()
