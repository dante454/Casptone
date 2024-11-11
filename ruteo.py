import numpy as np
import matplotlib.pyplot as plt
from funciones_caso_base import *

# Función para calcular la distancia euclidiana entre dos puntos
def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# Algoritmo de Cheapest Insertion corregido
def cheapest_insertion(points, depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=180):
    """
    Algoritmo de Cheapest Insertion modificado para manejar prioridades y rechazar "Pick-ups" y "Deliveries",
    con verificación de tiempos de vencimiento al insertar puntos.
    """

    # Función para calcular los tiempos de llegada a cada punto en una ruta
    def calculate_arrival_times(ruta_indices, pedidos_validos, depot, camion_velocidad, minuto_actual, service_time=5):
        arrival_times = []
        current_time = minuto_actual
        current_location = depot

        # Para cada punto en la ruta
        for idx in ruta_indices:
            pedido = pedidos_validos[idx]
            next_location = pedido.coordenadas

            # Calcular el tiempo de viaje al siguiente punto
            distance = euclidean_distance(current_location, next_location)
            travel_time = distance / camion_velocidad

            # Tiempo de llegada al siguiente punto
            arrival_time = current_time + travel_time

            # Actualizar el tiempo actual sumando el tiempo de viaje y el tiempo de atención
            current_time = arrival_time + service_time

            # Almacenar el tiempo de llegada (antes del servicio)
            arrival_times.append(arrival_time)

            # Actualizar la ubicación actual
            current_location = next_location

        # Finalmente, regresar al depósito
        distance = euclidean_distance(current_location, depot)
        travel_time = distance / camion_velocidad
        current_time += travel_time  # Sumar tiempo para regresar al depósito

        return arrival_times, current_time  # Retorna los tiempos de llegada y el tiempo total

    # Calcular prioridades de los pedidos
    def calcular_prioridad(pedido):
        if pedido.indicador == 0:  # Delivery
            tiempo_restante = 180 - (minuto_actual - pedido.minuto_llegada)
            return tiempo_restante
        else:  # Pick-up
            tiempo_transcurrido = minuto_actual - 520  # Desde el inicio de la simulación
            return max(0, tiempo_transcurrido)

    # Ordenar pedidos por prioridad
    pedidos_disponibles = sorted(pedidos_disponibles, key=calcular_prioridad, reverse=False)
    # Filtrar pedidos válidos dentro del tiempo límite de vencimiento
    pedidos_validos = [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]

    if not pedidos_validos:
        return [depot, depot]  # No hay pedidos válidos

    # Inicializar ruta vacía
    route = []

    # Encontrar el pedido más cercano al depósito para comenzar
    min_dist = float('inf')
    first_point = None
    for i, pedido in enumerate(pedidos_validos):
        dist = euclidean_distance(depot, pedido.coordenadas)
        if dist < min_dist:
            min_dist = dist
            first_point = i

    # Añadir el pedido más cercano a la ruta
    route.append(first_point)
    unvisited = set(range(len(pedidos_validos))) - {first_point}

    # Calcular los tiempos de llegada y tiempo total de la ruta inicial
    arrival_times, tiempo_total = calculate_arrival_times(route, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=5)

    # Verificar que podemos llegar al primer punto antes de que venza
    pedido = pedidos_validos[first_point]
    expiration_time = pedido.minuto_llegada + tiempo_limite
    if arrival_times[0] > expiration_time:
        print("No se puede llegar al primer pedido antes de que venza")
        return [depot, depot]  # No se puede realizar ninguna ruta

    # Verificar si la ruta inicial cumple con el horizonte de tiempo
    if tiempo_total > 1020:
        print("La ruta inicial excede el horizonte de tiempo")
        return [depot, depot]  # No se puede realizar ninguna ruta

    # Proceso de inserción con prioridades y rechazo inteligente
    while unvisited:
        min_increase = float('inf')
        best_position = None
        best_point = None

        # Buscar el mejor punto para insertar
        for point in unvisited:
            # Intentar insertar el punto en cada posición posible
            for i in range(len(route) + 1):
                # Crear una ruta temporal con el nuevo punto insertado
                ruta_temporal = route.copy()
                ruta_temporal.insert(i, point)

                # Calcular los tiempos de llegada y el tiempo total de la ruta temporal
                arrival_times_temp, total_time_temp = calculate_arrival_times(
                    ruta_temporal, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=5
                )

                # Verificar si la ruta temporal cumple con el horizonte de tiempo
                if total_time_temp > 1020:
                    continue  # No se puede insertar el punto en esta posición

                # Verificar que podemos llegar a todos los puntos antes de que venzan
                all_points_valid = True
                for idx_ruta, arrival_time in zip(ruta_temporal, arrival_times_temp):
                    pedido_ruta = pedidos_validos[idx_ruta]
                    expiration_time_ruta = pedido_ruta.minuto_llegada + tiempo_limite
                    if arrival_time > expiration_time_ruta:
                        # No se puede llegar a este punto antes de que venza
                        all_points_valid = False
                        break

                if not all_points_valid:
                    continue  # No considerar esta inserción

                # Calcular el incremento en el tiempo respecto a la ruta actual
                increase = total_time_temp - tiempo_total

                # Rechazo para "Pick-ups"
                if (pedidos_validos[point].indicador == 1 and
                    increase > parametros["max_aumento_distancia"] * (minuto_actual / parametros["tiempo_necesario_pick_up"]) and
                    minuto_actual < parametros["tiempo_necesario_pick_up"]):
                    continue  # Intentar con otro punto

                # Rechazo para "Deliveries"
                if (pedidos_validos[point].indicador == 0 and
                    calcular_prioridad(pedidos_validos[point]) > parametros["tiempo_restante_max"] and
                    increase > parametros["max_aumento_distancia_delivery"]):
                    continue  # Intentar con otro punto

                # Elegir este punto si el incremento es el menor hasta ahora
                if increase < min_increase:
                    min_increase = increase
                    best_position = i
                    best_point = point
                    best_total_time = total_time_temp
                    best_arrival_times = arrival_times_temp

        # Si encontramos un punto para insertar
        if best_point is not None:
            # Insertar el punto en la ruta
            route.insert(best_position, best_point)
            unvisited.remove(best_point)
            # Actualizar tiempo_total y arrival_times
            tiempo_total = best_total_time
            arrival_times = best_arrival_times
        else:
            # No se puede insertar ningún punto sin exceder el tiempo o causar vencimiento de pedidos
            break

    # Construir la ruta final
    ruta_final_coords = [depot] + [pedidos_validos[idx].coordenadas for idx in route] + [depot]

    return ruta_final_coords

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
    #ruta = three_opt(ruta)

    return ruta

def calcular_tiempo_regreso(velocidad, distancia):
    tiempo = distancia / velocidad
    return tiempo


def vence_el_pedido(pedido, tiempo_llegada_punto, tiempo_limite):
    if pedido.indicador == 0:
        if (tiempo_llegada_punto <= pedido.minuto_llegada + tiempo_limite):
            return False
    return True