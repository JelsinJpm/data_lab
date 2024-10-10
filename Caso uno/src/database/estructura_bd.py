from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DECIMAL, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Definimos la base para las clases de modelos
Base = declarative_base()

# Tabla intermedia Producto_Colores para relación muchos-a-muchos
producto_colores = Table('producto_colores', Base.metadata,
    Column('producto_id', Integer, ForeignKey('productos.producto_id'), primary_key=True),
    Column('color_id', Integer, ForeignKey('colores.color_id'), primary_key=True)
)

# Tabla intermedia Producto_Tallas para relación muchos-a-muchos
producto_tallas = Table('producto_tallas', Base.metadata,
    Column('producto_id', Integer, ForeignKey('productos.producto_id'), primary_key=True),
    Column('talla_id', Integer, ForeignKey('tallas.talla_id'), primary_key=True)
)

# Tabla intermedia Producto_Subcategorias para relación muchos-a-muchos
producto_subcategorias = Table('producto_subcategorias', Base.metadata,
    Column('producto_id', Integer, ForeignKey('productos.producto_id'), primary_key=True),
    Column('subcategoria_id', Integer, ForeignKey('subcategorias.subcategoria_id'), primary_key=True)
)

# Clase que representa la tabla de Categorías Principales
class CategoriaPrincipal(Base):
    __tablename__ = 'categorias_principales'
    
    categoria_id = Column(Integer, primary_key=True, autoincrement=True)  # ID de la categoría
    nombre_categoria = Column(String(255), nullable=False)  # Nombre de la categoría

    # Relación uno-a-muchos con Productos
    productos = relationship("Producto", back_populates="categoria_principal")

# Clase que representa la tabla de Productos
class Producto(Base):
    __tablename__ = 'productos'
    
    producto_id = Column(Integer, primary_key=True, autoincrement=True)  # ID del producto
    nombre = Column(String(255), nullable=False)  # Nombre del producto
    categoria_id = Column(Integer, ForeignKey('categorias_principales.categoria_id'), nullable=False)  # FK a la categoría
    referencia = Column(String(255))  # Referencia del producto
    precio = Column(DECIMAL(10, 2))  # Precio del producto
    descuento = Column(DECIMAL(5, 2))  # Descuento aplicado al producto
    descripcion = Column(Text)  # Descripción del producto
    detalles = Column(Text)  # Detalles adicionales del producto
    position = Column(Integer)  # Posición para ordenación
    pagination = Column(Integer)  # Número de página para paginación

    # Relaciones
    categoria_principal = relationship("CategoriaPrincipal", back_populates="productos")  # Relación con Categoría
    colores = relationship("Color", secondary=producto_colores, back_populates="productos")  # Relación con Colores
    tallas = relationship("Talla", secondary=producto_tallas, back_populates="productos")  # Relación con Tallas
    subcategorias = relationship("Subcategoria", secondary=producto_subcategorias, back_populates="productos")  # Relación con Subcategorías
    imagenes = relationship("Imagen", back_populates="producto")  # Relación con Imágenes
    recomendaciones = relationship("RecomendacionCuidado", back_populates="producto")  # Relación con Recomendaciones de Cuidado

# Clase que representa la tabla de Colores
class Color(Base):
    __tablename__ = 'colores'
    
    color_id = Column(Integer, primary_key=True, autoincrement=True)  # ID del color
    nombre = Column(String(255), nullable=False)  # Nombre del color
    
    # Relación muchos-a-muchos con Productos
    productos = relationship("Producto", secondary=producto_colores, back_populates="colores")

# Clase que representa la tabla de Tallas
class Talla(Base):
    __tablename__ = 'tallas'
    
    talla_id = Column(Integer, primary_key=True, autoincrement=True)  # ID de la talla
    nombre = Column(String(255), nullable=False)  # Nombre de la talla
    
    # Relación muchos-a-muchos con Productos
    productos = relationship("Producto", secondary=producto_tallas, back_populates="tallas")

# Clase que representa la tabla de Subcategorías
class Subcategoria(Base):
    __tablename__ = 'subcategorias'
    
    subcategoria_id = Column(Integer, primary_key=True, autoincrement=True)  # ID de la subcategoría
    nombre = Column(String(255), nullable=False)  # Nombre de la subcategoría
    
    # Relación muchos-a-muchos con Productos
    productos = relationship("Producto", secondary=producto_subcategorias, back_populates="subcategorias")

# Clase que representa la tabla de URLs de Imágenes
class Imagen(Base):
    __tablename__ = 'urls_imagenes'
    
    imagen_id = Column(Integer, primary_key=True, autoincrement=True)  # ID de la imagen
    producto_id = Column(Integer, ForeignKey('productos.producto_id'))  # FK al producto
    url = Column(Text, nullable=False)  # URL de la imagen
    
    # Relación uno-a-muchos con Productos
    producto = relationship("Producto", back_populates="imagenes")

# Clase que representa la tabla de Recomendaciones de Cuidado
class RecomendacionCuidado(Base):
    __tablename__ = 'recomendaciones_cuidado'
    
    recomendacion_id = Column(Integer, primary_key=True, autoincrement=True)  # ID de la recomendación
    producto_id = Column(Integer, ForeignKey('productos.producto_id'))  # FK al producto
    recomendacion = Column(Text, nullable=False)  # Texto de la recomendación
    
    # Relación uno-a-muchos con Productos
    producto = relationship("Producto", back_populates="recomendaciones")

# Conexión a la base de datos (ajustar el URI de conexión según corresponda)
engine = create_engine('mysql+pymysql://root:@localhost/data_lab')

# Creamos todas las tablas definidas en la base de datos
Base.metadata.create_all(engine)