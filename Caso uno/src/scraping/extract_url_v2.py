import pandas as pd
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

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

def extract_products(playwright, url):
    products = []
    seen_urls = set()  # Para almacenar URLs vistas y evitar duplicados
    page_number = 1  # Contador de la página
    
    try:
        browser = playwright.chromium.launch(headless=True)  # Lanzar el navegador
        page = browser.new_page()

        while url:
            logger.info(f"Extrayendo datos de: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state('networkidle')  # Esperar a que la página termine de cargar

                # Extraemos todos los enlaces de productos
                product_links = page.query_selector_all('a.vtex-product-summary-2-x-clearLink')

                for product in product_links:
                    product_url = product.get_attribute('href')  # Extraemos el href con el SKU ID
                    full_url = f"https://www.arturocalle.com{product_url}"  # Formamos la URL completa
                    
                    if full_url not in seen_urls:  # Verificamos si la URL ya fue vista
                        seen_urls.add(full_url)  # Marcamos como vista para no repetir algún producto
                        products.append({
                            'URL': full_url,
                            'Posición': len(products) + 1,  # Posición en la lista
                            'Paginación': page_number  # Número de la página actual
                        })

                logger.info(f"Extraídos {len(product_links)} productos de la página {page_number}")

                # Intentamos localizar el botón de "Mostrar más" o el siguiente enlace de paginación
                next_button = page.query_selector('a[href*="page="]')
                if next_button:
                    next_url = next_button.get_attribute('href')
                    url = f"{url.split('?')[0]}{next_url}"  # Construimos la URL de la siguiente página
                    page_number += 1  # Incrementamos el número de la página
                else:
                    logger.info(f"No se encontraron más páginas para {url}")
                    url = None  # No hay más páginas

            except Exception as e:
                logger.error(f"Error al acceder a la URL {url}: {str(e)}")
                url = None  # Terminamos el bucle si hay un error

        browser.close()
        logger.info(f"Extracción completada para la URL inicial. Total de productos: {len(products)}")
        return products

    except Exception as e:
        logger.error(f"Error al iniciar el navegador: {str(e)}")
        return []

# Iniciamos Playwright y extraemos los productos
with sync_playwright() as playwright:
    # URLs de las categorías que deseas scrapear
    category_urls = [
        # 'https://www.arturocalle.com/hombre',
        # 'https://www.arturocalle.com/woman',
        'https://www.arturocalle.com/kids',
        # 'https://www.arturocalle.com/viaje',
        # 'https://www.arturocalle.com/marketplace',
        'https://www.arturocalle.com/ofertas-arturo-calle'
    ]

    all_products = []  # Aquí almacenaremos todos los productos de todas las categorías

    # Iteramos sobre cada URL de categoría
    for category_url in category_urls:
        logger.info(f"Iniciando extracción para: {category_url}")
        products = extract_products(playwright, category_url)  # Extraemos los productos de la categoría
        all_products.extend(products)  # Agregamos los productos extraídos a la lista general
        logger.info(f"Extracción completada para {category_url}. Productos extraídos: {len(products)}")

# Creamos un DataFrame y guardamos en CSV
df = pd.DataFrame(all_products)
csv_filename = f"productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_filename, index=False)
logger.info(f"Datos extraídos y guardados en {csv_filename}")
print(f"Datos extraídos y guardados en {csv_filename}")
logger.info("Proceso de scraping completado.")