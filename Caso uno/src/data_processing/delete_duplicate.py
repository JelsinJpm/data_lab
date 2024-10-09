import pandas as pd

# Cargamos el archivo CSV que contiene los productos desde una ruta específica
# Debemos asegurarnos de que el archivo esté en la ruta correcta para evitar errores
df = pd.read_csv('C:/Users/johan/Desktop/Data/Caso uno/data/productos_scrapeados.csv')

# Mostramos el número total de filas antes de la eliminación de duplicados
# Esto nos permite comparar la cantidad de datos antes y después del proceso de limpieza
print(f"Número de filas antes de eliminar duplicados: {len(df)}")

# Eliminamos las filas duplicadas basadas en la columna 'Referencia'
# Esto asegura que cada producto sea único en base a su referencia
df_clean = df.drop_duplicates(subset='Referencia')

# Mostramos el número de filas después de eliminar duplicados para verificar cuántas se eliminaron
print(f"Número de filas después de eliminar duplicados: {len(df_clean)}")

# Guardamos el DataFrame limpio en un nuevo archivo CSV en la ruta especificada
# El parámetro index=False evita que el índice del DataFrame sea guardado en el archivo final
df_clean.to_csv('C:/Users/johan/Desktop/Data/Caso uno/data/productos_scrapeados_v3_limpios.csv', index=False)

# Imprimimos cuántas filas duplicadas fueron eliminadas en total
# Esto nos permite saber el impacto del proceso de limpieza
print(f"Se eliminaron {len(df) - len(df_clean)} filas duplicadas.")