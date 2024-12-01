import numpy as np
from ruteo import generar_ruta
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from funciones_complementarias import procesar_tiempos, calcular_distancia, calcular_tiempo_ruta, calcular_distancia_ruta, calcular_distancia_total, calcular_beneficio

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

class Pedido:
    def __init__(self, coordenadas, indicador, minuto_llegada):
        self.coordenadas = coordenadas
        self.indicador = indicador  # 0: Delivery, 1: Pick-up
        self.minuto_llegada = minuto_llegada
        self.disponible = 0  # 0: No disponible, 1: Disponible (tras 15 min)
        self.entregado = 0  # 0: No entregado, 1: Entregado
        self.tiempo_entrega = None  # Tiempo de entrega (minuto_llegada - minuto_entrega)
        self.area = self.determinar_area()  # Atributo que indica el área del pedido

    def hacer_disponible(self, minuto_actual):
        if minuto_actual >= self.minuto_llegada + 15:
            self.disponible = 1
            

    def entregar(self, minuto_entrega):
        self.entregado = 1
        self.tiempo_entrega = minuto_entrega - self.minuto_llegada
        self.disponible = 0  # Ya no está disponible porque fue entregado

    def determinar_area(self):
        return asignar_area(self.coordenadas)

class Camion:
    def __init__(self, id, tiempo_inicial):
        self.id = id
        self.tiempo_restante = tiempo_inicial  # Minutos hasta que el camión esté disponible
        self.velocidad = 583
        self.rutas = []  # Almacena todas las rutas realizadas por el camión
    
    def actualizar_tiempo(self):
        if self.tiempo_restante > 1:
            self.tiempo_restante -= 1
        else:
            self.tiempo_restante = 0

    def asignar_ruta(self, ruta, tiempo_ruta):
        self.rutas.append(ruta)  # Agregar la ruta realizada a la lista de rutas
        self.tiempo_restante = tiempo_ruta
        print(f"Camión {self.id} asignado a una nueva ruta, tiempo de ruta: {tiempo_ruta} minutos")

def filtrar_pedidos_vencidos(pedidos_disponibles, minuto_actual, tiempo_limite=140):
    # Filtrar los pedidos que aún pueden ser tomados (dentro de los 180 minutos desde que llegaron)
    pedidos_validos = [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]
    return pedidos_validos


def separar_y_seleccionar_area(pedidos_disponibles):
    # Separar los pedidos según su área
    pedidos_area1 = [pedido.coordenadas for pedido in pedidos_disponibles if pedido.area == 1]
    pedidos_area2 = [pedido.coordenadas for pedido in pedidos_disponibles if pedido.area == 2]
    pedidos_area3 = [pedido.coordenadas for pedido in pedidos_disponibles if pedido.area == 3]

    # Calcular cuál área tiene más pedidos
    max_area = max(len(pedidos_area1), len(pedidos_area2), len(pedidos_area3))

    if max_area == len(pedidos_area1):
        return pedidos_area1
    elif max_area == len(pedidos_area2):
        return pedidos_area2
    else:
        return pedidos_area3


def flujo_ruteo(camion, simulacion):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 2. Filtrar los pedidos que ya pasaron los 180 minutos desde su llegada
    pedidos_disponibles = filtrar_pedidos_vencidos(pedidos_disponibles, simulacion.minuto_actual)

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta(pedidos_a_rutear, [10000, 10000])

    
    # 5. Verificar si el camión alcanza a completar la ruta en el tiempo disponible para deliveries
    tiempo_maximo = 1020  # Tiempo máximo en minutos (17:00 PM)
    while True:
        puede_entregar, punto_no_entregado = verificar_tiempo_ruta(camion, ruta, simulacion.minuto_actual, tiempo_maximo, camion.velocidad)
        
        if puede_entregar:
            break  # Si puede entregar todos los puntos, salimos del loop
        else:
            # Eliminar el punto que no se puede entregar a tiempo utilizando np.array_equal
            ruta = [p for p in ruta if not np.array_equal(p, punto_no_entregado)]
            print(f"Se eliminó el punto {punto_no_entregado} porque no se puede entregar a tiempo.")
    
    # 6. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 7. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta)

    # 8. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta


def ajustar_ruta(ruta):
    ruta.pop(-2)
    return ruta


def asignar_area(punto):
    x, y = punto
    
    vector = np.array([x - 10000, y - 10000])
    
    # Definir vectores de referencia para dividir las áreas
    v1 = np.array([1, 0])   # Eje X
    v2 = np.array([-0.5, np.sqrt(3)/2])  # Ángulo 120° desde el eje X
    v3 = np.array([-0.5, -np.sqrt(3)/2]) # Ángulo 240° desde el eje X
    
    if np.dot(vector, v1) >= 0 and np.dot(vector, v2) >= 0:
        return 1  # Área 1
    elif np.dot(vector, v2) < 0 and np.dot(vector, v3) >= 0:
        return 2  # Área 2
    else:
        return 3  # Área 3
    
    
def verificar_tiempo_ruta(camion, ruta, minuto_actual, tiempo_maximo, velocidad):
    for i, punto in enumerate(ruta[:-1]):  # Iteramos sobre todos los puntos menos el último (el depósito)
        tiempo_necesario = calcular_tiempo_ruta(ruta[:i+1], velocidad)
        if minuto_actual + tiempo_necesario > tiempo_maximo:
            return False, punto  # Devolvemos el punto que no se puede entregar a tiempo
    return True, None  # Si se pueden entregar todos los puntos, devolvemos True



# Función para actualizar el estado de la simulación, marcando los puntos de la ruta como visitados
def actualizar_estado_simulacion(simulacion, ruta):
    # Para cada punto en la ruta, buscar el pedido correspondiente en pedidos disponibles
    for punto in ruta:
        for pedido in simulacion.pedidos_disponibles:
            if np.array_equal(pedido.coordenadas, punto):
                # Cambiar el estado del pedido a entregado
                pedido.entregar(simulacion.minuto_actual)
                # Mover el pedido a la lista de pedidos entregados
                simulacion.pedidos_disponibles.remove(pedido)
                simulacion.pedidos_entregados.append(pedido)
                


def simular_minuto_a_minuto(simulacion, camiones, x_minutos):
    # Inicia la simulación desde las 8:30 AM (minuto 630) hasta las 7:00 PM (1110 minutos)
    for minuto in range(520, 1020):
        simulacion.minuto_actual = minuto
        print(f"Minuto {minuto}: simulando...")

        # Actualizar los pedidos disponibles minuto a minuto
        simulacion.revisar_pedidos_disponibles()


        # Actualizar tiempos de los camiones
        for camion in camiones:
            camion.actualizar_tiempo()
            
        # Evaluar si los camiones deben salir a rutear
        for camion in camiones:
            if evaluar_salida(camion, simulacion, x_minutos):
                # Gestionar el camión cuando sale a realizar una ruta
                flujo_ruteo(camion, simulacion)

        # Avanza el minuto en la simulación
        simulacion.avanzar_minuto()
    
    print(len(simulacion.pedidos_entregados))
    print("Simulación finalizada.")
    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)

    for camion in camiones:
        tiempo_en_ruta = 0

        for ruta in camion.rutas:
            tiempo_en_ruta += calcular_tiempo_ruta(ruta, camion.velocidad)

        print(f"Camión {camion.id}:")
        print(f"Veces que realizó rutas: {len(camion.rutas)}")
        print(f"Tiempo total manejado: {tiempo_en_ruta / 60:.2f} horas")

    print(f"Beneficio total: {beneficio_total}")
    print(f"Distancia total recorrida: {distancia_total} M")

# Función que evalúa los criterios de salida de los camiones
def evaluar_salida(camion, simulacion, x_minutos):
    # Si el camión tiene tiempo restante, no puede salir
    if camion.tiempo_restante > 0:
        return False
    
    if len(simulacion.pedidos_disponibles) == 0:
        return False
    #Que no salga a siertas horas


    #Que salga si es que hay mas de x pedidos

    # Criterio: El camión debe salir cada x_minutos
    if simulacion.minuto_actual % x_minutos != 0:
        return False

    # Criterios adicionales se pueden agregar aquí
    # Por ejemplo, si hay un número suficiente de pedidos acumulados, etc.

    return True  # Si se cumplen los criterios, el camión puede salir


# Función para gestionar la salida de los camiones
def gestionar_salida_camion(camion, simulacion):
    # Imprimir información del camión y el minuto actual
    print(f"Gestionando la salida del camión {camion.id} en el minuto {simulacion.minuto_actual}")

    # Llamar al flujo de ruteo para asignar una ruta al camión
    ruta, tiempo_ruta = flujo_ruteo(camion, simulacion)

    # Asignar la ruta generada al camión
    camion.asignar_ruta(ruta, tiempo_ruta)






ruta_arrivals = 'Instancia Tipo IV/scen_arrivals_sample.pkl'
ruta_points = 'Instancia Tipo IV/scen_points_sample.pkl'
ruta_indicadores = 'Instancia Tipo IV/scen_indicador_sample.pkl'


simulacion_a_usar = 0  # Cambia este valor para seleccionar otra simulación (0-99)
division_minutos = 60  # Ajusta según el valor que prefieras para la división de segundos a minutos
minuto_inicio = 526  # Ajustamos el minuto de inicio del horizonte de tiempo

with open(ruta_points, 'rb') as f:
    all_points = pickle.load(f)
with open(ruta_arrivals, 'rb') as f:
    all_llegadas = pickle.load(f)
with open(ruta_indicadores, 'rb') as f:
    all_indicadores = pickle.load(f)

points = all_points[simulacion_a_usar]
llegadas = all_llegadas[simulacion_a_usar]
indicadores = all_indicadores[simulacion_a_usar]

arribos_por_minuto = procesar_tiempos([llegadas], division_minutos)[0]


puntos_visitados = [0] * len(points)

# Inicializar la simulación
simulacion = EstadoSimulacion(520, points, indicadores, arribos_por_minuto)

# Inicializar un camión de ejemplo
camion1 = Camion(id=1, tiempo_inicial=0)
camion2 = Camion(id=2, tiempo_inicial=0)
camion3 = Camion(id=3, tiempo_inicial=0)

# Lista de camiones
camiones = [camion1, camion2, camion3]

# Ejecutar la simulación con los camiones
x_minutos = 1  # Por ejemplo, los camiones pueden salir cada 30 minutos
simular_minuto_a_minuto(simulacion, camiones, x_minutos)

