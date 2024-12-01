import numpy as np
import matplotlib.pyplot as plt
from funciones_complementarias import *


#Calcular prioridad para poder ver que pedidos priorizar de los deliveries
def calcular_prioridad(pedido, minuto_actual):
        if pedido.indicador == 0:  # Delivery
            tiempo_restante = 195 - (minuto_actual - pedido.minuto_llegada)
            return tiempo_restante
        else:  # Pick-up
            return(195)

#Calcula en el minuto que se llega a cada punto de la ruta para luego ver si es factible agregar ese punto, se usa para rutear e incorporar pickup
def calculate_arrival_times(ruta_indices, pedidos_validos, depot, camion_velocidad, minuto_actual, service_time=3):
        arrival_times = []
        current_time = minuto_actual
        current_location = depot

        # Para cada punto en la ruta
        for idx in ruta_indices:
            pedido = pedidos_validos[idx]
            next_location = pedido.coordenadas

            # Calcular el tiempo de viaje al siguiente punto
            distance = manhattan_distance(current_location, next_location)
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
        distance = manhattan_distance(current_location, depot)
        travel_time = distance / camion_velocidad
        current_time += travel_time  # Sumar tiempo para regresar al depósito

        return arrival_times, current_time  # Retorna los tiempos de llegada y el tiempo total

# Algoritmo de Cheapest Insertion corregido con la heuristica de ruteo (Descarta el pedido si no es urgente y empeora mucho la ruta)
def cheapest_insertion(tiempo_total, unvisited, route, pedidos_validos, depot, camion, minuto_actual, parametros, tiempo_limite=195):
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
                    ruta_temporal, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=3
                )

                # Verificar si la ruta temporal cumple con el horizonte de tiempo
                if total_time_temp > 1019:
                    continue  # No se puede insertar el punto en esta posición

                # Verificar que podemos llegar a todos los puntos antes de que venzan
                all_points_valid = True
                for idx_ruta, arrival_time in zip(ruta_temporal, arrival_times_temp):
                    pedido_ruta = pedidos_validos[idx_ruta]
                    if pedido_ruta.indicador == 0:
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
                    calcular_prioridad(pedidos_validos[point], minuto_actual) > parametros["tiempo_restante_max"] and
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


#Funcion que hace el primer llamado a cheapest insertion y hace la entrega de un punto valido para luego crear la ruta
def generar_ruta(depot, camion, minuto_actual, pedidos_disponibles, parametros, tiempo_limite=195):
    # Calcular prioridades de los pedidos
    def calcular_prioridad(pedido):
        if pedido.indicador == 0:  # Delivery
            tiempo_restante = 195 - (minuto_actual - pedido.minuto_llegada)
            return tiempo_restante
        else:  # Pick-up
            return(195)

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
        dist = manhattan_distance(depot, pedido.coordenadas)
        if dist < min_dist:
            min_dist = dist
            first_point = i

    # Añadir el pedido más cercano a la ruta
    route.append(first_point)
    unvisited = set(range(len(pedidos_validos))) - {first_point}

    # Calcular los tiempos de llegada y tiempo total de la ruta inicial
    arrival_times, tiempo_total = calculate_arrival_times(route, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=3)

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

    ruta = cheapest_insertion(tiempo_total, unvisited, route, pedidos_validos, depot, camion, minuto_actual, parametros, tiempo_limite=195)  # Pasa la ubicación del depot

    return ruta

#Cheapest insertion que se usa para el caso base
def cheapest_insertion_caso_base(points, depot, camion, minuto_actual, pedidos_disponibles, tiempo_limite=195):
    """
    Algoritmo de Cheapest Insertion para el caso base, sin ordenamiento de prioridad
    y sin rechazo de "Pick-ups" y "Deliveries".

    - No se permite recoger pedidos vencidos.
    - El camión debe regresar antes del minuto 1020.
    """

    def calculate_arrival_times(ruta_indices, pedidos_validos, depot, camion_velocidad, minuto_actual, service_time=3):
        arrival_times = []
        current_time = minuto_actual
        current_location = depot

        for idx in ruta_indices:
            pedido = pedidos_validos[idx]
            next_location = pedido.coordenadas
            distance = manhattan_distance(current_location, next_location)
            travel_time = distance / camion_velocidad
            arrival_time = current_time + travel_time
            current_time = arrival_time + service_time
            arrival_times.append(arrival_time)
            current_location = next_location

        distance = manhattan_distance(current_location, depot)
        travel_time = distance / camion_velocidad
        current_time += travel_time
        return arrival_times, current_time

    pedidos_validos = [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]
    if not pedidos_validos:
        return [depot, depot]

    route = []
    min_dist = float('inf')
    first_point = None
    for i, pedido in enumerate(pedidos_validos):
        dist = manhattan_distance(depot, pedido.coordenadas)
        if dist < min_dist:
            min_dist = dist
            first_point = i

    route.append(first_point)
    unvisited = set(range(len(pedidos_validos))) - {first_point}
    arrival_times, tiempo_total = calculate_arrival_times(route, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=3)

    pedido = pedidos_validos[first_point]
    expiration_time = pedido.minuto_llegada + tiempo_limite
    if arrival_times[0] > expiration_time or tiempo_total > 1020:
        return [depot, depot]

    while unvisited:
        min_increase = float('inf')
        best_position = None
        best_point = None

        for point in unvisited:
            for i in range(len(route) + 1):
                ruta_temporal = route.copy()
                ruta_temporal.insert(i, point)
                arrival_times_temp, total_time_temp = calculate_arrival_times(ruta_temporal, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=5)

                if total_time_temp > 1020:
                    continue

                all_points_valid = True
                for idx_ruta, arrival_time in zip(ruta_temporal, arrival_times_temp):
                    pedido_ruta = pedidos_validos[idx_ruta]
                    expiration_time_ruta = pedido_ruta.minuto_llegada + tiempo_limite
                    if arrival_time > expiration_time_ruta:
                        all_points_valid = False
                        break

                if not all_points_valid:
                    continue

                increase = total_time_temp - tiempo_total

                if increase < min_increase:
                    min_increase = increase
                    best_position = i
                    best_point = point
                    best_total_time = total_time_temp
                    best_arrival_times = arrival_times_temp

        if best_point is not None:
            route.insert(best_position, best_point)
            unvisited.remove(best_point)
            tiempo_total = best_total_time
            arrival_times = best_arrival_times
        else:
            break

    ruta_final_coords = [depot] + [pedidos_validos[idx].coordenadas for idx in route] + [depot]
    return ruta_final_coords



##########Ruteo para la incorporacion de pick ups dinamicos ###############


def cheapest_insertion_adaptacion(
    minuto_actual, parametros, camion, current_index, pedidos_validos, ruta_actual, todos_los_pedidos, tiempo_limite=195):
    # Obtener la ubicación y el tiempo actual del camión
    current_location = ruta_actual[current_index]
    
    # Calcular el tiempo de llegada al punto actual
    arrival_times_up_to_current, _ = calculate_arrival_times_adapted(
        ruta_actual[:current_index + 1],
        camion.velocidad,
        camion.tiempo_inicio_ruta,
        [10000, 10000],
        service_time=3
    )

    # Lista de pedidos ya en la ruta actual (desde current_index + 1 hasta el final)
    ruta_actual_aux = ruta_actual[current_index + 1:]
    ruta_actual_aux = [cord for cord in ruta_actual_aux if not np.array_equal(cord, [10000, 10000])]

    pedidos_en_ruta = []
    for cord in ruta_actual_aux:
        pedidos_en_punto = [pedido for pedido in todos_los_pedidos if np.array_equal(pedido.coordenadas, cord)]
        if pedidos_en_punto:
            pedidos_en_ruta.append(pedidos_en_punto[0])
        else:
            print(f"No se encontró un pedido para el punto {cord}")

    # Crear una lista combinada de pedidos totales sin duplicados
    pedidos_totales = pedidos_en_ruta.copy()
    for pedido in pedidos_validos:
        if pedido not in pedidos_totales:
            pedidos_totales.append(pedido)

    # Mapear pedidos a sus índices en pedidos_totales
    pedido_a_indice = {pedido: idx for idx, pedido in enumerate(pedidos_totales)}

    # Índices de los pedidos ya en la ruta (inicialmente)
    indices_route = [pedido_a_indice[pedido] for pedido in pedidos_en_ruta]

    # Índices de los nuevos pedidos a considerar para inserción
    unvisited = [pedido_a_indice[pedido] for pedido in pedidos_validos if pedido not in pedidos_en_ruta]

    # Calcular el tiempo total restante sin nuevos pickups
    ruta_remaining_coords = [pedido.coordenadas for pedido in pedidos_en_ruta]
    arrival_times_remaining, tiempo_total_remaining = calculate_arrival_times_adapted(
        ruta_remaining_coords,
        camion.velocidad,
        minuto_actual,
        current_location,
        service_time=3
    )
    tiempo_total = tiempo_total_remaining
    p_insertados = 0
    max_insertados = 1
    while unvisited and p_insertados < max_insertados:
        min_increase = float('inf')
        best_position = None
        best_point = None
        best_total_time = None
        best_arrival_times = None

        # Buscar el mejor punto para insertar
        for point in unvisited:
            if point in indices_route:
                continue
            for i in range(len(indices_route) + 1):
                ruta_temporal = indices_route.copy()
                ruta_temporal.insert(i, point)

                # Construir la ruta completa temporal
                ruta_compl_temp_coords = [current_location] + [pedidos_totales[idx].coordenadas for idx in ruta_temporal]

                # Calcular tiempos de llegada y tiempo total de la ruta
                arrival_times_temp, total_time_temp = calculate_arrival_times_adapted(
                    ruta_compl_temp_coords,
                    camion.velocidad,
                    minuto_actual,
                    current_location,
                    service_time=3
                )

                # Verificar si cumple con el horizonte de tiempo
                if total_time_temp > 1019:
                    continue

                # Verificar que todos los puntos pueden atenderse antes de su vencimiento
                all_points_valid = True
                for idx_ruta, arrival_time in zip(ruta_temporal, arrival_times_temp):
                    pedido_ruta = pedidos_totales[idx_ruta]
                    expiration_time_ruta = pedido_ruta.minuto_llegada + tiempo_limite
                    if arrival_time > expiration_time_ruta:
                        all_points_valid = False
                        break

                if not all_points_valid:
                    continue

                # Calcular incremento en tiempo
                increase = total_time_temp - tiempo_total

                # Rechazo para "Pick-ups"
                # Verificar que ningún delivery planeado sea afectado por la inserción del pickup
                if pedidos_totales[point].indicador == 1:  # Pickup
                    if any(
                        pedidos_totales[idx].indicador == 0 and arrival_time > pedidos_totales[idx].minuto_llegada + tiempo_limite
                        for idx, arrival_time in zip(ruta_temporal, arrival_times_temp)
                    ):
                        continue  # Rechazar la inserción si afecta algún delivery

                # Rechazo para "Pick-ups"
                if (pedidos_totales[point].indicador == 1 and
                    increase > parametros['max_aumento_distancia_en_ruta'] * (minuto_actual / parametros['tiempo_necesario_pick_up_en_ruta']) and
                    minuto_actual < parametros['tiempo_necesario_pick_up_en_ruta']):
                    print('pick up rechazado por no ser conveniente')
                    continue


                # Elegir este punto si el incremento es el menor
                if increase < min_increase:
                    min_increase = increase
                    best_position = i
                    best_point = point
                    best_total_time = total_time_temp
                    best_arrival_times = arrival_times_temp

        # Si se encuentra un punto para insertar
        if best_point is not None:
            indices_route.insert(best_position, best_point)
            unvisited.remove(best_point)
            tiempo_total = best_total_time
            arrival_times = best_arrival_times
            p_insertados +=1
            print('SE ENCONTRO PUNTO')
        else:
            print('NO HAY PUNTO')
            break

    # Construir la ruta final
    ruta_final_coords = ruta_actual[:current_index + 1] + [pedidos_totales[idx].coordenadas for idx in indices_route] + [[10000, 10000]]
    return ruta_final_coords

def calculate_arrival_times_adapted(ruta_coords, camion_velocidad, current_time, current_location, service_time=3):
    arrival_times = []

    # Para cada punto en la ruta
    for coord in ruta_coords:
        next_location = coord

        # Calcular el tiempo de viaje al siguiente punto
        distance = manhattan_distance(current_location, next_location)
        travel_time = distance / camion_velocidad

        # Tiempo de llegada al siguiente punto
        arrival_time = current_time + travel_time

        # Almacenar el tiempo de llegada
        arrival_times.append(arrival_time)

        # Actualizar el tiempo actual sumando el tiempo de atención
        current_time = arrival_time + service_time

        # Actualizar la ubicación actual
        current_location = next_location

    # Finalmente, regresar al depósito
    distance = manhattan_distance(current_location, [10000, 10000])
    travel_time = distance / camion_velocidad
    current_time += travel_time  # Sumar tiempo para regresar al depósito

    return arrival_times, current_time # Retorna los tiempos de llegada y el tiempo total

def hora_entrega_pedidos(ruta, depot, camion_velocidad, minuto_actual, service_time=3):
    arrival_times = []
    current_time = minuto_actual
    current_location = depot

    # Para cada punto en la ruta
    for punto in ruta:
        next_location = punto

        # Calcular el tiempo de viaje al siguiente punto
        distance = manhattan_distance(current_location, next_location)
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
    distance = manhattan_distance(current_location, depot)
    travel_time = distance / camion_velocidad
    current_time += travel_time  # Sumar tiempo para regresar al depósito

    return arrival_times, current_time  # Retorna los tiempos de llegada y el tiempo total

