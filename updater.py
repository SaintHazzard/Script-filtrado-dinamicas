import requests
import os
import sys
from pathlib import Path

URL_VERSION = "https://raw.githubusercontent.com/SaintHazzard/Script-filtrado-dinamicas/main/version.json"
VERSION_LOCAL = "1.0.1"

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
    print("⬇️ Descargando nueva versión...")
    nombre_exe = f"consolidado-dinamicas-v{version}.exe"
    temp_path = Path(nombre_exe)

    r = requests.get(url, stream=True)
    with open(temp_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Descarga completada: {nombre_exe}")
    return temp_path

def reemplazar_y_ejecutar(nuevo_exe):
    actual_exe = Path(sys.executable)
    print(f"📄 Simulación: Reemplazar {actual_exe} con {nuevo_exe}")
    # os.remove(actual_exe)
    # nuevo_exe.rename(actual_exe)
    # os.startfile(actual_exe)
    # # Eliminar el actual
    # os.remove(actual_exe)
    # # Renombrar el nuevo como el original
    # nuevo_exe.rename(actual_exe)
    # print("🚀 Aplicación actualizada. Reiniciando...")
    # os.startfile(actual_exe)
    sys.exit()

def main():
    data = verificar_actualizacion()
    if data:
        nuevo_exe = descargar_actualizacion(data["url"], data["version"])
        reemplazar_y_ejecutar(nuevo_exe)
    else:
        print("👍 No hay actualizaciones.")

if __name__ == "__main__":
    main()
