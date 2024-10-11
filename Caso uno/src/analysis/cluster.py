import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sqlalchemy import create_engine, text

# Creamos la conexión a la base de datos
engine = create_engine('mysql+pymysql://root:''@localhost/data_lab')

# Consulta SQL para extraer los datos necesarios
query = text("""
    SELECT 
        p.producto_id,
        p.precio,
        p.descuento,
        COUNT(DISTINCT pc.color_id) as num_colores,
        COUNT(DISTINCT pt.talla_id) as num_tallas,
        COUNT(DISTINCT ps.subcategoria_id) as num_subcategorias
    FROM 
        productos p
    LEFT JOIN 
        producto_colores pc ON p.producto_id = pc.producto_id
    LEFT JOIN 
        producto_tallas pt ON p.producto_id = pt.producto_id
    LEFT JOIN 
        producto_subcategorias ps ON p.producto_id = ps.producto_id
    GROUP BY 
        p.producto_id, p.precio, p.descuento
""")

# Ejecutar la consulta y cargar los resultados en un DataFrame
df = pd.read_sql(query, engine)

# Cerramos la conexión a la base de datos
engine.dispose()

# Preparar los datos para el clustering
features = ['precio', 'descuento', 'num_colores', 'num_tallas', 'num_subcategorias']

# Normalizar los datos
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[features])

# Método del codo para determinar el número óptimo de clusters
distortions = []
silhouette_scores = []
K = range(2, 11)

for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_features)
    distortions.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(scaled_features, kmeans.labels_))

# Visualización del método del codo
plt.figure(figsize=(8, 4))
plt.plot(K, distortions, 'bo-', label='Distorsión (Inercia)')
plt.xlabel('Número de clusters (k)')
plt.ylabel('Inercia')
plt.title('Método del Codo')
plt.show()

# Visualización del Silhouette Score
plt.figure(figsize=(8, 4))
plt.plot(K, silhouette_scores, 'ro-', label='Silhouette Score')
plt.xlabel('Número de clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score por número de clusters')
plt.show()

# Selección del número de clusters (puedes ajustar según los gráficos)
n_clusters = 6
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(scaled_features)

# Imprimir estadísticas por cluster
print("Estadísticas por cluster:")
print(df.groupby('cluster')[features].mean())

# Función para obtener productos representativos de cada cluster
def get_representative_products(df, features, n=3):
    representatives = {}
    for cluster in df['cluster'].unique():
        cluster_df = df[df['cluster'] == cluster]
        if len(cluster_df) == 0:
            print(f"Advertencia: El cluster {cluster} está vacío.")
            continue
        if len(cluster_df) < n:
            print(f"Advertencia: El cluster {cluster} tiene menos de {n} productos.")
        center = cluster_df[features].mean()
        distances = ((cluster_df[features] - center) ** 2).sum(axis=1)
        n_representatives = min(n, len(cluster_df))
        representative_indices = distances.nsmallest(n_representatives).index
        representatives[cluster] = cluster_df.loc[representative_indices, 'producto_id'].tolist()
    return representatives

# Obtener productos representativos
representative_products = get_representative_products(df, features)
print("\nProductos representativos por cluster:")
for cluster, products in representative_products.items():
    print(f"Cluster {cluster}: {products}")

# Gráfico de barras para el tamaño de los clusters
plt.figure(figsize=(8, 6))
df['cluster'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title('Número de productos por cluster')
plt.xlabel('Cluster')
plt.ylabel('Número de productos')
plt.xticks(rotation=0)
plt.show()

# Boxplot para la distribución de precios por cluster
plt.figure(figsize=(10, 6))
sns.boxplot(x='cluster', y='precio', data=df, palette='viridis')
plt.title('Distribución de precios por cluster')
plt.xlabel('Cluster')
plt.ylabel('Precio')
plt.show()

# Scatterplot utilizando variables importantes (precio vs descuento)
plt.figure(figsize=(10, 6))
sns.scatterplot(x='precio', y='descuento', hue='cluster', data=df, palette='viridis', s=100, alpha=0.7)
plt.title('Productos agrupados por Precio y Descuento')
plt.xlabel('Precio')
plt.ylabel('Descuento')
plt.show()

# Guardar los resultados del clustering
df.to_csv('resultados_clustering.csv', index=False)
print("\nResultados guardados en 'resultados_clustering.csv'")

# Información adicional
print("\nNúmero de productos en cada cluster:")
print(df['cluster'].value_counts().sort_index())

print("\nRango de precios por cluster:")
print(df.groupby('cluster')['precio'].agg(['min', 'max']))