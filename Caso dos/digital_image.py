import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def solicitar_datos_recorte():
    while True:
        # Pedir al usuario los porcentajes de recorte para la imagen
        x_start_percent = float(input("Ingrese el porcentaje de inicio en X para recortar la imagen (e.g., 15 para 15%): "))
        x_end_percent = float(input("Ingrese el porcentaje de fin en X para recortar la imagen (e.g., 95 para 95%): "))
        y_start_percent = float(input("Ingrese el porcentaje de inicio en Y para recortar la imagen (e.g., 10 para 10%): "))
        y_end_percent = float(input("Ingrese el porcentaje de fin en Y para recortar la imagen (e.g., 50 para 50%): "))

        # Convertir los porcentajes a fracciones (e.g., 15% -> 0.15)
        x_start = x_start_percent / 100
        x_end = x_end_percent / 100
        y_start = y_start_percent / 100
        y_end = y_end_percent / 100

        return x_start, x_end, y_start, y_end

def solicitar_datos_escalado():
    # Pedir al usuario el número de muestras
    num_muestras = int(input("Ingrese el número de muestras (e.g., 1000): "))

    # Pedir al usuario el rango de escalado para X e Y
    x_min = float(input("Ingrese el valor mínimo del eje X (e.g., 0): "))
    x_max = float(input("Ingrese el valor máximo del eje X (e.g., 20): "))
    y_min = float(input("Ingrese el valor mínimo del eje Y (e.g., 0): "))
    y_max = float(input("Ingrese el valor máximo del eje Y (e.g., 500): "))

    return num_muestras, x_min, x_max, y_min, y_max

def cargar_y_recortar_imagen(image_path, x_start, x_end, y_start, y_end):
    # Cargar la imagen del gráfico de líneas
    img = cv2.imread(image_path)
    height, width = img.shape[:2]

    # Calcular las posiciones para recortar en función de los porcentajes
    x_start_px, x_end_px = int(width * x_start), int(width * x_end)
    y_start_px, y_end_px = int(height * y_start), int(height * y_end)

    # Recortar la imagen para centrarse en el área relevante (gráfico)
    cropped_img = img[y_start_px:y_end_px, x_start_px:x_end_px]
    
    return cropped_img, width, height

def mostrar_imagen(cropped_img):
    # Mostrar la imagen recortada y pedir confirmación al usuario
    plt.figure(figsize=(10, 6))
    plt.imshow(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Recortada - Verifique si es Correcta")
    plt.axis('off')
    plt.show()

    respuesta = input("¿Está satisfecho con el recorte? (s/n): ").strip().lower()
    return respuesta == 's'

def procesar_imagen(cropped_img):
    # Convertir a escala de grises y aplicar desenfoque
    gray_cropped = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    blurred_cropped = cv2.GaussianBlur(gray_cropped, (5, 5), 0)

    # Detectar bordes con Canny
    edges_cropped = cv2.Canny(blurred_cropped, threshold1=50, threshold2=150)

    # Encontrar contornos
    contours_cropped, _ = cv2.findContours(edges_cropped, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return contours_cropped, edges_cropped

def extraer_puntos(contours_cropped):
    data_cropped = []
    for cnt in contours_cropped:
        for point in cnt:
            x, y = point[0]
            data_cropped.append([x, y])

    df_cropped = pd.DataFrame(data_cropped, columns=['x', 'y'])
    
    return df_cropped

def filtrar_puntos(df_cropped, min_dist=2):
    # Filtrar puntos que están demasiado cerca para evitar duplicados
    df_cropped = df_cropped.sort_values(by='x')  # Ordenar por eje X
    df_filtrado = df_cropped.iloc[0:1]  # Comenzar con el primer punto
    
    for i in range(1, len(df_cropped)):
        x_diff = np.abs(df_cropped.iloc[i]['x'] - df_filtrado.iloc[-1]['x'])
        y_diff = np.abs(df_cropped.iloc[i]['y'] - df_filtrado.iloc[-1]['y'])
        if x_diff > min_dist or y_diff > min_dist:
            df_filtrado = pd.concat([df_filtrado, df_cropped.iloc[i:i+1]])

    return df_filtrado

def escalar_puntos(df_cropped, cropped_img, x_min, x_max, y_min, y_max):
    # Establecer la escala para los ejes X e Y
    width_cropped, height_cropped = cropped_img.shape[1], cropped_img.shape[0]
    scale_x = (x_max - x_min) / width_cropped
    scale_y = (y_max - y_min) / height_cropped

    # Aplicar las escalas a los puntos detectados
    df_cropped['x_escalado'] = x_min + df_cropped['x'] * scale_x
    df_cropped['y_escalado'] = y_max - df_cropped['y'] * scale_y  # Invertir el eje Y

    return df_cropped

def muestrear_puntos(df_cropped, num_muestras):
    # Ordenar puntos por el eje X
    df_cropped = df_cropped.sort_values(by='x_escalado')

    # Interpolación regularizada
    f_interpolacion = interp1d(df_cropped['x_escalado'], df_cropped['y_escalado'], kind='linear', fill_value="extrapolate")
    
    # Muestreo equidistante
    x_muestras = np.linspace(df_cropped['x_escalado'].min(), df_cropped['x_escalado'].max(), num_muestras)
    y_muestras = f_interpolacion(x_muestras)

    # DataFrame con los puntos muestreados
    df_muestreado = pd.DataFrame({'x_muestra': x_muestras, 'y_muestra': y_muestras})

    return df_muestreado

def graficar_puntos(df_muestreado, edges_cropped, cropped_img):
    # Graficar los puntos escalados
    plt.figure(figsize=(10, 6))
    plt.scatter(df_muestreado['x_muestra'], df_muestreado['y_muestra'], s=1, c='orange')
    plt.title("Puntos Detectados del Gráfico Escalado")
    plt.xlabel("Eje X")
    plt.ylabel("Eje Y")
    plt.grid()
    plt.show()

def main():
    image_path = input("Ingrese la ruta del archivo de imagen: ")

    # Solicitar los datos de recorte
    while True:
        x_start, x_end, y_start, y_end = solicitar_datos_recorte()

        # Cargar y recortar la imagen
        cropped_img, width, height = cargar_y_recortar_imagen(image_path, x_start, x_end, y_start, y_end)

        # Mostrar la imagen recortada para verificación del usuario
        if mostrar_imagen(cropped_img):
            break
        else:
            print("Por favor, ajuste los valores de recorte y vuelva a intentar.")

    # Solicitar los datos de escalado
    num_muestras, x_min, x_max, y_min, y_max = solicitar_datos_escalado()

    # Procesar imagen y obtener contornos
    contours_cropped, edges_cropped = procesar_imagen(cropped_img)
    
    # Extraer puntos detectados
    df_cropped = extraer_puntos(contours_cropped)

    if df_cropped.empty:
        print("No se detectaron puntos.")
        return

    # Filtrar puntos duplicados o demasiado cercanos
    df_filtrado = filtrar_puntos(df_cropped)

    # Escalar los puntos según los valores proporcionados por el usuario
    df_escalado = escalar_puntos(df_filtrado, cropped_img, x_min, x_max, y_min, y_max)

    # Muestrear puntos
    df_muestreado = muestrear_puntos(df_escalado, num_muestras)

    # Graficar resultados
    graficar_puntos(df_muestreado, edges_cropped, cropped_img)

    # Guardar en CSV si se desea
    archivo_salida = input("Ingrese el nombre del archivo CSV de salida (o presione Enter para omitir): ")
    if archivo_salida:
        df_muestreado.to_csv(archivo_salida, index=False)
        print(f"Resultados guardados en {archivo_salida}.csv")

if __name__ == "__main__":
    main()