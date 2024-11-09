import numpy as np
from ruteo import generar_ruta
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from funciones_caso_base import *
import matplotlib.animation as animation


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
        self.tiempo_inicio_ruta = None

    def actualizar_tiempo(self):
        if self.tiempo_restante > 1:
            self.tiempo_restante -= 1
        else:
            self.tiempo_restante = 0


    def asignar_ruta(self, ruta, tiempo_ruta, tiempo_inicio):
        self.rutas.append(ruta)  # Agregar la ruta realizada a la lista de rutas
        self.tiempo_restante = tiempo_ruta
        self.tiempo_inicio_ruta = tiempo_inicio  # Registrar el tiempo de inicio de la ruta
        print(f"Camión {self.id} asignado a una nueva ruta, tiempo de ruta: {tiempo_ruta} minutos")

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

    depot=[10000, 10000]
    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta(points, depot, camion, simulacion.minuto_actual, pedidos_a_rutear, tiempo_limite=180)

    # 5. Verificar si el camión alcanza a completar la ruta en el tiempo disponible
    # while not verificar_llegada_a_tiempo(camion, ruta, simulacion.minuto_actual) and len(ruta) > 1:
    #     ruta = ajustar_ruta(ruta)  # Llamar a la función que elimina el mejor punto de la ruta
    
    actualizar_estado_simulacion(simulacion, ruta)

    # 6. Aplicar la nueva política para eliminar puntos si reducen al menos x% la distancia
    ruta = eliminar_puntos_si_reducen_distancia(ruta, simulacion)

    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta, simulacion.minuto_actual)

    # 9. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta


def ajustar_ruta(ruta):
    ruta.pop(-2)
    return ruta


def asignar_area(punto):
    x, y = punto
    cx, cy = 10000, 10000  # Centro del mapa
    vector = np.array([x - cx, y - cy])
    angle = np.degrees(np.arctan2(vector[1], vector[0]))

    if angle < 0:
        angle += 360

    if 0 <= angle < 120:
        return 1  # Área 1
    elif 120 <= angle < 240:
        return 2  # Área 2
    else:
        return 3  # Área 3
    

# Función para verificar si se alcanza a completar la ruta en el tiempo disponible
def verificar_llegada_a_tiempo(camion, ruta, minuto_actual):
    tiempo_total = calcular_tiempo_ruta(ruta, camion.velocidad)
    if minuto_actual + tiempo_total > 1020:  # Verifica si se pasa de las 7 PM (1110 minutos)
        return False
    return True




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
        simulacion.registrar_estado(camiones)

    
    print(len(simulacion.pedidos_entregados))
    print("Simulación finalizada.")
    

    for camion in camiones:
        tiempo_en_ruta = 0

        for ruta in camion.rutas:
            tiempo_en_ruta += calcular_tiempo_ruta(ruta, camion.velocidad)

        print(f"Camión {camion.id}:")
        print(f"Veces que realizó rutas: {len(camion.rutas)}")
        print(f"Tiempo total manejado: {tiempo_en_ruta / 60:.2f} horas")

    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)

    print(f"Beneficio total: {beneficio_total}")
    print(f"Distancia total recorrida: {distancia_total} M")

    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
    print(f"Tiempo de respuesta promedio: {tiempo_respuesta_promedio:.2f} minutos")


    # Contar la cantidad de pick-ups y deliveries realizados
    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)

    # Imprimir el conteo de pick-ups y deliveries
    print(f"Cantidad de pick-ups realizados: {cantidad_pickups}")
    print(f"Cantidad de deliveries realizados: {cantidad_deliveries}")

    graficar_rutas_y_puntos(camiones, simulacion)


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


#nueva politica
def eliminar_puntos_si_reducen_distancia(ruta, simulacion, x_porcentaje=40, y_max_puntos=15):
    puntos_eliminados = 0
    distancia_original = calcular_distancia_ruta(ruta)

    while puntos_eliminados < y_max_puntos and len(ruta) > 2 and simulacion.minuto_actual < 900:  # No podemos eliminar el depósito
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
x_minutos = 60  # Por ejemplo, los camiones pueden salir cada 30 minutos
simular_minuto_a_minuto(simulacion, camiones, x_minutos)



def crear_gif_con_movimiento_camiones(simulacion, archivo_gif="simulacion_movimiento_camiones.gif"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 20000)
    ax.set_ylim(0, 20000)

    # Colores para cada camión
    colores_camiones = ["cyan", "magenta", "orange"]
    velocidad_camion = 35 * 1000 / 60  # 35 km/h convertidos a metros por minuto

    # Función para calcular la posición actual del camión
    def calcular_posicion_actual(ruta, tiempo_transcurrido, velocidad):
        distancia_recorrida = tiempo_transcurrido * velocidad
        distancia_acumulada = 0

        for i in range(1, len(ruta)):
            distancia_segmento = calcular_distancia(ruta[i-1], ruta[i])
            if distancia_acumulada + distancia_segmento >= distancia_recorrida:
                # Interpolar entre los puntos
                fraccion = (distancia_recorrida - distancia_acumulada) / distancia_segmento
                x = ruta[i-1][0] + fraccion * (ruta[i][0] - ruta[i-1][0])
                y = ruta[i-1][1] + fraccion * (ruta[i][1] - ruta[i-1][1])
                return (x, y)
            distancia_acumulada += distancia_segmento

        # Si ha recorrido toda la ruta, devolver el último punto
        return ruta[-1]

    # Función para actualizar cada cuadro de la animación
    def actualizar(frame):
        ax.clear()
        ax.set_xlim(0, 20000)
        ax.set_ylim(0, 20000)
        ax.set_title(f"Minuto {simulacion.registro_minuto_a_minuto[frame]['minuto']}")
        ax.scatter(10000, 10000, c="black", s=50, label="Depósito")  # Depósito en negro

        estado = simulacion.registro_minuto_a_minuto[frame]

        # Graficar pedidos
        for pedido in estado["pedidos"]:
            x, y = pedido["coordenadas"]
            if pedido["entregado"]:
                ax.plot(x, y, 'go')  # Pedido entregado en verde
            elif pedido["estado"] == "Disponible":
                if estado["minuto"] - pedido["minuto_llegada"] > 180:  # Pedidos vencidos
                    ax.plot(x, y, 'mo')  # Pedido vencido en magenta
                else:
                    ax.plot(x, y, 'bo')  # Pedido disponible en azul
            else:
                ax.plot(x, y, 'ro')  # Pedido no disponible en rojo

        # Graficar camiones y sus rutas
        for i, camion in enumerate(estado["camiones"]):
            if camion["rutas_realizadas"] > 0:
                ruta = camion["ruta_actual"]
                tiempo_transcurrido = estado["minuto"] - camion["tiempo_inicio_ruta"]
                posicion_actual = calcular_posicion_actual(ruta, tiempo_transcurrido, velocidad_camion)

                # Graficar la ruta completa del camión en su color asignado
                ruta_x = [punto[0] for punto in ruta]
                ruta_y = [punto[1] for punto in ruta]
                ax.plot(ruta_x, ruta_y, '--', color=colores_camiones[i], alpha=0.3)  # Ruta en línea discontinua con transparencia

                # Graficar la posición actual del camión en su color asignado
                ax.scatter(posicion_actual[0], posicion_actual[1], c=colores_camiones[i], s=70, label=f"Camión {camion['id']}")

        ax.legend()

    # Crear la animación
    anim = animation.FuncAnimation(fig, actualizar, frames=len(simulacion.registro_minuto_a_minuto), interval=100)
    
    # Guardar el GIF
    anim.save(archivo_gif, writer="pillow")
    print(f"GIF creado: {archivo_gif}")

# Llamar a la función para crear el GIF
crear_gif_con_movimiento_camiones(simulacion)