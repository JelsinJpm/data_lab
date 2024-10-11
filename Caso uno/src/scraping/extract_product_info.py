import requests
from bs4 import BeautifulSoup
import time
import logging
import pandas as pd  # Importar pandas para la estructuración de los datos
from requests.exceptions import ChunkedEncodingError, ConnectionError

# Configuración del logger
logging.basicConfig(
    filename='scraping_productos.log',  # Archivo donde se guardarán los logs
    level=logging.INFO,                 # Nivel de los logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato de los logs
    datefmt='%Y-%m-%d %H:%M:%S'
)

def scrape_product(url, position, pagination, max_retries=3, wait_time=2):
    logging.info(f"Iniciando scraping para la URL: {url}")
    
    start_time = time.time()  # Comenzamos a medir el tiempo

    retries = 0
    while retries < max_retries:
        try:
            time.sleep(wait_time)  # Espera para dar tiempo a que la página cargue completamente
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                logging.info(f"Solicitud exitosa para {url}")
                
                soup = BeautifulSoup(response.content, "html.parser")  # Parsear el contenido HTML

                # Extraer el nombre del producto
                product_name = soup.find("span", class_="vtex-store-components-3-x-productBrand")
                product_name = (
                    product_name.get_text(strip=True) if product_name else "Nombre no disponible"
                )

                # Extraer la categoría principal y subcategorías (breadcrumb)
                breadcrumb = soup.find("div", {"data-testid": "breadcrumb"})
                categories = []
                if breadcrumb:
                    links = breadcrumb.find_all("a")
                    categories = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
                    main_category = categories[0] if categories else None
                    subcategories = categories[1:] if len(categories) > 1 else []
                else:
                    main_category = None
                    subcategories = []

                # Extraer la referencia
                reference = soup.find("span", class_="vtex-product-identifier-0-x-product-identifier__value")
                reference = (
                    reference.get_text(strip=True) if reference else "Referencia no disponible"
                )

                # Extracción del precio
                price_container = soup.find("span", class_="vtex-product-price-1-x-sellingPriceValue")
                price = (
                    price_container.get_text(strip=True) if price_container else "Precio no disponible"
                )

                # Extracción de la descripción del producto
                description_container = soup.find("div", class_="vtex-store-components-3-x-productDescriptionText")
                description = (
                    " ".join(part.strip() for part in description_container.strings if part.strip() and "Mostrar más" not in part)
                    if description_container else "Descripción no disponible"
                )

                # Extracción de los detalles del producto
                product_details = {}
                details_container = soup.find(
                    "td", class_="vtex-store-components-3-x-specificationItemSpecifications--especificacionesdeta"
                )
                if details_container:
                    for li in details_container.find_all("li"):
                        text = li.text.strip()
                        try:
                            key, value = text.split(":", 1)
                            product_details[key.strip()] = value.strip()
                        except ValueError:
                            continue  # Omite si no se puede dividir

                # Extracción de las recomendaciones de cuidado
                care_instructions = []
                care_container = soup.find(
                    "td", class_="vtex-store-components-3-x-specificationItemSpecifications--especificacionesapli"
                )
                if care_container:
                    care_instructions = [li.text.strip() for li in care_container.find_all("li")]

                # Extracción de imágenes del producto
                image_urls = []
                image_container = soup.find(
                    "div", class_="vtex-store-components-3-x-carouselGaleryCursor"
                )
                if image_container:
                    images = image_container.find_all("img", class_="vtex-store-components-3-x-productImageTag")
                    for img in images:
                        src = img.get("src")
                        if src:
                            base_url = src.split("?")[0]  # Extraer la URL de la imagen de mayor resolución
                            image_urls.append(base_url)

                # Extracción de los colores disponibles
                colors_container = soup.find('div', class_='vtex-store-components-3-x-skuSelectorSubcontainer--colores')
                colors = []
                if colors_container:
                    color_options = colors_container.find_all('div', class_='vtex-store-components-3-x-skuSelectorItem')
                    for option in color_options:
                        if 'vtex-store-components-3-x-diagonalCross' not in option.get('class', []) and \
                        'vtex-store-components-3-x-skuSelectorItem--disabled' not in option.get('class', []) and \
                        option.get('aria-disabled') != 'true':
                            color_name = option.find('div', class_='vtex-store-components-3-x-skuSelectorItemTextValue')
                            color_name = color_name.get_text(strip=True) if color_name else "Color no disponible"
                            colors.append(color_name)

                # Extracción de las tallas disponibles
                sizes_container = soup.find('div', class_='vtex-store-components-3-x-skuSelectorSubcontainer--talla')
                sizes = []
                if sizes_container:
                    size_options = sizes_container.find_all('div', class_='vtex-store-components-3-x-skuSelectorItem')
                    for option in size_options:
                        if 'vtex-store-components-3-x-diagonalCross' not in option.get('class', []) and \
                        'vtex-store-components-3-x-skuSelectorItem--disabled' not in option.get('class', []) and \
                        option.get('aria-disabled') != 'true':
                            size_name = option.find('div', class_='vtex-store-components-3-x-skuSelectorItemTextValue')
                            size_name = size_name.get_text(strip=True) if size_name else "Talla no disponible"
                            sizes.append(size_name)

                # Extracción del descuento
                discount_container = soup.find('div', class_='vtex-store-components-3-x-discountContainer')
                discount = "0%"  # Valor por defecto si no hay descuento
                if discount_container:
                    discount_value = discount_container.find('div', class_='vtex-store-components-3-x-discountInsideContainer')
                    if discount_value:
                        discount = discount_value.get_text(strip=True)

                # Empaquetar la información en un diccionario
                product_data = {
                    "Nombre del Producto": product_name,
                    "Categoría Principal": main_category,
                    "Subcategorías": subcategories,
                    "Referencia": reference,
                    "Precio": price,
                    "Descuento": discount,
                    "Colores Disponibles": colors,
                    "Tallas Disponibles": sizes,
                    "Descripción del Producto": description,
                    "Detalles del Producto": product_details,
                    "Recomendaciones de Cuidado": care_instructions,
                    "URLs de Imágenes": image_urls,
                    "Position": position,
                    "Pagination": pagination
                }

                end_time = time.time()  # Medir el tiempo que tomó la extracción
                logging.info(f"Extracción completada para {url} en {end_time - start_time:.2f} segundos.")
                
                return product_data

            else:
                logging.error(f"Error en la solicitud a {url}. Código de estado: {response.status_code}")
                return None
        
        except (ChunkedEncodingError, ConnectionError) as e:
            retries += 1
            logging.error(f"Error de conexión: {e}. Reintentando ({retries}/{max_retries})...")
            time.sleep(wait_time)  # Espera antes de reintentar
        except Exception as e:
            logging.error(f"Otro error: {e}")
            break
    
    logging.error(f"No se pudo completar la solicitud para la URL: {url} después de {max_retries} intentos.")
    return None

# Comenzar a medir el tiempo total
start_time_total = time.time()

# Cargar el archivo CSV con las URLs, posiciones y paginaciones
csv_file = "C:/Users/johan/Desktop/Data/Caso uno/src/scraping/productos_20241006_165851.csv"
product_df = pd.read_csv(csv_file)

# Lista para almacenar los datos de todos los productos
all_products = []

# Iterar sobre las filas del DataFrame
for index, row in product_df.iterrows():
    url = row['URL']
    position = row['Posición']
    pagination = row['Paginación']
    print(f"Scrapeando URL: {url} (Posición: {position}, Paginación: {pagination})")
    
    product_data = scrape_product(url, position, pagination)
    if product_data:
        all_products.append(product_data)

# Convertir la lista de productos en un DataFrame
products_df = pd.DataFrame(all_products)

# Guardar los datos en un archivo CSV
products_df.to_csv('productos_scrapeados_v4.csv', index=False, encoding='utf-8')
logging.info("Datos estructurados y almacenados en productos_scrapeados_v4.csv")

# Calcular el tiempo total de ejecución
end_time_total = time.time()
execution_time = end_time_total - start_time_total
logging.info(f"Tiempo total de ejecución: {execution_time:.2f} segundos")
print(f"Datos estructurados y almacenados en 'productos_scrapeados_v4.csv'")