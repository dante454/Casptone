import numpy as np

import pickle
import pandas as pd
import matplotlib.pyplot as plt
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

    def calcular_beneficio_acumulado(self):
        """Calcula el beneficio acumulado desde el inicio de la simulación."""
        return sum(
            1 if pedido.indicador == 1 else 2 
            for pedido in self.pedidos_entregados
        )

    def calcular_beneficio_maximo(self):
        """Calcula el beneficio máximo posible hasta el minuto actual."""
        return sum(
            1 if pedido.indicador == 1 else 2 
            for pedido in (self.pedidos_entregados + self.pedidos_disponibles + self.pedidos_no_disponibles)
        )

    def calcular_porcentaje_beneficio(self, beneficio_acumulado):
        """Calcula el porcentaje del beneficio respecto al máximo beneficio disponible."""
        beneficio_maximo = self.calcular_beneficio_maximo()
        if beneficio_maximo == 0:
            return 0  # Evita división por cero
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

class Pedido:
    def __init__(self, coordenadas, indicador, minuto_llegada):
        self.coordenadas = coordenadas
        self.indicador = indicador  # 0: Delivery, 1: Pick-up
        self.minuto_llegada = minuto_llegada
        self.disponible = 0  # 0: No disponible, 1: Disponible (tras 15 min)
        self.entregado = 0  # 0: No entregado, 1: Entregado
        self.tiempo_entrega = None  # Tiempo de entrega (minuto_llegada - minuto_entrega)
        self.momento_entrega = None
        self.area = self.determinar_area()  # Atributo que indica el área del pedido

    def hacer_disponible(self, minuto_actual):
        if minuto_actual >= self.minuto_llegada + 15:
            self.disponible = 1
            

    def entregar(self, minuto_entrega):
        self.entregado = 1
        self.tiempo_entrega = minuto_entrega - self.minuto_llegada
        self.momento_entrega = minuto_entrega
        self.disponible = 0  # Ya no está disponible porque fue entregado

    def determinar_area(self):
        return asignar_area(self.coordenadas)

class Camion:
    def __init__(self, id, tiempo_inicial):
        self.id = id
        self.tiempo_restante = tiempo_inicial  # Minutos hasta que el camión esté disponible
        self.velocidad = ((25 * 1000) / 60) #metro/minuto
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
        


def crear_gif_con_movimiento_camiones(simulacion, archivo_gif="simulacion_movimiento_camiones.gif"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 20000)
    ax.set_ylim(0, 20000)

    # Colores para cada camión
    colores_camiones = ["cyan", "magenta", "orange"]
    velocidad_camion = ((25 * 1000) / 60)  # 35 km/h convertidos a metros por minuto

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



def graficar_rutas_y_puntos(camiones, simulacion):
    plt.figure(figsize=(10, 10))
    
    # Colores para las rutas de los camiones
    colores_camiones = ['blue', 'green', 'red']
    
    # Variable para controlar si ya se agregó la leyenda de cada camión
    etiquetas_camion = [False, False, False]
    
    # Iterar sobre los camiones y graficar cada ruta
    for idx, camion in enumerate(camiones):
        for ruta in camion.rutas:
            ruta = np.array(ruta)  # Convertir la ruta a un array de numpy
            if not etiquetas_camion[idx]:  # Solo agregar una vez la etiqueta
                plt.plot(ruta[:, 0], ruta[:, 1], color=colores_camiones[idx], label=f'Ruta Camión {camion.id}')
                etiquetas_camion[idx] = True
            else:
                plt.plot(ruta[:, 0], ruta[:, 1], color=colores_camiones[idx])

    # Graficar **todos** los puntos de la simulación diferenciados por tipo (pickup o delivery)
    pickup_legend = False
    delivery_legend = False
    
    for i, punto in enumerate(simulacion.puntos):
        if simulacion.indicadores[i] == 1:  # Pick-up
            if not pickup_legend:
                plt.scatter(punto[0], punto[1], color='orange', marker='o', label='Pick-up')
                pickup_legend = True
            else:
                plt.scatter(punto[0], punto[1], color='orange', marker='o')
        else:  # Delivery
            if not delivery_legend:
                plt.scatter(punto[0], punto[1], color='purple', marker='s', label='Delivery')
                delivery_legend = True
            else:
                plt.scatter(punto[0], punto[1], color='purple', marker='s')

    # Marcar el depósito (asumimos que está en el centro)
    plt.scatter(10000, 10000, color='black', marker='D', s=100, label='Depósito')

    # Dibujar las líneas divisorias de las áreas con un grosor más grande
    cx, cy = 10000, 10000
    plt.plot([cx, cx + 10000 * np.cos(np.radians(0))], [cy, cy + 10000 * np.sin(np.radians(0))], 'k-', linewidth=2.5)  # Línea 0° (ancho de línea 2.5)
    plt.plot([cx, cx + 10000 * np.cos(np.radians(120))], [cy, cy + 10000 * np.sin(np.radians(120))], 'k-', linewidth=2.5)  # Línea 120° (ancho de línea 2.5)
    plt.plot([cx, cx + 10000 * np.cos(np.radians(240))], [cy, cy + 10000 * np.sin(np.radians(240))], 'k-', linewidth=2.5)  # Línea 240° (ancho de línea 2.5)

    # Ajustar el gráfico
    plt.title('Rutas y Puntos de Pick-up/Delivery')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()
def procesar_tiempos(arrivals, division_minutos):

    minutos = [[segundo // division_minutos for segundo in simulacion] for simulacion in arrivals]
    df = pd.DataFrame(minutos).T  # Transponer para tener simulaciones como columnas
    arribos_por_minuto = df.apply(lambda x: x.value_counts().sort_index()).fillna(0).astype(int)
    return arribos_por_minuto

def calcular_distancia(punto1, punto2):
    return abs(punto1[0] - punto2[0]) + abs(punto1[1] - punto2[1])

# Función placeholder para calcular el tiempo de la ruta
def calcular_tiempo_ruta(ruta, velocidad_camion):
    distancia_total = calcular_distancia_ruta(ruta)
    tiempo_extra = (len(ruta) - 2) * 5 #5 minutos en entregar cada pedido
    return ((distancia_total / velocidad_camion)  + tiempo_extra)# Tiempo en minutos


def calcular_distancia_ruta(ruta):
    distancia_total = 0

    # Calcular la distancia entre cada par de puntos consecutivos en la ruta
    for i in range(1, len(ruta)):
        distancia_total += calcular_distancia(ruta[i-1], ruta[i])

    return distancia_total

def calcular_beneficio(simulacion):
    beneficio = 0
    beneficio_maximo = 0

    # Iterar sobre los pedidos entregados
    for pedido in simulacion.pedidos_entregados:
        if pedido.indicador == 0:  # Es un delivery
            beneficio += 2
        elif pedido.indicador == 1:  # Es un pick-up
            beneficio += 1

    # Calcular el beneficio máximo posible
    for pedido in simulacion.pedidos_disponibles + simulacion.pedidos_entregados:
        if pedido.indicador == 0:  # Delivery
            beneficio_maximo += 2
        elif pedido.indicador == 1:  # Pick-up
            beneficio_maximo += 1

    # Calcular el porcentaje del beneficio máximo alcanzado
    porcentaje_recuperado = (beneficio / beneficio_maximo) * 100 if beneficio_maximo > 0 else 0

    print(f"Beneficio total: {beneficio}, Beneficio máximo: {beneficio_maximo}, \nPorcentaje recuperado: {porcentaje_recuperado:.2f}%")
    return porcentaje_recuperado

def calcular_distancia_total(camiones):
    distancia_total = 0
    for camion in camiones:
        for ruta in camion.rutas:
            distancia_total += calcular_distancia_ruta(ruta)
    return distancia_total

def filtrar_por_radio_buffer(pedidos_disponibles, radio_buffer):
    # Definir la ubicación del depósito (en el centro del mapa)
    deposito = np.array([10000, 10000])
    
    pedidos_dentro_del_buffer = []
    
    for pedido in pedidos_disponibles:
        # Calcular la distancia Manhattan entre el depósito y el pedido
        distancia = np.abs(pedido.coordenadas[0] - deposito[0]) + np.abs(pedido.coordenadas[1] - deposito[1])
        
        # Si la distancia está dentro del radio del buffer, agregar el pedido a la lista
        if distancia <= radio_buffer:
            pedidos_dentro_del_buffer.append(pedido)
    
    return pedidos_dentro_del_buffer


centros_areas = {
    1: np.array([7500, 10000]),  # Centro del área 1
    2: np.array([12500, 7500]),  # Centro del área 2
    3: np.array([12500, 12500])  # Centro del área 3
}

# Definir un radio para cada área (puedes ajustar estos valores)
radios_areas = {
    1: 10000,  # Radio para el área 1
    2: 8000,  # Radio para el área 2(abajo iz)
    3: 70000   # Radio para el área 3
}

# Definir el depósito (ejemplo en el centro del mapa)
deposito = [10000, 10000]  # Ajusta las coordenadas según tu mapa

# Definir un radio máximo (e.g., 5000 metros)
radio_maximo = 5000

def filtrar_por_radio_depot(pedidos_disponibles, deposito, radio_maximo):
    pedidos_dentro_del_buffer = []

    for pedido in pedidos_disponibles:
        # Calcular la distancia euclidiana entre el pedido y el depósito
        distancia = np.sqrt((pedido.coordenadas[0] - deposito[0])**2 + 
                            (pedido.coordenadas[1] - deposito[1])**2)

        # Si la distancia está dentro del radio máximo, agregar el pedido a la lista
        if distancia <= radio_maximo:
            pedidos_dentro_del_buffer.append(pedido)

    return pedidos_dentro_del_buffer


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
    


