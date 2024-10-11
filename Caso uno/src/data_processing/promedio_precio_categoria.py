import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from sqlalchemy import create_engine

# Creamos una conexión a la base de datos MySQL
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Realizamos la consulta para obtener precios y categorías
query = """
SELECT ca.nombre_categoria, p.precio 
FROM productos p 
JOIN categorias_principales ca ON ca.categoria_id = p.categoria_id
"""
df_precios = pd.read_sql(query, engine)

# Cerramos el motor de conexión
engine.dispose()

# Formateamos los precios en el DataFrame con el formato COP (para visualización)
df_precios['precio_formateado'] = df_precios['precio'].apply(lambda x: f'COP {int(x):,}'.replace(",", "."))

# Imprimimos el DataFrame con la columna formateada (opcional)
print(df_precios[['nombre_categoria', 'precio_formateado']].head())

# Calculamos el precio promedio por categoría usando la columna numérica 'precio'
precio_promedio = df_precios.groupby('nombre_categoria')['precio'].mean().reset_index()

# Configuramos el estilo de Seaborn
sns.set(style="whitegrid")

# Creamos el gráfico de barras
plt.figure(figsize=(10, 6))
sns.barplot(data=precio_promedio, x='nombre_categoria', y='precio', palette='Blues')

# Añadimos títulos y etiquetas
plt.title('Comparación de Precios Promedio por Categoría', fontsize=14)
plt.xlabel('Categoría', fontsize=12)
plt.ylabel('Precio Promedio (COP)', fontsize=12)

# Formateamos el eje Y para mostrar el precio con separadores de miles y símbolo COP
def format_cop(value, tick_number):
    return f'COP {int(value):,}'.replace(",", ".")

plt.gca().yaxis.set_major_formatter(FuncFormatter(format_cop))

# Mostramos gráfico
plt.xticks(rotation=45)
plt.show()

print(precio_promedio)