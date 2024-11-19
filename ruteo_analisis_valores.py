import numpy as np
import matplotlib.pyplot as plt
from funciones_caso_base import *
from ruteo import manhattan_distance, calculate_arrival_times, verificar_llegada_a_tiempo, total_distance
from ruteo import calcular_tiempo_regreso, vence_el_pedido
from politica_final import *

# Función para calcular el beneficio máximo posible
def calcular_beneficio_maximo(simulacion, valor_deliv, valor_pick):
    return sum(valor_pick if pedido.indicador == 1 else valor_deliv  
               for pedido in (simulacion.pedidos_entregados + simulacion.pedidos_disponibles + simulacion.pedidos_no_disponibles))

def calcular_beneficio2(simulacion, valor_delivery=2, valor_pickup=1):
    beneficio = 0
    for pedido in simulacion.pedidos_entregados:
        if pedido.indicador == 1:  # Pick-up
            beneficio += valor_pickup
        else:  # Delivery
            beneficio += valor_delivery
    return beneficio


def calcular_prioridad2(pedido, minuto_actual, valor_pickup, valor_delivery):
    if pedido.indicador == 0:  # Delivery
        tiempo_restante = 180 - (minuto_actual - pedido.minuto_llegada)
        return tiempo_restante * valor_delivery
    else:  # Pick-up
        return 180 * valor_pickup
    

def cheapest_insertion2(tiempo_total, unvisited, route, points, pedidos_validos, depot, camion, minuto_actual, pedidos_disponibles, parametros, valor_pickup, valor_delivery, tiempo_limite=180):
    while unvisited:
        min_increase = float('inf')
        best_position = None
        best_point = None

        for point in unvisited:
            for i in range(len(route) + 1):
                ruta_temporal = route.copy()
                ruta_temporal.insert(i, point)

                # Calcular los tiempos de llegada y el tiempo total de la ruta temporal
                arrival_times_temp, total_time_temp = calculate_arrival_times(
                    ruta_temporal, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=3
                )

                # Ignorar rutas que excedan el tiempo límite global
                if total_time_temp > 1020:
                    continue

                # Validar que todos los puntos sean válidos (no vencidos)
                all_points_valid = True
                prioridad_total = 0
                for idx_ruta, arrival_time in zip(ruta_temporal, arrival_times_temp):
                    pedido_ruta = pedidos_validos[idx_ruta]
                    expiration_time_ruta = pedido_ruta.minuto_llegada + tiempo_limite
                    if arrival_time > expiration_time_ruta:
                        all_points_valid = False
                        break

                    # Sumar la prioridad del punto basado en su tipo
                    if pedido_ruta.indicador == 0:  # Delivery
                        prioridad_total += valor_delivery
                    else:  # Pick-up
                        prioridad_total += valor_pickup

                if not all_points_valid:
                    continue

                # Ajustar el criterio para seleccionar la mejor inserción
                # Considera tanto el aumento de tiempo como la prioridad
                weighted_increase = (total_time_temp - tiempo_total) / prioridad_total

                # Si esta inserción es mejor que la anterior, actualiza
                if weighted_increase < min_increase:
                    min_increase = weighted_increase
                    best_position = i
                    best_point = point
                    best_total_time = total_time_temp
                    best_arrival_times = arrival_times_temp

        if best_point is not None:
            # Insertar el mejor punto en la mejor posición
            route.insert(best_position, best_point)
            unvisited.remove(best_point)
            tiempo_total = best_total_time
        else:
            # Si no se encontró un punto válido, termina
            break

    return [depot] + [pedidos_validos[idx].coordenadas for idx in route] + [depot]


    
def generar_ruta2(points, depot, camion, minuto_actual, pedidos_disponibles, parametros, valor_pickup, valor_delivery, tiempo_limite=180):
    # Ordenar pedidos por prioridad calculada
    pedidos_disponibles = sorted(
        pedidos_disponibles,
        key=lambda p: calcular_prioridad2(p, minuto_actual, valor_pickup, valor_delivery),
        reverse=True
    )

    pedidos_validos = [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]
    if not pedidos_validos:
        return [depot, depot]

    route = []
    min_dist = float('inf')
    first_point = None
    for i, pedido in enumerate(pedidos_validos):
        prioridad = calcular_prioridad2(pedido, minuto_actual, valor_pickup, valor_delivery)
        dist = manhattan_distance(depot, pedido.coordenadas) / prioridad  # Ponderar la distancia con la prioridad
        if dist < min_dist:
            min_dist = dist
            first_point = i


    route.append(first_point)
    unvisited = set(range(len(pedidos_validos))) - {first_point}
    arrival_times, tiempo_total = calculate_arrival_times(route, pedidos_validos, depot, camion.velocidad, minuto_actual, service_time=3)

    if tiempo_total > 1020:
        return [depot, depot]

    return cheapest_insertion2(tiempo_total, unvisited, route, points, pedidos_validos, depot, camion, minuto_actual, pedidos_disponibles, parametros, valor_pickup, valor_delivery, tiempo_limite)

    

def simular_minuto_a_minuto2(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3, valor_pickup, valor_delivery):
    for minuto in range(520, 1020):
        simulacion.minuto_actual = minuto

        if minuto <= 650:
            parametros = parametros_ventana_1
        elif 651 <= minuto <= 780:
            parametros = parametros_ventana_2
        else:
            parametros = parametros_ventana_3

        simulacion.revisar_pedidos_disponibles()

        for camion in camiones:
            camion.actualizar_tiempo()

        for camion in camiones:
            if evaluar_salida(camion, simulacion, parametros):
                flujo_ruteo2(camion, simulacion, parametros, valor_pickup, valor_delivery)  # Pasar los valores

        if minuto % 30 == 0:
            beneficio_acumulado = simulacion.calcular_beneficio_acumulado(valor_delivery, valor_pickup)
            porcentaje_beneficio = simulacion.calcular_porcentaje_beneficio(beneficio_acumulado, valor_delivery, valor_pickup)
            simulacion.beneficio_por_intervalo.append((minuto, porcentaje_beneficio))

        simulacion.avanzar_minuto()
        simulacion.registrar_estado(camiones)


    beneficio_total = calcular_beneficio2(simulacion, valor_delivery, valor_pickup)
    distancia_total = calcular_distancia_total(camiones)
    beneficio_total_disponible = calcular_beneficio_maximo(simulacion, valor_delivery, valor_pickup)
    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta) if tiempos_respuesta else 0

    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)

    print(f"Simulación finalizada. Beneficio total: {beneficio_total}/{beneficio_total_disponible}")
    print(f"Distancia total recorrida: {distancia_total} metros")
    print(f"Tiempo promedio de respuesta: {tiempo_respuesta_promedio:.2f} minutos")
    print(f"Cantidad de pickups realizados: {cantidad_pickups}")
    print(f"Cantidad de deliveries realizados: {cantidad_deliveries}")


def flujo_ruteo2(camion, simulacion, parametros, valor_pickup, valor_delivery):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    depot = [10000, 10000]  # Depósito
    points = simulacion.puntos  # Asegúrate de que los puntos estén disponibles en la simulación

    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta2(points, depot, camion, simulacion.minuto_actual, pedidos_a_rutear, parametros, valor_pickup, valor_delivery, tiempo_limite=180)

    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta, simulacion.minuto_actual)
    # 9. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta


class EstadoSimulacion2:
    def __init__(self, minuto_inicial, puntos, indicadores, arribos_por_minuto):
        self.minuto_actual = minuto_inicial
        self.pedidos_no_disponibles = []
        self.pedidos_disponibles = []
        self.pedidos_entregados = []
        self.puntos = puntos
        self.indicadores = indicadores
        self.arribos_por_minuto = arribos_por_minuto
        self.punto_index = 0 # Para mantener el control sobre los puntos que vamos usand
        self.beneficio_por_intervalo = [] 
        self.registro_minuto_a_minuto = []


    def avanzar_minuto(self):
        self.minuto_actual += 1
        self.revisar_pedidos_disponibles()

        # Crear nuevos pedidos según arribos_por_minuto
        if self.minuto_actual in self.arribos_por_minuto:
            cantidad_pedidos = self.arribos_por_minuto[self.minuto_actual]
            for _ in range(cantidad_pedidos):
                # Crear pedidos a partir de los puntos e indicadores
                nuevo_pedido = Pedido(self.puntos[self.punto_index], self.indicadores[self.punto_index], self.minuto_actual)
                self.pedidos_no_disponibles.append(nuevo_pedido)
                self.punto_index += 1  # Avanzar al siguiente punto

    def revisar_pedidos_disponibles(self):
        for pedido in self.pedidos_no_disponibles[:]:
            pedido.hacer_disponible(self.minuto_actual)
            if pedido.disponible == 1 and pedido.entregado == 0:
                self.pedidos_no_disponibles.remove(pedido)
                self.pedidos_disponibles.append(pedido)

    def calcular_beneficio_acumulado(self, valor_delivery=2, valor_pickup=1):
        return sum(
            valor_pickup if pedido.indicador == 1 else valor_delivery
            for pedido in self.pedidos_entregados
        )

    def calcular_beneficio_maximo(self, valor_delivery=2, valor_pickup=1):
        return sum(
            valor_pickup if pedido.indicador == 1 else valor_delivery
            for pedido in (
                self.pedidos_entregados
                + self.pedidos_disponibles
                + self.pedidos_no_disponibles
            )
        )

    def calcular_porcentaje_beneficio(self, beneficio_acumulado, valor_delivery=2, valor_pickup=1):
        beneficio_maximo = self.calcular_beneficio_maximo(valor_delivery, valor_pickup)
        if beneficio_maximo == 0:
            return 0  # Evitar división por cero
        return (beneficio_acumulado / beneficio_maximo) * 100
    
    def registrar_estado(self, camiones):
        # Capturar el estado actual de los pedidos y camiones
        estado = {
            "minuto": self.minuto_actual,
            "pedidos": [
                {
                    "coordenadas": pedido.coordenadas,
                    "tipo": "Delivery" if pedido.indicador == 0 else "Pick-up",
                    "estado": "Disponible" if pedido.disponible else "No Disponible",
                    "entregado": pedido.entregado,
                    "minuto_llegada": pedido.minuto_llegada
                } for pedido in self.pedidos_no_disponibles + self.pedidos_disponibles + self.pedidos_entregados
            ],
            "camiones": [
                {
                    "id": camion.id,
                    "tiempo_restante": camion.tiempo_restante,
                    "rutas_realizadas": len(camion.rutas),
                    "ruta_actual": camion.rutas[-1] if camion.rutas else [],
                    "tiempo_inicio_ruta": camion.tiempo_inicio_ruta  # Incluir tiempo de inicio de la ruta
                } for camion in camiones
            ]
        }
        # Agregar el estado actual a la lista de registros
        self.registro_minuto_a_minuto.append(estado)
