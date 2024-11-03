import numpy as np
import matplotlib.pyplot as plt
from funciones_caso_base import *

# Función para calcular la distancia euclidiana entre dos puntos
def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Algoritmo de Cheapest Insertion corregido
def cheapest_insertion(points, depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=180):
    """
    Algoritmo de Cheapest Insertion modificado para manejar prioridades y rechazar "Pick-ups" y "Deliveries" de forma simplificada.
    """

    # 1. Calcular las prioridades de los pedidos
    def calcular_prioridad(pedido):
        if pedido.indicador == 0:  # Delivery
            tiempo_restante = (pedido.minuto_llegada - minuto_actual) * -1
            return tiempo_restante  # Prioridad más alta cuando el tiempo restante es bajo
        else:  # Pick-up
            tiempo_transcurrido = minuto_actual - 520  # Desde el inicio de la simulación
            return max(0, tiempo_transcurrido)  # Prioridad más alta a medida que el día avanza

    # 2. Ordenar los pedidos por prioridad (de mayor a menor)
    pedidos_disponibles = sorted(pedidos_disponibles, key=calcular_prioridad, reverse=True)

    # Filtrar los pedidos válidos (dentro del tiempo límite)
    pedidos_validos = [
        pedido for pedido in pedidos_disponibles
        if minuto_actual - pedido.minuto_llegada <= tiempo_limite
    ]

    if not pedidos_validos:
        return [depot, depot]  # No hay pedidos válidos

    # Inicializar la ruta desde el depot
    route = [0]  # '0' representa el depósito

    # 3. Encontrar el pedido más cercano al depot para comenzar la ruta
    min_dist = float('inf')
    next_point = None
    for i, pedido in enumerate(pedidos_validos):
        dist = euclidean_distance(depot, pedido.coordenadas)
        if dist < min_dist:
            min_dist = dist
            next_point = i

    # Añadir el pedido más cercano a la ruta
    route.append(next_point)
    unvisited = set(range(len(pedidos_validos))) - {next_point}  # Puntos no visitados

    # 4. Proceso de inserción con prioridades y rechazo inteligente
    while unvisited:
        min_increase = float('inf')
        best_position = None
        best_point = None

        # Buscar el mejor punto para insertar con el menor incremento de distancia
        for point in unvisited:
            for i in range(1, len(route)):
                # 4.1 Calcular el incremento de distancia si se inserta el punto
                current_dist = euclidean_distance(
                    pedidos_validos[route[i]].coordenadas, 
                    pedidos_validos[route[i - 1]].coordenadas
                )
                new_dist = (
                    euclidean_distance(pedidos_validos[route[i - 1]].coordenadas, pedidos_validos[point].coordenadas) +
                    euclidean_distance(pedidos_validos[point].coordenadas, pedidos_validos[route[i]].coordenadas)
                )
                increase = new_dist - current_dist

                # 4.2 Criterio de rechazo para "Pick-ups" usando la prioridad
                if (pedidos_validos[point].indicador == 1 and  # Solo aplicar a "Pick-ups"
                    increase > parametros["max_aumento_distancia"] * (minuto_actual / parametros["tiempo_necesario_pick_up"]) and 
                    minuto_actual < parametros["tiempo_necesario_pick_up"]):
                    print("Se rechaza Pick Up")
                    continue  # Rechazar el Pick-up

                # 4.3 Criterio de rechazo simplificado para "Deliveries"
                if (pedidos_validos[point].indicador == 0 and  # Solo aplicar a "Deliveries"
                    (calcular_prioridad(pedidos_validos[point]) > parametros["tiempo_restante_max"] and  # Queda mucho tiempo
                    increase > parametros["max_aumento_distancia_delivery"])):  # Incremento de distancia es demasiado grande
                    print("Se rechaza deliverie")
                    continue  # Rechazar el Delivery
                # 4.4 Construir la ruta temporal y calcular el tiempo de llegada al nuevo punto
                ruta_temporal = [depot] + [pedidos_validos[j].coordenadas for j in route[:i]] + \
                                [pedidos_validos[point].coordenadas] + [pedidos_validos[j].coordenadas for j in route[i:]] + \
                                [depot]
                tiempo_total = calcular_tiempo_ruta(ruta_temporal, camion.velocidad)
                tiempo_llegada_punto = minuto_actual + tiempo_total

                # Verificar si el camión puede llegar a tiempo al nuevo punto
                pedido = pedidos_validos[point]
                if (tiempo_llegada_punto <= pedido.minuto_llegada + tiempo_limite and
                    verificar_llegada_a_tiempo(camion, ruta_temporal, minuto_actual)):
                    # Elegir este punto si el incremento de distancia es el menor
                    if increase < min_increase:
                        min_increase = increase
                        best_position = i
                        best_point = point

        # Si no se encuentra una inserción válida, termina el proceso
        if best_position is None or best_point is None:
            break

        # Inserta el mejor punto en la posición óptima
        route.insert(best_position, best_point)
        unvisited.remove(best_point)  # Marca el punto como visitado

    # Añadir el depot al final de la ruta
    route.append(0)

    # Retornar la ruta con las coordenadas de los puntos
    return [depot] + [pedidos_validos[i].coordenadas for i in route if i != 0] + [depot]

# Función para verificar si el camión puede completar la ruta a tiempo
def verificar_llegada_a_tiempo(camion, ruta, minuto_actual):
    tiempo_total = calcular_tiempo_ruta(ruta, camion.velocidad)
    if minuto_actual + tiempo_total > 1020:  # Verifica si se pasa de las 7 PM (1020 minutos)
        return False
    return True

# Función para calcular la distancia total de una ruta
def total_distance(route):
    dist = 0
    for i in range(len(route) - 1):
        dist += euclidean_distance(route[i], route[i + 1])
    return dist


def two_opt(route):
    best_route = route
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:  # No intercambiar nodos consecutivos
                    continue
                new_route = (
                    best_route[:i] +
                    best_route[i:j][::-1] +
                    best_route[j:]
                )
                if total_distance(new_route) < total_distance(best_route):
                    best_route = new_route
                    improved = True
    return best_route

# Función de 3-opt
def three_opt(route):
    n = len(route)
    improved = True

    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    new_route = (route[:i] + 
                                route[j:k][::-1] +  # Reversa del segmento
                                route[i:j] + 
                                route[k:])
                    if total_distance(new_route) < total_distance(route):
                        route = new_route
                        improved = True
    return route

# Graficar las rutas
def graficar_rutas(ruta_cheapest, distancia_cheapest, ruta_3opt, distancia_3opt):
    # Extraer las coordenadas de las rutas
    x_cheapest, y_cheapest = zip(*ruta_cheapest)
    x_3opt, y_3opt = zip(*ruta_3opt)

    # Crear el gráfico
    plt.figure(figsize=(10, 6))
    
    # Graficar la ruta Cheapest Insertion
    plt.plot(x_cheapest, y_cheapest, marker='o', label=f'Cheapest Insertion\nDistancia total: {distancia_cheapest}', color='blue')
    
    # Graficar la ruta 3-opt
    plt.plot(x_3opt, y_3opt, marker='o', label=f'3-opt\nDistancia total: {distancia_3opt}', color='orange')
    
    # Añadir etiquetas y leyenda
    plt.title('Comparación de Rutas')
    plt.xlabel('Coordenadas X')
    plt.ylabel('Coordenadas Y')
    plt.legend()
    plt.grid()
    plt.axis('equal')  # Para que los ejes sean de la misma escala
    plt.show()

def generar_ruta(points, depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=180):
    ruta = cheapest_insertion(points, depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=180)  # Pasa la ubicación del depot
    #ruta = two_opt(ruta)
    ruta = three_opt(ruta)

    return ruta

def calcular_tiempo_regreso(velocidad, distancia):
    tiempo = distancia / velocidad
    return tiempo


def vence_el_pedido(pedido, tiempo_llegada_punto, tiempo_limite):
    if pedido.indicador == 0:
        if (tiempo_llegada_punto <= pedido.minuto_llegada + tiempo_limite):
            return False
    return True