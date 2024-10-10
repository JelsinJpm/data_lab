import pandas as pd
import ast
import re

# Cargar el archivo CSV que contiene los productos desde una ruta específica
df = pd.read_csv('C:/Users/johan/Desktop/Data/Caso uno/data/productos_scrapeados_v2_limpios.csv')

# Mostramos el número total de filas antes de la eliminación de duplicados
print(f"Número de filas antes de eliminar duplicados: {len(df)}")

# Eliminamos las filas duplicadas basadas en la columna 'Referencia'
df_clean = df.drop_duplicates(subset='Referencia')

# Mostramos el número de filas después de eliminar duplicados para verificar cuántas se eliminaron
print(f"Número de filas después de eliminar duplicados: {len(df_clean)}")

# Imprimimos cuántas filas duplicadas fueron eliminadas
print(f"Se eliminaron {len(df) - len(df_clean)} filas duplicadas.")

# Ahora, procesamos el DataFrame limpio para trabajar con las subcategorías y reordenar las columnas
df_clean.columns = df_clean.columns.str.strip()  # Eliminar espacios adicionales en los nombres de las columnas

# Verificar las columnas y eliminar las columnas numéricas (0, 1, 2, ..., 11)
df_clean = df_clean.loc[:, ~df_clean.columns.str.match(r'^\d+$')]

# Eliminar la columna 'Subcategorías' si ya tienes las columnas 'Subcategoría_1', 'Subcategoría_2', ...
if 'Subcategorías' in df_clean.columns:
    # Convertir las subcategorías de string a lista (si está en formato string como una lista)
    df_clean['Subcategorías'] = df_clean['Subcategorías'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Crear columnas separadas para cada subcategoría
    max_subcategorias = df_clean['Subcategorías'].apply(len).max()  # Cuántas subcategorías hay como máximo

    # Crear nuevas columnas para cada subcategoría
    for i in range(max_subcategorias):
        df_clean[f'Subcategoría_{i+1}'] = df_clean['Subcategorías'].apply(lambda x: x[i] if len(x) > i else None)

    # Eliminar la columna 'Subcategorías' original
    df_clean.drop(columns=['Subcategorías'], inplace=True)

# Organizar las subcategorías después de la columna 'Categoría Principal'
subcategorias = [f'Subcategoría_{i+1}' for i in range(7)]  # Aquí asumo que tienes hasta 7 subcategorías

# Crear una lista de las columnas en el orden deseado
columnas_ordenadas = ['Nombre del Producto', 'Categoría Principal'] + subcategorias + [col for col in df_clean.columns if col not in ['Nombre del Producto', 'Categoría Principal'] + subcategorias]

# Reordenar el DataFrame con las columnas organizadas
df_clean = df_clean[columnas_ordenadas]

# Función para limpiar y reorganizar las tallas
def limpiar_tallas(tallas):
    # Si el valor es una cadena, la convertimos en lista de tallas
    if isinstance(tallas, str):
        tallas = ast.literal_eval(tallas)  # Convertimos la cadena en lista de tallas
    
    tallas_limpias = []

    for talla in tallas:
        # Eliminar ceros a la izquierda en números (e.g., '02' -> '2')
        talla = re.sub(r'\b0+(\d)', r'\1', talla)
        
        # Si la talla contiene un rango numérico (e.g. '10-12'), la dividimos por el '-'
        if '-' in talla:
            tallas_limpias.extend(talla.split('-'))  # Divide y agrega cada número individualmente
        elif '/' in talla:
            # Si la talla contiene '/', la reemplazamos por una coma para separar los valores
            tallas_limpias.extend(talla.split('/'))  # Divide en 'XS' y 'S'
        else:
            # Si no es un rango ni tiene '/', agregamos la talla tal cual
            tallas_limpias.append(talla)

    # Devolver la lista de tallas limpiadas
    return tallas_limpias

# Aplicar la función de limpieza a la columna 'Tallas Disponibles'
df_clean['Tallas Disponibles'] = df_clean['Tallas Disponibles'].apply(limpiar_tallas)

# Mostrar el DataFrame limpio y organizado
print("\nDatos limpios y organizados:")
print(df_clean)

# Guardamos el DataFrame limpio en un nuevo archivo CSV
df_clean.to_csv('C:/Users/johan/Desktop/Data/Caso uno/data/productos_scrapeados_v3_limpios.csv', index=False)