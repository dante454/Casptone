import numpy as np
from ruteo import *
import pickle
import matplotlib.pyplot as plt
from funciones_caso_base import *


def calcular_beneficio_maximo(simulacion):
        """Calcula el beneficio máximo posible hasta el minuto actual."""
        return sum(
            1 if pedido.indicador == 1 else 2 
            for pedido in (simulacion.pedidos_entregados + simulacion.pedidos_disponibles + simulacion.pedidos_no_disponibles)
        )
#Separa los pedidos en la areas asignadas por los parametros
def separar_y_seleccionar_area(pedidos_disponibles):
    # Separar los pedidos según su área
    pedidos_area1 = [pedido for pedido in pedidos_disponibles if pedido.area == 1]
    pedidos_area2 = [pedido for pedido in pedidos_disponibles if pedido.area == 2]
    pedidos_area3 = [pedido for pedido in pedidos_disponibles if pedido.area == 3]

    # Calcular cuál área tiene más pedidos
    max_area = max(len(pedidos_area1), len(pedidos_area2), len(pedidos_area3))

    if max_area == len(pedidos_area1):
        return pedidos_area1
    elif max_area == len(pedidos_area2):
        return pedidos_area2
    else:
        return pedidos_area3


#Maneja el flujo de desiciones desde que se toma la decision de salir a repartir
def flujo_ruteo(camion, simulacion, parametros):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    depot = [10000, 10000]
    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta(depot, camion, simulacion.minuto_actual, pedidos_a_rutear, parametros, tiempo_limite=195)

    #  5. Si no hay puntos en la ruta, no hacer nada
    if len(ruta) <= 2:
        return

    # 6. Reiniciar el contador de pickups dinámicos para la nueva ruta
    camion.pickups_actuales = 0
    camion.pickups_evaluados = False

    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta, simulacion.minuto_actual)

    # 9. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta

# Función para actualizar el estado de la simulación, marcando los puntos de la ruta como visitados
def actualizar_estado_simulacion(simulacion, ruta):
    # Lista para almacenar los pedidos que se entregarán
    pedidos_a_entregar = []
    
    # Para cada punto en la ruta, buscar el pedido correspondiente en pedidos disponibles
    for punto in ruta:

        pedidos_en_punto = [pedido for pedido in simulacion.pedidos_disponibles if np.array_equal(pedido.coordenadas, punto)]
        pedidos_a_entregar.extend(pedidos_en_punto)

    index = []
    for i in range (len(pedidos_a_entregar)):
        index.append(i)

    arraival_times, _ = calculate_arrival_times(index, pedidos_a_entregar, [10000, 10000], ((25 * 1000) / 60), simulacion.minuto_actual, service_time=3)
    # Actualizar el estado de los pedidos y las listas de la simulación
    x = 0
    for pedido in pedidos_a_entregar:
        # Cambiar el estado del pedido a entregado
        minuto_entrega = arraival_times[x]
        pedido.entregar(minuto_entrega)
        # Mover el pedido a la lista de pedidos entregados
        simulacion.pedidos_entregados.append(pedido)
        x += 1

    # Remover los pedidos entregados de la lista de pedidos disponibles
    simulacion.pedidos_disponibles = [pedido for pedido in simulacion.pedidos_disponibles if pedido not in pedidos_a_entregar]

#Simula minuto a minuto todo lo que va pasando dinamicamente
def simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3):
    
    for minuto in range(520, 1020 + 1):
        simulacion.minuto_actual = minuto
        print(f"Minuto {minuto}: simulando...")

        if minuto <= 650:
            parametros = parametros_ventana_1
        elif 651 <= minuto <= 780:
            parametros = parametros_ventana_2
        else:
            parametros = parametros_ventana_3
        # Actualizar los pedidos disponibles minuto a minuto
        simulacion.revisar_pedidos_disponibles()
        velocidad_camion = ((25 * 1000) / 60)
        simulacion.tercerizar_pedido([10000,10000],velocidad_camion)


        # Actualizar tiempos de los camiones
        for camion in camiones:
            camion.actualizar_tiempo()
            
        # Evaluar si los camiones deben salir a rutear
        for camion in camiones:
            if evaluar_salida(camion, simulacion, parametros):
                # Gestionar el camión cuando sale a realizar una ruta
                flujo_ruteo(camion, simulacion, parametros)
        
        # Cada 10 minutos, calcular el porcentaje de beneficio captado
        if minuto % 10 == 0:
            beneficio_acumulado = simulacion.calcular_beneficio_acumulado()
            porcentaje_beneficio = simulacion.calcular_porcentaje_beneficio(beneficio_acumulado)
            simulacion.beneficio_por_intervalo.append((minuto, porcentaje_beneficio))

            pedidos_totales = simulacion.pedidos_disponibles + simulacion.pedidos_entregados + simulacion.pedidos_no_disponibles

            total_deliveries = sum(1 for pedido in pedidos_totales if pedido.indicador == 0)
            total_pickups = sum(1 for pedido in pedidos_totales if pedido.indicador == 1)

            completados_deliveries = sum(
                1 for pedido in simulacion.pedidos_entregados
                if pedido.indicador == 0 and pedido.tiempo_entrega <= minuto
            )
            completados_pickups = sum(
                1 for pedido in simulacion.pedidos_entregados
                if pedido.indicador == 1 and pedido.tiempo_entrega <= minuto
            )

            porcentaje_deliveries = (completados_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
            porcentaje_pickups = (completados_pickups / total_pickups) * 100 if total_pickups > 0 else 0

            # Guardar los porcentajes en los atributos de simulación
            simulacion.deliveries_intervalos.append((minuto, porcentaje_deliveries))
            simulacion.pickups_intervalos.append((minuto, porcentaje_pickups))



        # Avanza el minuto en la simulación
        simulacion.avanzar_minuto(parametros)
        simulacion.registrar_estado(camiones)
    

    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)
    beneficio_total_disponible = calcular_beneficio_maximo(simulacion)
    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta) if tiempos_respuesta else 0

    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)
    #print(len(simulacion.pedidos_entregados))
    print("Simulación finalizada.")
    print(f"Simulación finalizada. Beneficio total: {beneficio_total}/{beneficio_total_disponible}")
    print(f"Distancia total recorrida: {distancia_total} metros")
    print(f"Tiempo promedio de respuesta: {tiempo_respuesta_promedio:.2f} minutos")
    print(f"Cantidad de pickups realizados: {cantidad_pickups}")
    print(f"Cantidad de deliveries realizados: {cantidad_deliveries}")

# Función que evalúa los criterios de salida de los camiones
def evaluar_salida(camion, simulacion, parametros):
    if camion.tiempo_restante > 0:
        evaluar_incorporacion_pickup(camion, parametros, simulacion)
        return False

    if len(simulacion.pedidos_disponibles) == 0:
        return False

    # Calcula el valor ponderado de los criterios
    valor_ponderado = (
        parametros["peso_min_pedidos"] * (len(simulacion.pedidos_disponibles) / max(1, parametros["min_pedidos_salida"])) +
        parametros["peso_ventana_tiempo"] * (simulacion.minuto_actual % parametros["x_minutos"] == 0)
    )

    # Verifica si el valor ponderado supera el umbral
    return valor_ponderado >= parametros["umbral_salida"]


# Aqui se encuentran todas las funciones relacionadas a la incorporacion del pick up
# evaluar incorporacion de pick up y pick up nuevos disponibles.

def evaluar_incorporacion_pickup(camion, parametros, simulacion):
    # Límite de pickups dinámicos permitidos por ruta dependiendo de instancia

    # Verificar si ya se alcanzó el límite de pickups dinámicos
    if camion.pickups_actuales >= parametros['maximo_incorporacion_pick_up']:
        print(f"Camión {camion.id}: Límite de {parametros['maximo_incorporacion_pick_up']} pickups dinámicos alcanzado para esta ruta.")
        return

    # Verificar si ya se evaluaron los pick-ups para esta ruta
    if camion.pickups_evaluados:
        return  # No se realiza ninguna acción si ya se evaluaron los pick-ups

    ruta_actual = camion.rutas[-1]
    total_puntos_ruta = len(ruta_actual) - 1  # Excluimos el depósito final
    punto_medio_index = total_puntos_ruta // 2  # Índice del punto medio

    # Obtener solo la lista de tiempos de llegada (primer elemento de la tupla)
    minutos_de_entrega, _ = hora_entrega_pedidos(ruta_actual, [10000, 10000], camion.velocidad, camion.tiempo_inicio_ruta, service_time=3)
    tiempo_actual = simulacion.minuto_actual

    # Verificar si el camión está en el punto medio de la ruta
    if punto_medio_index < len(minutos_de_entrega):
        tiempo_llegada_punto_medio = minutos_de_entrega[punto_medio_index]
        if tiempo_actual >= tiempo_llegada_punto_medio and tiempo_actual < tiempo_llegada_punto_medio + 3:  # En rango de atención del punto medio
            # Llamar a la función para añadir pickups dinámicos
            nueva_ruta = pick_up_nuevos_disponible(camion, parametros, simulacion, punto_medio_index)
            
            # Contar los pickups añadidos dinámicamente
            if nueva_ruta:
                nuevos_pickups = len(nueva_ruta) - len(camion.rutas[-1])
                camion.pickups_actuales += nuevos_pickups
                print(f"Camión {camion.id}: Se añadieron {nuevos_pickups} pickups dinámicos. Total actuales: {camion.pickups_actuales}")

            # Marcar que los pick-ups ya fueron evaluados para esta ruta
            camion.pickups_evaluados = True
            return
    else:
        # Si por alguna razón el índice está fuera de rango, no hacemos nada
        return


def pick_up_nuevos_disponible(camion, parametros, simulacion, current_index):
    # Límite de pickups dinámicos permitidos por ruta dependiendo de instancia
    if instancia_archivo == 'Instancia Tipo I':
        max_pickups_dinamicos = 20
    else:
        max_pickups_dinamicos = 5

    # Verificar si se ha alcanzado el límite
    if camion.pickups_actuales >= max_pickups_dinamicos:
        print(f"Camión {camion.id}: Límite de {max_pickups_dinamicos} pickups dinámicos alcanzado.")
        return camion.rutas[-1]  # Devolver la ruta actual sin cambios

    # Verificar si hay pedidos disponibles
    if not simulacion.pedidos_disponibles:
        print(f"No hay solicitudes de pick-up disponibles en el minuto {simulacion.minuto_actual}.")
        return camion.rutas[-1]  # Devolver la ruta actual sin cambios

    nuevos_pickups = []

    # Identificar los nuevos pick-ups disponibles
    for pedido in simulacion.pedidos_disponibles:
        if pedido.indicador == 1 and pedido.disponible == 1:  # Solo pick-ups disponibles
            nuevos_pickups.append(pedido)

    # Si hay nuevos pickups disponibles, verificar límite antes de proceder
    if nuevos_pickups:
        # Verificar cuántos pickups más podemos agregar
        pickups_restantes = max_pickups_dinamicos - camion.pickups_actuales
        nuevos_pickups = nuevos_pickups[:pickups_restantes]  # Limitar la lista a lo permitido

        # Calcular la nueva ruta con los pickups seleccionados
        unvisited = set(range(len(nuevos_pickups)))
        todos_los_pedidos = simulacion.pedidos_disponibles + simulacion.pedidos_entregados
        nueva_ruta = cheapest_insertion_adaptacion(
            simulacion.minuto_actual, parametros, camion, current_index,
            nuevos_pickups, camion.rutas[-1], todos_los_pedidos, tiempo_limite=195
        )

        # Comparar la nueva ruta con la actual
        def listas_identicas(lista1, lista2):
            if len(lista1) != len(lista2):
                print("Las rutas tienen diferente largo")
                return False
            return all(np.array_equal(arr1, arr2) for arr1, arr2 in zip(lista1, lista2))

        # Si la nueva ruta tiene cambios, actualizamos la ruta del camión
        if not listas_identicas(nueva_ruta, camion.rutas[-1]):
            print("Se cambió la ruta por nueva solicitud de pick up")
            puntos_nuevos = [
                punto for punto in nueva_ruta if not any(np.array_equal(punto, p_antiguo) for p_antiguo in camion.rutas[-1])
            ]
            camion.rutas[-1] = nueva_ruta
            ruta_restante = nueva_ruta[current_index:]
            actualizar_estado_simulacion(simulacion, ruta_restante)

            # Incrementar el conteo de pickups actuales del camión
            camion.pickups_actuales += len(nuevos_pickups)
            print(f"Camión {camion.id}: Se agregaron {len(nuevos_pickups)} pickups. Total pickups dinámicos: {camion.pickups_actuales}")

            # Calcular el nuevo tiempo restante
            _, tiempo_total_nueva_ruta = calculate_arrival_times_adapted(
                nueva_ruta, camion.velocidad, camion.tiempo_inicio_ruta, [10000, 10000], service_time=3
            )
            camion.tiempo_restante = max(0, tiempo_total_nueva_ruta - simulacion.minuto_actual)

        return camion.rutas[-1]  # Devolver la nueva ruta actualizada

    else:
        print(f"No hay nuevas solicitudes de pick-up disponibles en el minuto {simulacion.minuto_actual}.")
        return camion.rutas[-1]  # Devolver la ruta actual sin cambios



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

def verificar_pedidos_repetidos(pedidos_entregados):
    print(len(pedidos_entregados))

    pedidos_vistos = set()
    pedidos_repetidos = []
    pic = 0
    deli = 0

    for pedido in pedidos_entregados:
        if pedido.indicador == 0:
            deli +=1
        elif pedido.indicador == 1:
            pic +=1
        # Convertir las coordenadas del pedido en una tupla para que sean hashables
        coordenadas = tuple(pedido.coordenadas)
        if coordenadas in pedidos_vistos:
            pedidos_repetidos.append(pedido)
        else:
            pedidos_vistos.add(coordenadas)
    print(pic)
    print(deli)
    return pedidos_repetidos






# Parámetros de la simulación (ajustables por Optuna)
parametros_ventana_1 = {'min_pedidos_salida': 8, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016, 'tiempo_necesario_pick_up_en_ruta': 1300, 'max_aumento_distancia_en_ruta': 0, 'maximo_incorporacion_pick_up': 10}

parametros_ventana_2 = {'min_pedidos_salida': 5, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000, 'maximo_incorporacion_pick_up': 0}

parametros_ventana_3 = {'min_pedidos_salida': 1, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556, 'tiempo_necesario_pick_up_en_ruta': 1300, 'max_aumento_distancia_en_ruta': 0, 'maximo_incorporacion_pick_up': 10}


instancia_archivo = 'Instancia Tipo IV'

# Cargar los datos de la simulación desde archivos pickle
with open(f'{instancia_archivo}/scen_points_sample.pkl', 'rb') as f:
    points = pickle.load(f)[3]
with open(f'{instancia_archivo}/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas = pickle.load(f)[3]
with open(f'{instancia_archivo}/scen_indicador_sample.pkl', 'rb') as f:
    indicadores = pickle.load(f)[3]


arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

# Inicializar los camiones
camiones = [
    Camion(id=1, tiempo_inicial=0),
    Camion(id=2, tiempo_inicial=0),
    Camion(id=3, tiempo_inicial=0)
]

simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

#registrar_tiempos_delivery(simulacion)


# Llamar a la función para crear el GIF
#crear_gif_con_movimiento_camiones(simulacion)
#generar_mapa_calor_rutas(simulacion)
