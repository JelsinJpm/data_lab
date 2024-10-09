import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
import seaborn as sns
import matplotlib.pyplot as plt

# Creamos la conexión a la base de datos
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Realizamos la consulta para obtener los detalles de los productos
query = """
SELECT p.precio AS "precio", t.nombre AS "talla", c.nombre AS "color" 
    FROM productos p
    JOIN producto_tallas pt ON p.producto_id = pt.producto_id
    JOIN tallas t ON t.talla_id = pt.talla_id
    JOIN producto_colores pc ON p.producto_id = pc.producto_id
    JOIN colores c ON c.color_id = pc.color_id;
"""
df_productos = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos
engine.dispose()

# Convertimos las columnas 'color' y 'talla' en variables categóricas numéricas usando OneHotEncoder
encoder = OneHotEncoder()
encoded_features = encoder.fit_transform(df_productos[['talla', 'color']])

# Normalizamos el precio
scaler = StandardScaler()
df_productos['precio_normalizado'] = scaler.fit_transform(df_productos[['precio']])

# Formateamos los precios en formato COP
df_productos['precio_formateado'] = df_productos['precio'].apply(lambda x: f'COP {int(x):,}'.replace(",", "."))

# Combinamos las características codificadas con el precio normalizado
X = np.hstack([df_productos[['precio_normalizado']].values, encoded_features.toarray()])

# Definimos el número de clusters según el Método del Codo (3 en este caso)
n_clusters = 3
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df_productos['cluster'] = kmeans.fit_predict(X)

# Visualización 1: Distribución de Precios por Cluster (Boxplot)
plt.figure(figsize=(10, 6))
sns.boxplot(x='cluster', y='precio', data=df_productos)
plt.title('Distribución de Precios por Cluster')
plt.xlabel('Cluster')
plt.ylabel('Precio (COP)')
plt.show()

# Visualización 2: Heatmap de la relación entre color y cluster
cluster_color = pd.crosstab(df_productos['color'], df_productos['cluster'])
plt.figure(figsize=(10, 8))
sns.heatmap(cluster_color, cmap='YlGnBu', annot=True, fmt="d")
plt.title('Relación entre Clusters y Colores')
plt.ylabel('Color')
plt.xlabel('Cluster')
plt.show()

# Visualización 3: Heatmap de la relación entre talla y cluster
cluster_talla = pd.crosstab(df_productos['talla'], df_productos['cluster'])
plt.figure(figsize=(10, 8))
sns.heatmap(cluster_talla, cmap='YlGnBu', annot=True, fmt="d")
plt.title('Relación entre Clusters y Tallas')
plt.ylabel('Talla')
plt.xlabel('Cluster')
plt.show()

# Mostrar los primeros registros con el cluster asignado y el precio formateado
print(df_productos[['precio_formateado', 'talla', 'color', 'cluster']].head())