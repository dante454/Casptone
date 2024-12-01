import numpy as np
from ruteo import generar_ruta
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from funciones_complementarias import *
from matplotlib.animation import FuncAnimation

# Supongo que tienes las funciones generar_ruta y las de funciones_caso_base definidas.
# Si no es así, deberías reemplazarlas con tus propias implementaciones o con código adecuado.

# Definición de las clases y funciones necesarias
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
        self.coordenadas = np.array(coordenadas, dtype=float)
        self.indicador = indicador  # 0: Delivery, 1: Pick-up
        self.minuto_llegada = minuto_llegada
        self.disponible = 0  # 0: No disponible, 1: Disponible (tras 15 min)
        self.entregado = 0  # 0: No entregado, 1: Entregado
        self.tiempo_entrega = None  # Tiempo de entrega (minuto_entrega - minuto_llegada)
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
        self.velocidad = 583  # Metros por minuto
        self.rutas = []  # Almacena todas las rutas realizadas por el camión
        self.posicion_actual = np.array([10000, 10000], dtype=float)  # Suponemos que inicia en el depósito
        self.en_ruta = False
        self.ruta_actual = []
        self.tiempo_en_punto = 0
        self.indice_punto_actual = 0  # Índice del punto actual en la ruta

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            if self.en_ruta:
                self.actualizar_posicion()
        else:
            self.tiempo_restante = 0
            self.en_ruta = False
            self.posicion_actual = np.array([10000, 10000], dtype=float)  # Regresa al depósito

    def asignar_ruta(self, ruta, tiempo_ruta):
        self.rutas.append(ruta)  # Agregar la ruta realizada a la lista de rutas
        self.tiempo_restante = tiempo_ruta
        self.en_ruta = True
        self.ruta_actual = ruta
        self.tiempo_en_punto = 0
        self.indice_punto_actual = 0  # Iniciar en el primer punto de la ruta
        self.posicion_actual = np.array(ruta[0], dtype=float)  # Inicia en el depósito
        print(f"Camión {self.id} asignado a una nueva ruta, tiempo de ruta: {tiempo_ruta} minutos")

    def actualizar_posicion(self):
        if self.indice_punto_actual < len(self.ruta_actual) - 1:
            punto_actual = np.array(self.ruta_actual[self.indice_punto_actual], dtype=float)
            punto_siguiente = np.array(self.ruta_actual[self.indice_punto_actual + 1], dtype=float)
            distancia = np.linalg.norm(punto_siguiente - punto_actual)
            tiempo_para_punto = distancia / self.velocidad

            if self.tiempo_en_punto >= tiempo_para_punto:
                # Avanzamos al siguiente punto
                self.posicion_actual = punto_siguiente
                self.indice_punto_actual += 1
                self.tiempo_en_punto = 0
            else:
                # Movemos el camión hacia el siguiente punto
                direccion = (punto_siguiente - punto_actual) / distancia
                distancia_avanzada = self.velocidad  # Avanzamos la distancia correspondiente a un minuto
                self.posicion_actual += direccion * self.velocidad * 1  # Multiplicamos por 1 minuto
                self.tiempo_en_punto += 1
        else:
            # Ruta terminada
            self.en_ruta = False
            self.posicion_actual = np.array([10000, 10000], dtype=float)  # Regresa al depósito

def asignar_area(punto):
    x, y = punto
    vector = np.array([x - 10000, y - 10000])
    angulo = np.degrees(np.arctan2(vector[1], vector[0]))
    if angulo < 0:
        angulo += 360
    if 0 <= angulo < 120:
        return 1
    elif 120 <= angulo < 240:
        return 2
    else:
        return 3

def filtrar_pedidos_vencidos(pedidos_disponibles, minuto_actual, tiempo_limite=140):
    # Filtrar los pedidos que aún pueden ser tomados (dentro de los 180 minutos desde que llegaron)
    pedidos_validos = [pedido for pedido in pedidos_disponibles if minuto_actual - pedido.minuto_llegada <= tiempo_limite]
    return pedidos_validos

def separar_y_seleccionar_area(pedidos_disponibles):
    # Separar los pedidos según su área
    pedidos_area1 = [pedido for pedido in pedidos_disponibles if pedido.area == 1]
    pedidos_area2 = [pedido for pedido in pedidos_disponibles if pedido.area == 2]
    pedidos_area3 = [pedido for pedido in pedidos_disponibles if pedido.area == 3]

    # Calcular cuál área tiene más pedidos
    areas = {1: pedidos_area1, 2: pedidos_area2, 3: pedidos_area3}
    max_area = max(areas, key=lambda k: len(areas[k]))

    return [pedido.coordenadas for pedido in areas[max_area]]

def flujo_ruteo(camion, simulacion):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 2. Filtrar los pedidos que ya pasaron los 180 minutos desde su llegada
    pedidos_disponibles = filtrar_pedidos_vencidos(pedidos_disponibles, simulacion.minuto_actual)

    if not pedidos_disponibles:
        return

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    if not pedidos_a_rutear:
        return

    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta(pedidos_a_rutear, [10000, 10000])

    # 5. Verificar si el camión alcanza a completar la ruta en el tiempo disponible
    while not verificar_llegada_a_tiempo(camion, ruta, simulacion.minuto_actual) and len(ruta) > 1:
        ruta = ajustar_ruta(ruta)  # Llamar a la función que elimina el mejor punto de la ruta

    if len(ruta) <= 1:
        return

    # 6. Aplicar la nueva política para eliminar puntos si reducen al menos x% la distancia
    ruta = eliminar_puntos_si_reducen_distancia(ruta, simulacion)

    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta)

def ajustar_ruta(ruta):
    if len(ruta) > 2:
        ruta.pop(-2)
    return ruta

def verificar_llegada_a_tiempo(camion, ruta, minuto_actual):
    tiempo_total = calcular_tiempo_ruta(ruta, camion.velocidad)
    if minuto_actual + tiempo_total > 1020:  # Verifica si se pasa de las 5 PM (1020 minutos)
        return False
    return True

def eliminar_puntos_si_reducen_distancia(ruta, simulacion, x_porcentaje=40, y_max_puntos=15):
    puntos_eliminados = 0
    distancia_original = calcular_distancia_ruta(ruta)

    while puntos_eliminados < y_max_puntos and len(ruta) > 2:  # No podemos eliminar el depósito
        mejor_reduccion = 0
        mejor_punto_a_eliminar = None

        for i in range(1, len(ruta) - 1):  # No podemos eliminar el depósito (punto 0 o el último)
            ruta_temporal = ruta[:i] + ruta[i+1:]
            distancia_reducida = calcular_distancia_ruta(ruta_temporal)

            reduccion = distancia_original - distancia_reducida
            porcentaje_reduccion = (reduccion / distancia_original) * 100

            if porcentaje_reduccion >= x_porcentaje and reduccion > mejor_reduccion:
                mejor_reduccion = reduccion
                mejor_punto_a_eliminar = i

        if mejor_punto_a_eliminar is not None:
            ruta.pop(mejor_punto_a_eliminar)
            puntos_eliminados += 1
            distancia_original = calcular_distancia_ruta(ruta)  # Actualizar la distancia original
            print(f"Se eliminó un punto para reducir la distancia en al menos {x_porcentaje}%.")
        else:
            break  # No se puede eliminar más puntos que cumplan con el criterio

    return ruta

def actualizar_estado_simulacion(simulacion, ruta):
    # Para cada punto en la ruta, buscar el pedido correspondiente en pedidos disponibles
    for punto in ruta:
        for pedido in simulacion.pedidos_disponibles:
            if np.allclose(pedido.coordenadas, punto):
                # Cambiar el estado del pedido a entregado
                pedido.entregar(simulacion.minuto_actual)
                # Mover el pedido a la lista de pedidos entregados
                simulacion.pedidos_disponibles.remove(pedido)
                simulacion.pedidos_entregados.append(pedido)
                break  # Salir del loop una vez encontrado

def simular_minuto_a_minuto(simulacion, camiones, x_minutos):
    # Lista para almacenar el estado en cada minuto
    estados_minuto_a_minuto = []

    # Inicia la simulación desde las 8:40 AM (minuto 520) hasta las 5:00 PM (1020 minutos)
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

        # Almacenar el estado actual para la animación
        estado_actual = {
            'minuto': minuto,
            'camiones': [{
                'id': camion.id,
                'posicion_actual': camion.posicion_actual.copy(),
                'en_ruta': camion.en_ruta,
                'ruta_actual': [np.array(punto) for punto in camion.ruta_actual]
            } for camion in camiones],
            'pedidos_no_disponibles': [pedido.coordenadas.copy() for pedido in simulacion.pedidos_no_disponibles],
            'pedidos_disponibles': [pedido.coordenadas.copy() for pedido in simulacion.pedidos_disponibles],
            'pedidos_entregados': [pedido.coordenadas.copy() for pedido in simulacion.pedidos_entregados],
        }
        estados_minuto_a_minuto.append(estado_actual)

        # Avanza el minuto en la simulación
        simulacion.avanzar_minuto()

    print(len(simulacion.pedidos_entregados))
    print("Simulación finalizada.")

    # Retornar los estados para la animación
    return estados_minuto_a_minuto

def evaluar_salida(camion, simulacion, x_minutos):
    # Si el camión tiene tiempo restante, no puede salir
    if camion.tiempo_restante > 0:
        return False

    if len(simulacion.pedidos_disponibles) == 0:
        return False

    # Criterio: El camión debe salir cada x_minutos
    if simulacion.minuto_actual % x_minutos != 0:
        return False

    return True  # Si se cumplen los criterios, el camión puede salir

# Funciones auxiliares
def procesar_tiempos(all_llegadas, division_minutos):
    arribos_por_minuto_list = []
    for llegadas in all_llegadas:
        arribos_por_minuto = {}
        for tiempo in llegadas:
            minuto = tiempo // division_minutos
            if minuto in arribos_por_minuto:
                arribos_por_minuto[minuto] += 1
            else:
                arribos_por_minuto[minuto] = 1
        arribos_por_minuto_list.append(arribos_por_minuto)
    return arribos_por_minuto_list

def calcular_tiempo_ruta(ruta, velocidad):
    distancia_total = calcular_distancia_ruta(ruta)
    tiempo_total = distancia_total / velocidad
    return int(np.ceil(tiempo_total))

def calcular_distancia_ruta(ruta):
    distancia = 0
    for i in range(len(ruta) - 1):
        distancia += np.linalg.norm(np.array(ruta[i+1]) - np.array(ruta[i]))
    return distancia

# Supongamos que cada entrega tiene un beneficio fijo de 10 unidades monetarias
def calcular_beneficio(simulacion):
    beneficio_por_entrega = 10
    return len(simulacion.pedidos_entregados) * beneficio_por_entrega

def calcular_distancia_total(camiones):
    distancia_total = 0
    for camion in camiones:
        for ruta in camion.rutas:
            distancia_total += calcular_distancia_ruta(ruta)
    return distancia_total

def crear_animacion(estados_minuto_a_minuto):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Configuramos los límites del gráfico según tus datos
    ax.set_xlim(9500, 10500)
    ax.set_ylim(9500, 10500)

    scat_pedidos_no_disponibles = ax.scatter([], [], c='gray', label='Pedidos No Disponibles')
    scat_pedidos_disponibles = ax.scatter([], [], c='blue', label='Pedidos Disponibles')
    scat_pedidos_entregados = ax.scatter([], [], c='green', label='Pedidos Entregados')
    scat_camiones = ax.scatter([], [], c='red', marker='s', label='Camiones')

    ax.legend(loc='upper right')

    def init():
        scat_pedidos_no_disponibles.set_offsets([])
        scat_pedidos_disponibles.set_offsets([])
        scat_pedidos_entregados.set_offsets([])
        scat_camiones.set_offsets([])
        return scat_pedidos_no_disponibles, scat_pedidos_disponibles, scat_pedidos_entregados, scat_camiones

    def update(frame):
        estado = estados_minuto_a_minuto[frame]
        minuto = estado['minuto']
        ax.set_title(f"Minuto: {minuto}")

        # Limpiar rutas anteriores
        for artist in ax.lines + ax.collections[4:]:  # Mantener los scatter plots iniciales
            artist.remove()

        # Actualizar pedidos
        pedidos_no_disponibles = np.array(estado['pedidos_no_disponibles'])
        pedidos_disponibles = np.array(estado['pedidos_disponibles'])
        pedidos_entregados = np.array(estado['pedidos_entregados'])

        scat_pedidos_no_disponibles.set_offsets(pedidos_no_disponibles)
        scat_pedidos_disponibles.set_offsets(pedidos_disponibles)
        scat_pedidos_entregados.set_offsets(pedidos_entregados)

        # Actualizar posiciones de los camiones y dibujar rutas
        posiciones_camiones = []
        for camion_estado in estado['camiones']:
            posiciones_camiones.append(camion_estado['posicion_actual'])
            if camion_estado['en_ruta']:
                ruta = camion_estado['ruta_actual']
                ruta_x = [p[0] for p in ruta]
                ruta_y = [p[1] for p in ruta]
                ax.plot(ruta_x, ruta_y, c='orange', linewidth=1, linestyle='--')

        scat_camiones.set_offsets(posiciones_camiones)

        return scat_pedidos_no_disponibles, scat_pedidos_disponibles, scat_pedidos_entregados, scat_camiones

    anim = FuncAnimation(fig, update, frames=len(estados_minuto_a_minuto), init_func=init, interval=100)
    plt.show()

# Cargar los datos
ruta_arrivals = 'Instancia Tipo III/scen_arrivals_sample.pkl'
ruta_points = 'Instancia Tipo III/scen_points_sample.pkl'
ruta_indicadores = 'Instancia Tipo III/scen_indicador_sample.pkl'

simulacion_a_usar = 0  # Cambia este valor para seleccionar otra simulación (0-99)
division_minutos = 1  # Asumiendo que los tiempos están en minutos
minuto_inicio = 520  # Ajustamos el minuto de inicio del horizonte de tiempo

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

# Inicializar la simulación
simulacion = EstadoSimulacion(minuto_inicio, points, indicadores, arribos_por_minuto)

# Inicializar los camiones
camion1 = Camion(id=1, tiempo_inicial=0)
camion2 = Camion(id=2, tiempo_inicial=0)
camion3 = Camion(id=3, tiempo_inicial=0)

# Lista de camiones
camiones = [camion1, camion2, camion3]

# Ejecutar la simulación con los camiones
x_minutos = 60  # Por ejemplo, los camiones pueden salir cada 60 minutos
estados_minuto_a_minuto = simular_minuto_a_minuto(simulacion, camiones, x_minutos)

# Crear la animación
crear_animacion(estados_minuto_a_minuto)