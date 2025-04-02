import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from pathlib import Path

def filtrado_detallado(criterio):
    # Cargar facturas filtradas
    ruta_facturas = Path(f"data/{criterio}/consolidado.xlsx")
    if not ruta_facturas.exists():
        print(f"❌ No existe el consolidado: {ruta_facturas}")
        return

    df_facturas = pd.read_excel(ruta_facturas)

    # Seleccionar archivos detalle
    Tk().withdraw()
    archivos = askopenfilenames(
        title="Selecciona los archivos detalle",
        filetypes=[("Excel y CSV", "*.xlsx *.xls *.csv")],
        initialdir="data"
    )
    if not archivos:
        print("⚠️ No seleccionaste archivos detalle.")
        return

    ids_filtrados = df_facturas['NumberId'].astype(str).unique()
    detalle_filtrado = []

    for archivo in archivos:
        print(f"🔍 Procesando detalle: {Path(archivo).name}")
        if archivo.endswith(".csv"):
            df_detalle = pd.read_csv(archivo, sep=';', engine='python')
        else:
            df_detalle = pd.read_excel(archivo)

        df_detalle_filtrado = df_detalle[df_detalle['O_NumberId'].astype(str).isin(ids_filtrados)]
        if not df_detalle_filtrado.empty:
            detalle_filtrado.append(df_detalle_filtrado)

    # Guardar resultado consolidado
    if detalle_filtrado:
        df_consolidado = pd.concat(detalle_filtrado, ignore_index=True)
        salida = Path(f"data/{criterio}/detalle_consolidado.xlsx")
        df_consolidado.to_excel(salida, index=False)
        print(f"✅ Detalle filtrado guardado en: {salida}")
    else:
        print("⚠️ No se encontraron registros detallados para los NumberId filtrados.")
