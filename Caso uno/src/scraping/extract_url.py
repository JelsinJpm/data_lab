import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime

# Configuración del sistema de logging
def setup_logger():
    log_filename = f"scraping_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger()

logger = setup_logger()

def extract_products(url):
    products = []
    seen_urls = set()  # Para almacenar URLs vistas y evitar duplicados
    page_number = 1  # Contador de la página
    
    while url:
        logger.info(f"Extrayendo datos de: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Lanzamos una excepción para códigos de estado HTTP no exitosos
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encuentra todos los productos en la página
            product_links = soup.find_all('a', class_='vtex-product-summary-2-x-clearLink')
            
            for product in product_links:
                product_url = f"https://www.arturocalle.com{product['href']}"  # Ajustamos el dominio aquí
                
                if product_url not in seen_urls:  # Verificamos si la URL ya fue vista
                    seen_urls.add(product_url)  # Marcamos como vista para no repetir algún producto
                    products.append({
                        'URL': product_url,
                        'Posición': len(products) + 1,  # Posición en la lista
                        'Paginación': page_number  # Número de la página actual
                    })
            
            logger.info(f"Extraídos {len(product_links)} productos de la página {page_number}")
            
            # Buscamos el enlace "Mostrar más"
            next_button = soup.find('a', href=lambda x: x and 'page=' in x)
            if next_button:
                # Construimos la URL de la siguiente página utilizando la base de la URL de la categoría
                url = f"{url.split('?')[0]}{next_button['href']}"  # Mantenemos la categoría en la URL
                page_number += 1  # Incrementamos el número de la página
            else:
                logger.info(f"No se encontraron más páginas para {url}")
                url = None  # No hay más páginas
        
        except requests.RequestException as e:
            logger.error(f"Error al acceder a la URL {url}: {str(e)}")
            url = None  # Terminamos el bucle si hay un error
    
    logger.info(f"Extracción completada para la URL inicial. Total de productos: {len(products)}")
    return products

# Listamos las URLs iniciales de las categorías que vamos a scrapear
category_urls = [
    'https://www.arturocalle.com/hombre',
    'https://www.arturocalle.com/woman',
    'https://www.arturocalle.com/kids',
    'https://www.arturocalle.com/viaje',
    'https://www.arturocalle.com/marketplace',
    'https://www.arturocalle.com/ofertas-arturo-calle'
]

all_products = []  # Aquí almacenaremos todos los productos de todas las categorías

# Iteramos sobre cada URL de categoría
for category_url in category_urls:
    logger.info(f"Iniciando extracción para: {category_url}")
    products = extract_products(category_url)  # Extraemos los productos de la categoría
    all_products.extend(products)  # Agregamos los productos extraídos a la lista general
    logger.info(f"Extracción completada para {category_url}. Productos extraídos: {len(products)}")

# Creamos un DataFrame y guardamos en CSV
df = pd.DataFrame(all_products)
csv_filename = f"productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_filename, index=False)
logger.info(f"Datos extraídos y guardados en {csv_filename}")
print(f"Datos extraídos y guardados en {csv_filename}")
logger.info("Proceso de scraping completado.")