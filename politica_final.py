import numpy as np
from ruteo import *
import pickle
import matplotlib.pyplot as plt
from funciones_complementarias import *
import parametros as p


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
    
    # Para cada punto en la ruta, buscar el pedido correspondiente en pedidos disponibles (Para no repetir pedidos)
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
        #print(f"Minuto {minuto}: simulando...")

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

            pedidos_totales = simulacion.pedidos_disponibles + simulacion.pedidos_entregados + simulacion.pedidos_no_disponibles + simulacion.pedidos_tercerizados

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
    if valor_ponderado >= parametros["umbral_salida"]:
        return True
    
    return False

############# Aqui se encuentran todas las funciones relacionadas a la incorporacion del pick up #####################
# evaluar incorporacion de pick up y pick up nuevos disponibles.

def evaluar_incorporacion_pickup(camion, parametros, simulacion):
    # Límite de pickups dinámicos permitidos por ruta dependiendo de instancia

    # Verificar si ya se alcanzó el límite de pickups dinámicos
    if camion.pickups_actuales >= parametros['maximo_incorporacion_pick_up']:
        print(f"Camión {camion.id}: Límite de {parametros['maximo_incorporacion_pick_up']} pickups dinámicos alcanzado.")
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
                print(f"Camión {camion.id}: Se añadieron pickups dinámicos.")

            # Marcar que los pick-ups ya fueron evaluados para esta ruta
            camion.pickups_evaluados = True
            return
    else:
        # Si por alguna razón el índice está fuera de rango, no hacemos nada
        return

#Revisa si llegaron nuevos pick ups y en caso de que lleguen maneja el flujo de si se incorpora o no y el cambio y registro de la ruta
def pick_up_nuevos_disponible(camion, parametros, simulacion, current_index):
    # Límite de pickups dinámicos permitidos por ruta dependiendo de instancia

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
        todos_los_pedidos = simulacion.pedidos_disponibles + simulacion.pedidos_entregados
        nueva_ruta = cheapest_insertion_adaptacion(
            simulacion.minuto_actual, parametros, camion, current_index,
            nuevos_pickups, camion.rutas[-1], todos_los_pedidos, tiempo_limite=195
        )
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
            print(f"Camión {camion.id}: Se agregaron pickups.")

            # Calcular el nuevo tiempo restante
            _, tiempo_total_nueva_ruta = calculate_arrival_times_adapted(
                nueva_ruta, camion.velocidad, camion.tiempo_inicio_ruta, [10000, 10000], service_time=3
            )
            camion.tiempo_restante = max(0, tiempo_total_nueva_ruta - simulacion.minuto_actual)

        return camion.rutas[-1]  # Devolver la nueva ruta actualizada

    else:
        print(f"No hay nuevas solicitudes de pick-up disponibles en el minuto {simulacion.minuto_actual}.")
        return camion.rutas[-1]  # Devolver la ruta actual sin cambios

#Revisa si la ruta cambio o no
def listas_identicas(lista1, lista2):
    if len(lista1) != len(lista2):
        print("Las rutas tienen diferente largo")
        return False
    return all(np.array_equal(arr1, arr2) for arr1, arr2 in zip(lista1, lista2))






instancia_archivo = 'Instancia Tipo IV'

if instancia_archivo == 'Instancia Tipo I':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_1
    parametros_ventana_2 = p.parametros_ventana_2_instancia_1
    parametros_ventana_3 = p.parametros_ventana_3_instancia_1
elif instancia_archivo == 'Instancia Tipo II':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_2
    parametros_ventana_2 = p.parametros_ventana_2_instancia_2
    parametros_ventana_3 = p.parametros_ventana_3_instancia_2
elif instancia_archivo == 'Instancia Tipo III':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_3
    parametros_ventana_2 = p.parametros_ventana_2_instancia_3
    parametros_ventana_3 = p.parametros_ventana_3_instancia_3
elif instancia_archivo == 'Instancia Tipo IV':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_4
    parametros_ventana_2 = p.parametros_ventana_2_instancia_4
    parametros_ventana_3 = p.parametros_ventana_3_instancia_4


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


# Llamar a la función para crear el GIF
#crear_gif_con_movimiento_camiones(simulacion)
