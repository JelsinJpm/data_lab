import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from sqlalchemy import create_engine

# Creamos la conexión a la base de datos MySQL utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/data_lab')

# Realizamos la consulta para obtener los precios de los productos y los nombres de sus categorías
query = """
SELECT p.precio, ca.nombre_categoria 
FROM productos p
JOIN categorias_principales ca ON p.categoria_id = ca.categoria_id
"""
df_precios = pd.read_sql(query, engine)

# Formateamos los precios para mostrar en formato COP (pesos colombianos) solo para visualización
# Este formateo nos permite mostrar los precios de manera más clara
df_precios['precio_formateado'] = df_precios['precio'].apply(lambda x: f'COP {int(x):,}'.replace(",", "."))

# Cerramos la conexión a la base de datos después de realizar la consulta
engine.dispose()

# Configuramos el estilo de Seaborn para mejorar la visualización
sns.set(style="whitegrid")

# Creamos un gráfico de caja (boxplot) para visualizar la distribución de precios por categoría
plt.figure(figsize=(12, 8))  # Definir el tamaño de la figura
sns.boxplot(data=df_precios, x='nombre_categoria', y='precio', palette='Blues')  # Gráfico de caja

# Añadimos el título y etiquetas a los ejes para mejorar la interpretación del gráfico
plt.title('Distribución de Precios por Categoría', fontsize=16)
plt.xlabel('Categoría', fontsize=12)
plt.ylabel('Precio', fontsize=12)

# Formateamos los valores del eje Y para mostrar los precios en formato COP (pesos colombianos)
# Definimos una función personalizada para formatear los precios en el gráfico
def format_cop(value,  tick_number):
    return f'COP {int(value):,}'.replace(",", ".")

# Aplicamos el formateo personalizado al eje Y
plt.gca().yaxis.set_major_formatter(FuncFormatter(format_cop))

# Rotamos las etiquetas del eje X para evitar solapamiento y mejorar la legibilidad
plt.xticks(rotation=45)

# Mostramos el gráfico generado
plt.show()