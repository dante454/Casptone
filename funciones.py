import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Función para convertir tiempos a minutos y contar arribos por minuto
def procesar_tiempos(arrivals, division_minutos):
    minutos = [[segundo // division_minutos for segundo in simulacion] for simulacion in arrivals]
    df = pd.DataFrame(minutos).T  # Transponer para tener simulaciones como columnas
    arribos_por_minuto = df.apply(lambda x: x.value_counts().sort_index()).fillna(0).astype(int)
    return arribos_por_minuto

# Función para separar arribos en pickups y deliveries basados en los indicadores
def separar_arribos(arribos, indicadores):
    pickups = []
    deliveries = []
    for simulacion_index in range(len(arribos)):
        pickups_simulacion = []
        deliveries_simulacion = []
        arr_simulacion = arribos[simulacion_index]
        ind_simulacion = indicadores[simulacion_index]
        for i in range(len(arr_simulacion)):
            if ind_simulacion[i]:  # 1 es pick-up
                pickups_simulacion.append(arr_simulacion[i])
            else:  # 0 es delivery
                deliveries_simulacion.append(arr_simulacion[i])
        pickups.append(pickups_simulacion)
        deliveries.append(deliveries_simulacion)
    return pickups, deliveries

# Función para graficar la cantidad por minuto
def graficar_cantidad_por_minuto(arrivals, division_minutos, nombre_archivo):
    # Procesar arribos por minuto usando la función procesar_tiempos
    arribos_por_minuto = procesar_tiempos(arrivals, division_minutos)
    
    # Calcular la media por minuto
    media_por_minuto = arribos_por_minuto.mean(axis=1)
    
    plt.figure(figsize=(12, 8))
    for columna in arribos_por_minuto.columns:
        plt.plot(arribos_por_minuto.index, arribos_por_minuto[columna], alpha=0.5)
    plt.plot(arribos_por_minuto.index, media_por_minuto, color='black', linewidth=2, label='Media')
    plt.xlabel('Minuto del día')
    plt.ylabel('Número de arribos')
    plt.title(f'Estadísticas de arribos por minuto del día - {nombre_archivo}')
    plt.legend()
    plt.grid(True)
    plt.show()

# Función para graficar la densidad de puntos
def graficar_densidad_puntos(points, area_densidad):
    plt.figure(figsize=(10, 6))
    for puntos in points:
        x = puntos[:, 0]
        y = puntos[:, 1]
        plt.hist2d(x, y, bins=area_densidad, cmap='Blues', alpha=1)
    plt.colorbar(label='Número de Puntos')
    plt.show()

# Función para graficar puntos por simulación
def graficar_puntos_por_simulacion(points, numero_simulaciones_mapa):
    plt.figure(figsize=(10, 6))
    colores = plt.cm.viridis(np.linspace(0, 1, numero_simulaciones_mapa))
    for i in range(numero_simulaciones_mapa):
        puntos_simulacion = np.array(points[i])
        x = puntos_simulacion[:, 0]
        y = puntos_simulacion[:, 1]
        plt.scatter(x, y, color=colores[i], s=10, alpha=0.7, label=f'Puntos Simulación {i + 1}')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Puntos por Simulación')
    plt.legend()
    plt.grid(True)
    plt.show()

# Función para graficar puntos de una simulación específica
def graficar_puntos_simulacion(indicadores, points, simulacion_index):
    color_delivery = 'blue'
    color_pickup = 'red'
    puntos_simulacion = np.array(points[simulacion_index])
    indicadores_simulacion = np.array(indicadores[simulacion_index])
    x = puntos_simulacion[:, 0]
    y = puntos_simulacion[:, 1]
    colores = np.where(indicadores_simulacion, color_pickup, color_delivery)
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(x, y, color=colores, s=10, alpha=0.7)
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_delivery, markersize=10, label='Delivery (0)'), plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_pickup, markersize=10, label='Pick-Up (1)')]
    plt.legend(handles=handles)
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title(f'Puntos de la Simulación {simulacion_index + 1}')
    plt.grid(True)
    plt.show()

# Función para calcular estadísticas por minuto
def recuperacion_estadisticas(arrivals, nombre_archivo, division_minutos):
    arribos_por_minuto = procesar_tiempos(arrivals, division_minutos)
    mediana_por_minuto = arribos_por_minuto.median(axis=1)
    desviacion_por_minuto = arribos_por_minuto.std(axis=1)
    percentil_25 = arribos_por_minuto.quantile(0.25, axis=1)
    percentil_75 = arribos_por_minuto.quantile(0.75, axis=1)
    print(f'Desviación estándar: {desviacion_por_minuto} para la {nombre_archivo}')
    print(f'Mediana por minuto: {mediana_por_minuto} para la {nombre_archivo}')
    print(f'Percentil 25: {percentil_25} para la {nombre_archivo}')
    print(f'Percentil 75: {percentil_75} para la {nombre_archivo}')

# Función para proporcionar la proporción de deliveries y pickups
def proporcion_deliveri_pickup(indicadores, nombre_archivo):
    indicadores_df = pd.DataFrame(indicadores)
    cantidad_1 = (indicadores_df == 1).sum().sum()
    cantidad_0 = (indicadores_df == 0).sum().sum()
    total = cantidad_0 + cantidad_1
    porcentaje_1 = cantidad_1 / total
    porcentaje_0 = cantidad_0 / total
    print(f'Cantidad de Pick-Ups en indicadores: {cantidad_1} = {porcentaje_1}% para la {nombre_archivo}')
    print(f'Cantidad de Deliveries en indicadores: {cantidad_0} = {porcentaje_0}% para la {nombre_archivo}')

# Función para graficar promedio de deliveries y pickups
def graficar_promedio_deliveries_pickups(arrivals, indicadores, division_minutos, nombre_archivo):
    # Separar arrivals en pickups y deliveries
    pickups, deliveries = separar_arribos(arrivals, indicadores)
    
    # Procesar arribos para pickups y deliveries
    arribos_por_minuto_pickups = procesar_tiempos(pickups, division_minutos)
    arribos_por_minuto_deliveries = procesar_tiempos(deliveries, division_minutos)
    
    # Calcular la media por minuto para pickups y deliveries
    media_por_minuto_pickups = arribos_por_minuto_pickups.mean(axis=1)
    media_por_minuto_deliveries = arribos_por_minuto_deliveries.mean(axis=1)
    
    # Graficar promedio por minuto para pickups y deliveries
    plt.figure(figsize=(12, 8))
    plt.plot(media_por_minuto_pickups, color='red', label='Promedio Pick-Ups')
    plt.plot(media_por_minuto_deliveries, color='blue', label='Promedio Deliveries')
    plt.xlabel('Minuto del día')
    plt.ylabel('Número de arribos')
    plt.title(f'Promedio de Pick-Ups y Deliveries por Minuto - {nombre_archivo}')
    plt.legend()
    plt.grid(True)
    plt.show()


def graficar_puntos_con_indicadores(points, indicadores, numero_simulaciones_mapa):
    plt.figure(figsize=(10, 6))
    
    # Definir colores para indicadores
    color_delivery = 'blue'  # Color para delivery (0)
    color_pickup = 'red'     # Color para pick-up (1)
    
    for i in range(numero_simulaciones_mapa):
        puntos_simulacion = np.array(points[i])
        indicadores_simulacion = np.array(indicadores[i])
        
        # Dividir los puntos en pick-ups y deliveries
        x = puntos_simulacion[:, 0]
        y = puntos_simulacion[:, 1]
        
        # Crear una lista de colores basada en los indicadores
        colores = np.where(indicadores_simulacion, color_pickup, color_delivery)

        # Graficar los puntos
        plt.scatter(x, y, color=colores, s=10, alpha=0.7, label=f'Simulación {i + 1}')
    
    # Añadir la leyenda de colores manualmente
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_delivery, markersize=10, label='Delivery (0)'), plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_pickup, markersize=10, label='Pick-Up (1)')]
    plt.legend(handles=handles)
    
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Puntos por Simulación con Indicadores de Delivery/Pick-Up')
    plt.grid(True)
    plt.show()



# Función principal para analizar la instancia
def analizar_instancia(ruta_arrivals, ruta_deadlines, ruta_indicadores, ruta_points, ruta_profits, ruta_ready_times, ruta_service_times, nombre_archivo, division_minutos, area_densidad, numero_simulaciones_mapa):
    print(f'A continuación se encuentran los datos para la {nombre_archivo}')
    
    # Cargar datos desde archivos pickle
    with open(ruta_arrivals, 'rb') as archivo:
        arrivals = pickle.load(archivo)
    with open(ruta_deadlines, 'rb') as archivo:
        deadlines = pickle.load(archivo)
    with open(ruta_indicadores, 'rb') as archivo:
        indicadores = pickle.load(archivo)
    with open(ruta_points, 'rb') as archivo:
        points = pickle.load(archivo)
    with open(ruta_profits, 'rb') as archivo:
        profits = pickle.load(archivo)
    with open(ruta_ready_times, 'rb') as archivo:
        ready_times = pickle.load(archivo)
    with open(ruta_service_times, 'rb') as archivo:
        service_times = pickle.load(archivo)

    graficar_promedio_deliveries_pickups(arrivals, indicadores, division_minutos, nombre_archivo)

    # Graficar cantidad por minuto
    graficar_cantidad_por_minuto(arrivals, division_minutos, nombre_archivo)

    # Graficar densidad de puntos
    graficar_densidad_puntos(points, area_densidad)

    # Graficar puntos por simulación
    graficar_puntos_por_simulacion(points, numero_simulaciones_mapa)

    # Graficar puntos de la primera simulación
    graficar_puntos_simulacion(indicadores, points, 0)

    recuperacion_estadisticas(arrivals, nombre_archivo, division_minutos)

    proporcion_deliveri_pickup(indicadores, nombre_archivo)

