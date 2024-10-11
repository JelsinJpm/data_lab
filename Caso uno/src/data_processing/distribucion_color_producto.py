import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Creamos la conexión a la base de datos MySQL usando SQLAlchemy
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Realizamos la consulta para obtener la cantidad de productos por color
# Agrupamos los productos según su color y contamos cuántos productos tienen cada color
query = """
SELECT c.nombre, COUNT(p.producto_id) as cantidad
    FROM producto_colores p
    JOIN colores c ON p.color_id = c.color_id
    GROUP BY c.nombre
    ORDER BY cantidad DESC
"""
df_colores = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos para liberar recursos
engine.dispose()

# Mostramos solo los 10 colores más frecuentes en los productos
top_n = 10
df_top_colores = df_colores.head(top_n)

# Creamos una nueva fila "Otros" que acumulara la cantidad de productos con los colores menos frecuentes
otros_colores = pd.DataFrame({'nombre': ['Otros'], 'cantidad': [df_colores['cantidad'][top_n:].sum()]})

# Concatenamos los 10 colores más frecuentes con la fila "Otros"
df_visualizacion = pd.concat([df_top_colores, otros_colores])

# Configuramos el estilo de Seaborn para el gráfico
sns.set(style="whitegrid")

# Creamos un gráfico de barras para visualizar la distribución de colores
plt.figure(figsize=(12, 8))
sns.barplot(data=df_visualizacion, x='nombre', y='cantidad', palette='Set3')  # Set3 es una paleta de colores predefinida

# Añadimos el título y etiquetas para mayor claridad en la visualización
plt.title(f'Distribución de Colores en los Productos (Top {top_n} + Otros)', fontsize=16)
plt.xlabel('Color', fontsize=12)
plt.ylabel('Cantidad de Productos', fontsize=12)

# Rotamos las etiquetas del eje x para evitar solapamientos y mejorar la legibilidad
plt.xticks(rotation=45)

# Mostrar el gráfico
plt.show()

print(df_visualizacion)