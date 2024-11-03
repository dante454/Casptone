#Recalculo a la mitad de la ruta inicial para agregar pickups si esq se puede

import numpy as np
import pickle
import matplotlib.pyplot as plt
from ruteo import generar_ruta
from funciones_caso_base import *

class EstadoSimulacion:
    def __init__(self, minuto_inicial, puntos, indicadores, arribos_por_minuto):
        self.minuto_actual = minuto_inicial
        self.pedidos_no_disponibles = []
        self.pedidos_disponibles = []
        self.pedidos_entregados = []
        self.puntos = puntos
        self.indicadores = indicadores
        self.arribos_por_minuto = arribos_por_minuto
        self.punto_index = 0  # Para mantener el control sobre los puntos que vamos usando

    def avanzar_minuto(self):
        self.minuto_actual += 1
        self.revisar_pedidos_disponibles()

        # Crear nuevos pedidos según arribos_por_minuto
        if self.minuto_actual in self.arribos_por_minuto:
            cantidad_pedidos = self.arribos_por_minuto[self.minuto_actual]
            for _ in range(cantidad_pedidos):
                nuevo_pedido = Pedido(self.puntos[self.punto_index], self.indicadores[self.punto_index], self.minuto_actual)
                self.pedidos_no_disponibles.append(nuevo_pedido)
                self.punto_index += 1  # Avanzar al siguiente punto

    def revisar_pedidos_disponibles(self):
        for pedido in self.pedidos_no_disponibles[:]:
            pedido.hacer_disponible(self.minuto_actual)
            if pedido.disponible == 1 and pedido.entregado == 0:
                self.pedidos_no_disponibles.remove(pedido)
                self.pedidos_disponibles.append(pedido)

class Pedido:
    def __init__(self, coordenadas, indicador, minuto_llegada):
        self.coordenadas = coordenadas
        self.indicador = indicador  # 0: Delivery, 1: Pick-up
        self.minuto_llegada = minuto_llegada
        self.disponible = 0  # 0: No disponible, 1: Disponible (tras 15 min)
        self.entregado = 0  # 0: No entregado, 1: Entregado
        self.tiempo_entrega = None  # Tiempo de entrega (minuto_llegada - minuto_entrega)

    def hacer_disponible(self, minuto_actual):
        if minuto_actual >= self.minuto_llegada + 15:
            self.disponible = 1

    def entregar(self, minuto_entrega):
        self.entregado = 1
        self.tiempo_entrega = minuto_entrega - self.minuto_llegada
        self.disponible = 0  # Ya no está disponible porque fue entregado

class Camion:
    def __init__(self, id, tiempo_inicial):
        self.id = id
        self.tiempo_restante = tiempo_inicial
        self.velocidad = 583  # Velocidad en metros por minuto
        self.rutas = []  # Lista de rutas realizadas
        self.ruta_actual = []  # Ruta que está realizando actualmente
        self.punto_actual = [10000, 10000]  # Inicia en el depósito
        self.en_ruta = False
        self.tiempo_en_ruta = 0
        self.indice_actual = 0  # Índice del punto actual en la ruta
        self.recalculado = False  # Indica si ya ha recalculado la ruta durante el viaje actual

    def asignar_ruta(self, ruta, tiempo_ruta):
        self.ruta_actual = ruta
        self.tiempo_restante = tiempo_ruta
        self.en_ruta = True
        self.tiempo_en_ruta = 0
        self.indice_actual = 0
        self.recalculado = False  # Reseteamos el indicador de recalculación para la nueva ruta

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.tiempo_en_ruta += 1

            # Actualizar la posición en la ruta según el tiempo transcurrido
            tiempo_total_ruta = calcular_tiempo_ruta(self.ruta_actual, self.velocidad)
            progreso = self.tiempo_en_ruta / tiempo_total_ruta
            self.indice_actual = min(int(progreso * (len(self.ruta_actual) - 1)), len(self.ruta_actual) - 1)
            self.punto_actual = self.ruta_actual[self.indice_actual]

            if self.tiempo_restante == 0:
                self.en_ruta = False
                self.rutas.append(self.ruta_actual)  # Guardar la ruta completa al finalizarla
        else:
            self.en_ruta = False

    def en_punto_medio(self):
        tiempo_total_ruta = calcular_tiempo_ruta(self.ruta_actual, self.velocidad)
        return self.tiempo_en_ruta >= tiempo_total_ruta / 2 and not self.recalculado

def flujo_ruteo(camion, simulacion):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    #pedidos_disponibles = (pedido for pedido in pedidos_disponibles if pedido.indicador == 0)
    # 2. Filtrar los pedidos que ya pasaron los 180 minutos desde su llegada
    pedidos_disponibles = filtrar_pedidos_vencidos(pedidos_disponibles, simulacion.minuto_actual)

    # 3. Seleccionar los pedidos a rutear y extraer las coordenadas
    pedidos_a_rutear = [pedido.coordenadas for pedido in pedidos_disponibles]

    # 4. Generar la ruta según los pedidos disponibles
    ruta = generar_ruta(pedidos_a_rutear, [10000, 10000])  # Inicia y termina en el depósito

    # 5. Verificar si el camión alcanza a completar la ruta en el tiempo disponible
    while not verificar_llegada_a_tiempo(camion, ruta, simulacion.minuto_actual) and len(ruta) > 2:
        ruta = ajustar_ruta(ruta)

    # 6. Asignar la ruta al camión
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta)

    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

def verificar_llegada_a_tiempo(camion, ruta, minuto_actual):
    tiempo_total = calcular_tiempo_ruta(ruta, camion.velocidad)
    if minuto_actual + tiempo_total > 1020:  # Verificar que regrese antes del minuto 1020
        return False
    return True

def ajustar_ruta(ruta):
    if len(ruta) > 2:
        ruta.pop(-2)
    return ruta

def actualizar_estado_simulacion(simulacion, ruta):
    for punto in ruta:
        for pedido in simulacion.pedidos_disponibles[:]:
            if np.array_equal(pedido.coordenadas, punto):
                pedido.entregar(simulacion.minuto_actual)
                simulacion.pedidos_disponibles.remove(pedido)
                simulacion.pedidos_entregados.append(pedido)

def filtrar_pedidos_vencidos(pedidos_disponibles, minuto_actual, tiempo_limite=180):
    return [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]

def recalcular_ruta_en_mitad(camion, simulacion):
    nuevos_pickups = [pedido for pedido in simulacion.pedidos_disponibles if pedido.indicador == 1 and pedido.entregado == 0]

    if not nuevos_pickups:
        camion.recalculado = True  # Marcamos que ya intentamos recalcular
        return  # No hay nuevos pickups para agregar

    # Obtener la ruta restante desde el punto actual hasta el depósito
    ruta_restante = camion.ruta_actual[camion.indice_actual:]

    # Excluir el depósito si ya está en la ruta restante
    if ruta_restante[-1] == [10000, 10000]:
        depot = ruta_restante.pop()
    else:
        depot = [10000, 10000]

    # Crear una nueva lista de puntos a rutear: punto actual + ruta restante (sin depósito) + nuevos pickups
    puntos_a_rutear = [camion.punto_actual] + ruta_restante[1:] + [pedido.coordenadas for pedido in nuevos_pickups]

    # Generar una nueva ruta desde el punto actual
    nueva_ruta_parcial = generar_ruta(puntos_a_rutear, camion.punto_actual)

    # Agregar el depósito al final de la ruta
    nueva_ruta_parcial.append(depot)

    # Construir la nueva ruta completa
    nueva_ruta = camion.ruta_actual[:camion.indice_actual] + nueva_ruta_parcial[1:]

    # Verificar si la nueva ruta cumple con el tiempo máximo permitido
    if verificar_llegada_a_tiempo(camion, nueva_ruta, simulacion.minuto_actual - camion.tiempo_en_ruta):
        # Asignar la nueva ruta al camión
        tiempo_ruta_restante = calcular_tiempo_ruta(nueva_ruta[camion.indice_actual:], camion.velocidad)
        camion.ruta_actual = nueva_ruta
        camion.tiempo_restante = tiempo_ruta_restante
        # Actualizar los pedidos entregados de la nueva ruta
        actualizar_estado_simulacion(simulacion, nueva_ruta[camion.indice_actual:])
    else:
        pass  # No se puede asignar la nueva ruta sin exceder el tiempo

    camion.recalculado = True  # Marcamos que ya se ha recalculado la ruta

def simular_minuto_a_minuto(simulacion, camiones, x_minutos):
    for minuto in range(simulacion.minuto_actual, 1020):
        simulacion.minuto_actual = minuto
        print(f"Minuto {minuto}: simulando...")

        # Actualizar los pedidos disponibles
        simulacion.revisar_pedidos_disponibles()

        # Actualizar tiempos de los camiones
        for camion in camiones:
            camion.actualizar_tiempo()

            # Evaluar si los camiones deben salir a rutear
            if not camion.en_ruta:
                if evaluar_salida(camion, simulacion, x_minutos):
                    flujo_ruteo(camion, simulacion)

            elif camion.en_punto_medio():
                print(f"Recalculando ruta para el camión {camion.id} en el minuto {minuto}")
                recalcular_ruta_en_mitad(camion, simulacion)

        # Avanzar un minuto en la simulación
        simulacion.avanzar_minuto()

    print("Simulación finalizada.")
    
    # Mostrar el resumen final de la simulación
    for camion in camiones:
        tiempo_en_ruta = sum(calcular_tiempo_ruta(ruta, camion.velocidad) for ruta in camion.rutas)
        print(f"Camión {camion.id}:")
        print(f"Veces que realizó rutas: {len(camion.rutas)}")
        print(f"Tiempo total manejado: {tiempo_en_ruta / 60:.2f} horas")
        print(f"Rutas completas: {camion.rutas}")

    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)
    print(f"Beneficio total: {beneficio_total}")
    print(f"Distancia total recorrida: {distancia_total} M")

    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    if tiempos_respuesta:
        tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        print(f"Tiempo de respuesta promedio: {tiempo_respuesta_promedio:.2f} minutos")
    else:
        print("No se completaron pedidos para calcular el tiempo de respuesta.")

    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)
    print(f"Cantidad de pick-ups realizados: {cantidad_pickups}")
    print(f"Cantidad de deliveries realizados: {cantidad_deliveries}")

    graficar_rutas_y_puntos(camiones, simulacion)

def evaluar_salida(camion, simulacion, x_minutos):
    if camion.tiempo_restante > 0:
        return False
    if len(simulacion.pedidos_disponibles) == 0:
        return False
    if simulacion.minuto_actual % x_minutos != 0:
        return False
    return True

# Cargar datos y ejecutar la simulación
ruta_arrivals = 'Instancia Tipo I/scen_arrivals_sample.pkl'
ruta_points = 'Instancia Tipo I/scen_points_sample.pkl'
ruta_indicadores = 'Instancia Tipo I/scen_indicador_sample.pkl'

with open(ruta_points, 'rb') as f:
    all_points = pickle.load(f)
with open(ruta_arrivals, 'rb') as f:
    all_llegadas = pickle.load(f)
with open(ruta_indicadores, 'rb') as f:
    all_indicadores = pickle.load(f)

points = all_points[0]
llegadas = all_llegadas[0]
indicadores = all_indicadores[0]

arribos_por_minuto = procesar_tiempos([llegadas], 60)[0]

simulacion = EstadoSimulacion(520, points, indicadores, arribos_por_minuto)

camion1 = Camion(id=1, tiempo_inicial=0)
camion2 = Camion(id=2, tiempo_inicial=0)
camion3 = Camion(id=3, tiempo_inicial=0)

camiones = [camion1, camion2, camion3]

simular_minuto_a_minuto(simulacion, camiones, 1)