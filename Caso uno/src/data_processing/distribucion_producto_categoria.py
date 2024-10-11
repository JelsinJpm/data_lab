import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Crear una conexión a la base de datos MySQL utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/data_lab')

# Realizamos la consulta para obtener las categorías y la cantidad de productos por cada una
# realizamos un JOIN entre las tablas 'productos' y 'categorias_principales' 
# y se agrupamos los resultados por nombre de categoría
query = """
SELECT ca.nombre_categoria, COUNT(p.producto_id) AS cantidad_productos
FROM productos p
JOIN categorias_principales ca ON p.categoria_id = ca.categoria_id
GROUP BY ca.nombre_categoria
ORDER BY cantidad_productos DESC
"""
df_categorias = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos después de la consulta
engine.dispose()

# Calcular total de productos
total_productos = df_categorias['cantidad_productos'].sum()

# Agregar columna de porcentaje
df_categorias['porcentaje'] = (df_categorias['cantidad_productos'] / total_productos) * 100

# Configuramos el estilo del gráfico utilizando Seaborn (estilo de cuadrícula blanca)
sns.set(style="whitegrid")

# Creamos un gráfico de barras para mostrar la cantidad de productos por categoría
plt.figure(figsize=(12, 8))  # Definir el tamaño del gráfico
sns.barplot(data=df_categorias, x='cantidad_productos', y='nombre_categoria', palette='viridis')  # Crear el gráfico

# Añadimos el título y etiquetas a los ejes del gráfico para mejorar la comprensión
plt.title('Distribución de Productos por Categoría', fontsize=16)
plt.xlabel('Cantidad de Productos', fontsize=12)
plt.ylabel('Categoría', fontsize=12)

# Mostramos el gráfico generado
plt.show()

print(df_categorias)