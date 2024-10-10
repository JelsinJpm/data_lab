import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from estructura_bd import CategoriaPrincipal, Producto, Subcategoria, Color, Talla, Imagen, RecomendacionCuidado
import ast  # Usar ast.literal_eval en lugar de eval para mayor seguridad

# Conexión a la base de datos
engine = create_engine('mysql+pymysql://root:@localhost/data_lab')
Session = sessionmaker(bind=engine)

# Función para procesar el precio desde un string a un float
def procesar_precio(precio_str):
    # Eliminar el símbolo de dólar y formatear el precio
    precio_str = precio_str.replace("$", "").replace(".", "").replace(",", ".")
    return float(precio_str)

# Función para procesar el descuento desde un string a un float
def procesar_descuento(descuento_str):
    # Eliminar el símbolo '%' y espacios
    descuento_str = descuento_str.replace("%", "").strip()
    return float(descuento_str)  # Convertir a decimal

# Función para insertar los datos desde el archivo CSV
def insertar_datos_csv(csv_file):
    session = Session()  # Iniciar sesión
    try:
        # Abrir el archivo CSV
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)  # Leer el archivo como un diccionario
            
            # Limpiar los encabezados para eliminar los espacios extra
            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            
            # Imprimir los encabezados para depuración (opcional)
            print("Encabezados del archivo CSV:", reader.fieldnames)

            # Procesar cada fila en el archivo CSV
            for row in reader:
                # Verificar o insertar la Categoría Principal
                categoria_nombre = row['Categoría Principal']
                categoria_principal = session.query(CategoriaPrincipal).filter_by(nombre_categoria=categoria_nombre).first()
                if not categoria_principal:
                    categoria_principal = CategoriaPrincipal(nombre_categoria=categoria_nombre)
                    session.add(categoria_principal)
                    session.flush()  # Asegurar que se cree el ID para la relación del producto
                
                # Procesar subcategorías
                subcategorias = []
                for i in range(1, 8):  # Recorremos las columnas de subcategorías (Subcategoría_1 a Subcategoría_7)
                    subcategoria = row.get(f'Subcategoría_{i}')
                    if subcategoria:  # Solo agregar si la subcategoría no es vacía
                        subcategorias.append(subcategoria)
                
                subcategoria_objs = []
                unique_subcategorias = set(subcategorias)  # Usar un conjunto para evitar duplicados
                
                for subcat in unique_subcategorias:
                    subcategoria = session.query(Subcategoria).filter_by(nombre=subcat).first()
                    if not subcategoria:
                        subcategoria = Subcategoria(nombre=subcat)
                        session.add(subcategoria)
                        session.flush()  # Asegurar que se cree el ID
                    subcategoria_objs.append(subcategoria)
                
                # Procesar colores
                colores = ast.literal_eval(row['Colores Disponibles']) if row['Colores Disponibles'] else []  # Usar ast.literal_eval
                color_objs = []
                unique_colores = set(colores)  # Usar un conjunto para evitar duplicados
                
                for color in unique_colores:
                    color_obj = session.query(Color).filter_by(nombre=color).first()
                    if not color_obj:
                        color_obj = Color(nombre=color)
                        session.add(color_obj)
                        session.flush()  # Asegurar que se cree el ID
                    color_objs.append(color_obj)
                
                # Procesar tallas
                tallas = ast.literal_eval(row['Tallas Disponibles']) if row['Tallas Disponibles'] else []  # Usar ast.literal_eval
                talla_objs = []
                unique_tallas = set(tallas)  # Usar un conjunto para evitar duplicados
                
                for talla in unique_tallas:
                    talla_obj = session.query(Talla).filter_by(nombre=talla).first()
                    if not talla_obj:
                        talla_obj = Talla(nombre=talla)
                        session.add(talla_obj)
                        session.flush()  # Asegurar que se cree el ID
                    talla_objs.append(talla_obj)
                
                # Verificar si el producto ya existe por referencia
                existing_product = session.query(Producto).filter_by(referencia=row['Referencia']).first()
                if existing_product:
                    print(f"El producto con la referencia {row['Referencia']} ya existe. Se omitirá la inserción.")
                    continue  # O puedes usar 'break' si deseas detener todo el proceso
                
                # Crear el producto
                producto = Producto(
                    nombre=row['Nombre del Producto'],
                    categoria_principal=categoria_principal,
                    referencia=row['Referencia'],
                    precio=procesar_precio(row['Precio']),
                    descuento=procesar_descuento(row['Descuento']),
                    descripcion=row['Descripción del Producto'],
                    detalles=row['Detalles del Producto'],
                    position=int(row['Position']),
                    pagination=int(row['Pagination'])
                )
                session.add(producto)
                session.flush()  # Asegurar que el producto obtenga un ID para las relaciones
                
                # Relacionar subcategorías, colores y tallas
                for subcategoria in subcategoria_objs:
                    if subcategoria not in producto.subcategorias:
                        producto.subcategorias.append(subcategoria)
                
                for color in color_objs:
                    if color not in producto.colores:
                        producto.colores.append(color)
                
                for talla in talla_objs:
                    if talla not in producto.tallas:
                        producto.tallas.append(talla)
                
                # Procesar URLs de imágenes
                imagenes = ast.literal_eval(row['URLs de Imágenes']) if row['URLs de Imágenes'] else []  # Usar ast.literal_eval
                for url in imagenes:
                    imagen = Imagen(producto_id=producto.producto_id, url=url)
                    session.add(imagen)
                
                # Procesar recomendaciones de cuidado
                recomendaciones = ast.literal_eval(row['Recomendaciones de Cuidado']) if row['Recomendaciones de Cuidado'] else []  # Usar ast.literal_eval
                for recomendacion in recomendaciones:
                    recomendacion_obj = RecomendacionCuidado(producto_id=producto.producto_id, recomendacion=recomendacion)
                    session.add(recomendacion_obj)
            
            # Hacer commit de todos los cambios
            session.commit()
            print("Datos insertados correctamente.")
    
    except Exception as e:
        session.rollback()  # Revertir cambios en caso de error
        print(f"Error al insertar datos: {e}")

    finally:
        session.close()  # Asegurar que la sesión se cierra

# Ejecutar la inserción de datos desde el CSV
insertar_datos_csv('C:/Users/johan/Desktop/Data/Caso uno/data/productos_scrapeados_v3_limpios.csv')