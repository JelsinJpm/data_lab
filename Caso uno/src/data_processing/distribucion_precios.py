import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import numpy as np

# Creamos la conexión a la base de datos MySQL utilizando SQLAlchemy
engine = create_engine('mysql+pymysql://root:@localhost/data_lab')

# Realizamos la consulta para obtener los precios de los productos
query = "SELECT precio FROM productos"
df_precios = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos después de realizar la consulta
engine.dispose()

# Nos aseguramos que los precios son numéricos (para evitar posibles errores con datos no válidos)
# pd.to_numeric convierte los valores no numéricos en NaN, lo que permite un manejo más fácil de los datos
df_precios['precio'] = pd.to_numeric(df_precios['precio'], errors='coerce')

# Aplicamos una transformación logarítmica a los precios para mejorar la distribución
# np.log1p(x) calcula log(1 + x), evitando errores con valores cero
df_precios['precio_log'] = np.log1p(df_precios['precio'])

# Formateamos los precios originales en formato COP (pesos colombianos) para visualización
# Esta transformación no afecta los cálculos, solo es para que los precios se vean más legibles
df_precios['precio_formateado'] = df_precios['precio'].apply(lambda x: f'COP {int(x):,}'.replace(",", "."))

# Configuramos el estilo de visualización con Seaborn (estilo de cuadrícula blanca)
sns.set(style="whitegrid")

# Creamos un histograma para mostrar la distribución de los precios transformados logarítmicamente
plt.figure(figsize=(10, 6))  # Definimos el tamaño de la figura
sns.histplot(df_precios['precio_log'], bins=20, kde=True, color='skyblue')  # Creamos el histograma con 20 bins y KDE

# Añadimos el título y etiquetas a la gráfica
plt.title('Distribución Logarítmica de Precios de Productos', fontsize=14)
plt.xlabel('Log(Precio)', fontsize=12)
plt.ylabel('Frecuencia', fontsize=12)

# Mostramos el gráfico
plt.show()

# Mostramos los primeros registros del DataFrame con precios originales, formateados y transformados
print(df_precios[['precio', 'precio_formateado', 'precio_log']].head())

print(df_precios)