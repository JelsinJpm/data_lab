import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from sqlalchemy import create_engine

# Creamos una conexión a la base de datos MySQL
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Realizamos la consulta para obtener precios, categorías y descuentos
query = """
SELECT ca.nombre_categoria, p.precio, p.descuento 
FROM productos p 
JOIN categorias_principales ca ON ca.categoria_id = p.categoria_id
"""
df_productos = pd.read_sql(query, engine)

# Cerramos el motor de conexión
engine.dispose()

# Imprimimos el DataFrame con las columnas relevantes (opcional)
print(df_productos[['nombre_categoria', 'precio', 'descuento']].head())

# Calculamos el descuento promedio por categoría
descuento_promedio = df_productos.groupby('nombre_categoria')['descuento'].mean().reset_index()

# Configuramos el estilo de Seaborn
sns.set(style="whitegrid")

# Creamos el gráfico de barras para mostrar el descuento promedio por categoría
plt.figure(figsize=(10, 6))
sns.barplot(data=descuento_promedio, x='nombre_categoria', y='descuento', palette='Blues')

# Añadimos títulos y etiquetas
plt.title('Comparación de Descuento Promedio por Categoría', fontsize=14)
plt.xlabel('Categoría', fontsize=12)
plt.ylabel('Descuento Promedio (%)', fontsize=12)

# Formateamos el eje Y para mostrar los valores de descuento de manera más legible
def format_percentage(value, tick_number):
    return f'{value:.1f}%'

plt.gca().yaxis.set_major_formatter(FuncFormatter(format_percentage))

# Mostramos gráfico
plt.xticks(rotation=45)
plt.show()

# Si deseas filtrar y ver solo los productos con descuento mayor a cierto valor
# Ejemplo: Filtrar productos con un descuento mayor al 20%
productos_con_descuento = df_productos[df_productos['descuento'] > 20]
print(productos_con_descuento[['nombre_categoria', 'precio', 'descuento']].head())