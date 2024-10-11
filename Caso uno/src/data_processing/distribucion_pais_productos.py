import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import ast  # Para convertir strings en formato de diccionario

# Creamos la conexión a la base de datos MySQL usando SQLAlchemy
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Realizamos la consulta para obtener la columna 'detalles' de la tabla 'productos'
# La columna 'detalles' contiene información adicional en formato de string
query = "SELECT detalles FROM productos"
df_detalles = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos para liberar recursos
engine.dispose()

# Función para extraer el 'País de Origen' de la columna 'detalles'
# Esta función convierte el string de la columna en un diccionario y extrae el país
def obtener_pais_origen(detalles):
    try:
        detalles_dict = ast.literal_eval(detalles)  # Convertir el string a diccionario
        return detalles_dict.get('País de Origen', 'Desconocido')  # Extraer el país de origen
    except (ValueError, SyntaxError):  # Manejar errores en la conversión del string a diccionario
        return 'Desconocido'

# Aplicamos la función 'obtener_pais_origen' a cada fila de la columna 'detalles'
df_detalles['pais_origen'] = df_detalles['detalles'].apply(obtener_pais_origen)

# Obtenemos el top 3 de países con más productos
# Utilizamos value_counts() para contar cuántos productos hay por país y nlargest() para seleccionar los 3 principales
top_paises = df_detalles['pais_origen'].value_counts().nlargest(3)

# Visualizamos la distribución de los países de origen utilizando un gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(x=top_paises.values, y=top_paises.index, palette='viridis')

# Añadimos el título y etiquetas al gráfico para mayor claridad
plt.title('Top 3 Países de Origen de los Productos', fontsize=16)
plt.xlabel('Cantidad de Productos', fontsize=12)
plt.ylabel('País de Origen', fontsize=12)

# Mostramos el gráfico resultante
plt.show()

# Mostramos los primeros registros del DataFrame con el país de origen extraído
print(df_detalles[['detalles', 'pais_origen']].head())

print(top_paises)