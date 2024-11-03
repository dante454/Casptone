import numpy as np

import pickle
import pandas as pd
import matplotlib.pyplot as plt

def graficar_rutas_y_puntos(camiones, simulacion):
    plt.figure(figsize=(10, 10))
    
    # Colores para las rutas de los camiones
    colores_camiones = ['blue', 'green', 'red']
    
    # Variable para controlar si ya se agregó la leyenda de cada camión
    etiquetas_camion = [False, False, False]
    
    # Iterar sobre los camiones y graficar cada ruta
    for idx, camion in enumerate(camiones):
        for ruta in camion.rutas:
            ruta = np.array(ruta)  # Convertir la ruta a un array de numpy
            if not etiquetas_camion[idx]:  # Solo agregar una vez la etiqueta
                plt.plot(ruta[:, 0], ruta[:, 1], color=colores_camiones[idx], label=f'Ruta Camión {camion.id}')
                etiquetas_camion[idx] = True
            else:
                plt.plot(ruta[:, 0], ruta[:, 1], color=colores_camiones[idx])

    # Graficar **todos** los puntos de la simulación diferenciados por tipo (pickup o delivery)
    pickup_legend = False
    delivery_legend = False
    
    for i, punto in enumerate(simulacion.puntos):
        if simulacion.indicadores[i] == 1:  # Pick-up
            if not pickup_legend:
                plt.scatter(punto[0], punto[1], color='orange', marker='o', label='Pick-up')
                pickup_legend = True
            else:
                plt.scatter(punto[0], punto[1], color='orange', marker='o')
        else:  # Delivery
            if not delivery_legend:
                plt.scatter(punto[0], punto[1], color='purple', marker='s', label='Delivery')
                delivery_legend = True
            else:
                plt.scatter(punto[0], punto[1], color='purple', marker='s')

    # Marcar el depósito (asumimos que está en el centro)
    plt.scatter(10000, 10000, color='black', marker='D', s=100, label='Depósito')

    # Dibujar las líneas divisorias de las áreas con un grosor más grande
    cx, cy = 10000, 10000
    plt.plot([cx, cx + 10000 * np.cos(np.radians(0))], [cy, cy + 10000 * np.sin(np.radians(0))], 'k-', linewidth=2.5)  # Línea 0° (ancho de línea 2.5)
    plt.plot([cx, cx + 10000 * np.cos(np.radians(120))], [cy, cy + 10000 * np.sin(np.radians(120))], 'k-', linewidth=2.5)  # Línea 120° (ancho de línea 2.5)
    plt.plot([cx, cx + 10000 * np.cos(np.radians(240))], [cy, cy + 10000 * np.sin(np.radians(240))], 'k-', linewidth=2.5)  # Línea 240° (ancho de línea 2.5)

    # Ajustar el gráfico
    plt.title('Rutas y Puntos de Pick-up/Delivery')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()
def procesar_tiempos(arrivals, division_minutos):

    minutos = [[segundo // division_minutos for segundo in simulacion] for simulacion in arrivals]
    df = pd.DataFrame(minutos).T  # Transponer para tener simulaciones como columnas
    arribos_por_minuto = df.apply(lambda x: x.value_counts().sort_index()).fillna(0).astype(int)
    return arribos_por_minuto

def calcular_distancia(punto1, punto2):
    return abs(punto1[0] - punto2[0]) + abs(punto1[1] - punto2[1])

# Función placeholder para calcular el tiempo de la ruta
def calcular_tiempo_ruta(ruta, velocidad_camion):
    distancia_total = calcular_distancia_ruta(ruta)
    tiempo_extra = len(ruta) * 5 #5 minutos en entregar cada pedido
    return ((distancia_total / velocidad_camion)  + tiempo_extra)# Tiempo en minutos


def calcular_distancia_ruta(ruta):
    distancia_total = 0

    # Calcular la distancia entre cada par de puntos consecutivos en la ruta
    for i in range(1, len(ruta)):
        distancia_total += calcular_distancia(ruta[i-1], ruta[i])

    return distancia_total

def calcular_beneficio(simulacion):
    beneficio = 0
    beneficio_maximo = 0

    # Iterar sobre los pedidos entregados
    for pedido in simulacion.pedidos_entregados:
        if pedido.indicador == 0:  # Es un delivery
            beneficio += 2
        elif pedido.indicador == 1:  # Es un pick-up
            beneficio += 1

    # Calcular el beneficio máximo posible
    for pedido in simulacion.pedidos_disponibles + simulacion.pedidos_entregados:
        if pedido.indicador == 0:  # Delivery
            beneficio_maximo += 2
        elif pedido.indicador == 1:  # Pick-up
            beneficio_maximo += 1

    # Calcular el porcentaje del beneficio máximo alcanzado
    porcentaje_recuperado = (beneficio / beneficio_maximo) * 100 if beneficio_maximo > 0 else 0

    print(f"Beneficio total: {beneficio}, Beneficio máximo: {beneficio_maximo}, \nPorcentaje recuperado: {porcentaje_recuperado:.2f}%")
    return beneficio, porcentaje_recuperado

def calcular_distancia_total(camiones):
    distancia_total = 0
    for camion in camiones:
        for ruta in camion.rutas:
            distancia_total += calcular_distancia_ruta(ruta)
    return distancia_total

def filtrar_por_radio_buffer(pedidos_disponibles, radio_buffer):
    # Definir la ubicación del depósito (en el centro del mapa)
    deposito = np.array([10000, 10000])
    
    pedidos_dentro_del_buffer = []
    
    for pedido in pedidos_disponibles:
        # Calcular la distancia Manhattan entre el depósito y el pedido
        distancia = np.abs(pedido.coordenadas[0] - deposito[0]) + np.abs(pedido.coordenadas[1] - deposito[1])
        
        # Si la distancia está dentro del radio del buffer, agregar el pedido a la lista
        if distancia <= radio_buffer:
            pedidos_dentro_del_buffer.append(pedido)
    
    return pedidos_dentro_del_buffer


centros_areas = {
    1: np.array([7500, 10000]),  # Centro del área 1
    2: np.array([12500, 7500]),  # Centro del área 2
    3: np.array([12500, 12500])  # Centro del área 3
}

# Definir un radio para cada área (puedes ajustar estos valores)
radios_areas = {
    1: 10000,  # Radio para el área 1
    2: 8000,  # Radio para el área 2(abajo iz)
    3: 70000   # Radio para el área 3
}

# Definir el depósito (ejemplo en el centro del mapa)
deposito = [10000, 10000]  # Ajusta las coordenadas según tu mapa

# Definir un radio máximo (e.g., 5000 metros)
radio_maximo = 5000

def filtrar_por_radio_depot(pedidos_disponibles, deposito, radio_maximo):
    pedidos_dentro_del_buffer = []

    for pedido in pedidos_disponibles:
        # Calcular la distancia euclidiana entre el pedido y el depósito
        distancia = np.sqrt((pedido.coordenadas[0] - deposito[0])**2 + 
                            (pedido.coordenadas[1] - deposito[1])**2)

        # Si la distancia está dentro del radio máximo, agregar el pedido a la lista
        if distancia <= radio_maximo:
            pedidos_dentro_del_buffer.append(pedido)

    return pedidos_dentro_del_buffer

