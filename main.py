from pathlib import Path
import pandas as pd
import fileSelector
import re
import updater

updater.main()

def filtrar_observacion(df, criterio):
    """Filtra registros donde al menos uno de los términos en 'Observation' coincida con el criterio."""
    if 'Observation' not in df.columns:
        return pd.DataFrame()

    def cumple_condicion(obs):
        if pd.isna(obs):
            return False
        partes = [o.strip().lower() for o in str(obs).split(',')]
        return criterio.lower() in partes

    return df[df['Observation'].apply(cumple_condicion)]



def procesar_archivos(archivos, criterio):
    carpeta_base = Path("data") / criterio
    carpeta_base.mkdir(parents=True, exist_ok=True)
    consolidado = []

    for archivo in archivos:
        nombre = Path(archivo).stem
        print(f"🔍 Procesando: {nombre}")

        if archivo.endswith(".csv"):
            df = pd.read_csv(archivo, sep=';', engine='python')
        else:
            df = pd.read_excel(archivo)

        df_filtrado = filtrar_observacion(df, criterio)
        if not df_filtrado.empty:
            salida = carpeta_base / f"{nombre}_filtrado.xlsx"  
            df_filtrado.to_excel(salida, index=False)
            consolidado.append(df_filtrado)
            print(f"✅ {len(df_filtrado)} registros filtrados guardados en: {salida}")
        else:
            print(f"⚠️ No se encontraron registros en {nombre}")

    # Guardar consolidado
    if consolidado:
        df_total = pd.concat(consolidado, ignore_index=True)
        salida_total = carpeta_base / "consolidado.xlsx"
        df_total.to_excel(salida_total, index=False)
        print(f"📄 Consolidado guardado en: {salida_total}")
    else:
        print("⚠️ No hubo registros para consolidar.")
        
def procesar_archivos_detallados(criterio,descuento_minimo=0):
    """Procesa archivos detallados y filtra por 'Observation'."""
    # Cargar facturas filtradas
    ruta_facturas = Path(f"data/{criterio}/consolidado.xlsx")
    if not ruta_facturas.exists():
        print(f"❌ No existe el consolidado: {ruta_facturas}")
        return

    df_facturas = pd.read_excel(ruta_facturas)

    # Seleccionar archivos detalle
    archivos = fileSelector.seleccionar_archivos()
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

        df_detalle_filtrado = df_detalle[
            (df_detalle['O_NumberId'].astype(str).isin(ids_filtrados)) &
            (df_detalle['DiscountPercentage'].fillna(0) > descuento_minimo)
        ]
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


def cruzar_con_info_adicional(criterio):
    """Cruza los registros detallados filtrados con la información adicional."""
    ruta_detalle = Path(f"data/{criterio}/detalle_consolidado.xlsx")
    if not ruta_detalle.exists():
        print(f"❌ No existe el archivo de detalle: {ruta_detalle}")
        return

    df_detalle = pd.read_excel(ruta_detalle)

    # Seleccionar archivo adicional
   
    archivo_extra = fileSelector.seleccionar_archivo()
    if not archivo_extra:
        print("⚠️ No seleccionaste archivo adicional.")
        return

    df_info = pd.read_excel(archivo_extra, header=1)


    df_info.columns = df_info.columns.str.strip()

    df_detalle['OldCode'] = df_detalle['OldCode'].apply(limpiar_codigo)
    df_info['REF COLOR TALLA'] = df_info['REF COLOR TALLA'].apply(limpiar_codigo)
    


    # Hacer merge
    df_resultado = df_detalle.merge(
        df_info[['REF COLOR TALLA', 'DIST-BASE', 'DCTO AJUSTADO', 'PART CLIENTE', 'PART TOTTO']],
        how='inner',
        left_on='OldCode',
        right_on='REF COLOR TALLA'
    )
    
    # Guardar resultado
    salida = Path(f"data/{criterio}/detalle_consolidado_enriquecido.xlsx")
    df_resultado.to_excel(salida, index=False)
    print(f"✅ Detalle enriquecido guardado en: {salida}")
    
    
def agregar_totales_en_detalle(criterio):
    """Agrega una hoja de totales al detalle enriquecido."""
    from openpyxl import load_workbook

    ruta = Path(f"data/{criterio}/detalle_consolidado_enriquecido.xlsx")
    if not ruta.exists():
        print(f"❌ No existe el archivo enriquecido: {ruta}")
        return

    # Leer el archivo enriquecido
    df = pd.read_excel(ruta)

    # Asegurar que los campos sean numéricos
    campos_numericos = ['DIST-BASE', 'DiscountPercentage', 'Price', 'TotalSale', 'DiscountValue', 'PART TOTTO']
    for col in campos_numericos:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Crear el dataframe resumen
    df_resumen = df[[
        'O_NumberId', 'ProductId', 'ProductName', 'Quantity', 'Price',
        'OldCode', 'Total', 'DiscountPercentage', 'DiscountValue', 'DIST-BASE', 'TotalSale', 'PART TOTTO'
    ]].copy()

    # Agregar columnas calculadas
    df_resumen['costo+iva'] = df_resumen['DIST-BASE'] * 1.19
    df_resumen['nalsani_descuento'] = df_resumen['DIST-BASE'] * (df_resumen['DiscountPercentage']/ 100)
    df_resumen['martinez_descuento'] = df_resumen['Price'] * (df_resumen['DiscountPercentage']/ 100)
    df_resumen['nota-credito'] = df_resumen['Price'] * (df_resumen['nalsani_descuento'] * df_resumen['PART TOTTO'])
    df_resumen['profit'] = (
        df_resumen['TotalSale'] - (df_resumen['DIST-BASE'] * 1.19) + (df_resumen['nalsani_descuento'] * df_resumen['PART TOTTO'])
    )

    # Guardar como segunda hoja
    with pd.ExcelWriter(ruta, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_resumen.to_excel(writer, sheet_name='totales', index=False)

    print(f"📄 Hoja 'totales' agregada al archivo: {ruta}")



def main():
    archivos = fileSelector.seleccionar_archivos()
    if not archivos:
        print("No se seleccionaron archivos.")
        return

    criterio = input("🔍 ¿Qué palabra querés buscar en 'Observation'? ").strip()
    if not criterio:
        print("Criterio vacío. Cancelando.")
        return

    procesar_archivos(archivos, criterio)
    procesar_archivos_detallados(criterio)
    cruzar_con_info_adicional(criterio)
    agregar_totales_en_detalle(criterio)



def limpiar_codigo(s):
    if pd.isna(s):
        return ''
    return re.sub(r'\s+', '', str(s)).strip().replace('\xa0', '')

if __name__ == "__main__":
    main()












