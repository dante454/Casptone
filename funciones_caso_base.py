import numpy as np

import pickle
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Clase que registra toda la simulacion y las cosas que rigen sobre ella
class EstadoSimulacion:
    def __init__(self, minuto_inicial, puntos, indicadores, arribos_por_minuto):
        self.minuto_actual = minuto_inicial
        self.pedidos_no_disponibles = []
        self.pedidos_disponibles = []
        self.pedidos_entregados = []
        self.pedidos_tercerizados = []
        self.puntos = puntos
        self.indicadores = indicadores
        self.arribos_por_minuto = arribos_por_minuto
        self.punto_index = 0 # Para mantener el control sobre los puntos que vamos usand
        self.beneficio_por_intervalo = [] 
        self.registro_minuto_a_minuto = []
        self.pickups_intervalos = []
        self.deliveries_intervalos = []


    def avanzar_minuto(self, parametros):
        self.minuto_actual += 1
        self.revisar_pedidos_disponibles()

        # Crear nuevos pedidos según arribos_por_minuto
        if self.minuto_actual in self.arribos_por_minuto:
            cantidad_pedidos = self.arribos_por_minuto[self.minuto_actual]
            for _ in range(cantidad_pedidos):
                # Crear pedidos a partir de los puntos e indicadores
                nuevo_pedido = Pedido(self.puntos[self.punto_index], self.indicadores[self.punto_index], self.minuto_actual, parametros)
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

    def tercerizar_pedido(self, depot, velocidad_camion):
        for pedido in self.pedidos_disponibles[:]:
            tiempo_tercerizacion = calcular_tiempo_ruta([depot, pedido.coordenadas], velocidad_camion) + 5
            tiempo_vida_restante =  195 - (self.minuto_actual - pedido.minuto_llegada) - tiempo_tercerizacion
            
            if tiempo_vida_restante <= 0:
                self.pedidos_disponibles.remove(pedido)
                self.pedidos_tercerizados.append(pedido)



#Clase que modela los pedidos y toda la informacion que contienen
class Pedido:
    def __init__(self, coordenadas, indicador, minuto_llegada, parametros):
        self.coordenadas = coordenadas
        self.indicador = indicador  # 0: Delivery, 1: Pick-up
        self.minuto_llegada = minuto_llegada
        self.disponible = 0  # 0: No disponible, 1: Disponible (tras 15 min)
        self.entregado = 0  # 0: No entregado, 1: Entregado
        self.tiempo_entrega = None  # Tiempo de entrega (minuto_llegada - minuto_entrega)
        self.momento_entrega = None
        self.area = self.determinar_area(parametros)  # Atributo que indica el área del pedido

    def hacer_disponible(self, minuto_actual):
        if minuto_actual >= self.minuto_llegada + 15:
            self.disponible = 1
            

    def entregar(self, minuto_entrega):
        self.entregado = 1
        self.tiempo_entrega = minuto_entrega - self.minuto_llegada
        self.momento_entrega = minuto_entrega
        self.disponible = 0  # Ya no está disponible porque fue entregado

    def determinar_area(self, parametros):
        return asignar_area(self.coordenadas, parametros)

#Clase que modela los camiones y toda la informacion que contienen
class Camion:
    def __init__(self, id, tiempo_inicial):
        self.id = id
        self.tiempo_restante = tiempo_inicial  # Minutos hasta que el camión esté disponible
        self.velocidad = ((25 * 1000) / 60) #metro/minuto
        self.rutas = []  # Almacena todas las rutas realizadas por el camión
        self.tiempo_inicio_ruta = None
        self.posicion_actual = None
        self.pickups_evaluados = False
        self.pickups_actuales = 0
        

    def actualizar_tiempo(self):
        if self.tiempo_restante > 1:
            self.tiempo_restante -= 1
        else:
            self.tiempo_restante = 0

    def asignar_ruta(self, ruta, tiempo_ruta, tiempo_inicio):
        self.rutas.append(ruta)  # Agregar la ruta realizada a la lista de rutas
        self.tiempo_restante = tiempo_ruta
        self.tiempo_inicio_ruta = tiempo_inicio  # Registrar el tiempo de inicio de la ruta
        self.pickups_evaluados = False
        print(f"Camión {self.id} asignado a una nueva ruta, tiempo de ruta: {tiempo_ruta} minutos")
        
    def actualizar_posicion(self, minuto_actual):
        if self.rutas and self.tiempo_restante != 0:
            ruta_actual = self.rutas[-1]  # Tomar la última ruta asignada
            tiempo_en_ruta = minuto_actual - self.tiempo_inicio_ruta
            self.posicion_actual = calcular_posicion_actual(ruta_actual, tiempo_en_ruta, self.velocidad)
        else:
            self.posicion_actual = None

#Calculo de distacia usando manhatan
def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
  
    # Función para calcular la posición actual del camión

#Funcion que se usa para crear el gif de movimiento y la ruta de los camiones
def calcular_posicion_actual(ruta, tiempo_transcurrido, velocidad_camion):
    tiempo_servicio=3
    tiempos_acumulados = [0]  # Lista para almacenar tiempos acumulados en cada punto
    tiempos_segmento = []     # Lista para almacenar tiempos de cada segmento (viaje + servicio)

    # Calcular tiempos acumulados en cada punto de la ruta
    for i in range(1, len(ruta)):
        # Distancia entre puntos
        distancia = manhattan_distance(ruta[i-1], ruta[i])
        tiempo_viaje = distancia / velocidad_camion
        tiempo_total_segmento = tiempo_viaje + tiempo_servicio  # Tiempo de viaje + tiempo de servicio en el punto anterior
        tiempos_segmento.append(tiempo_total_segmento)
        tiempos_acumulados.append(tiempos_acumulados[-1] + tiempo_total_segmento)

    # Verificar si el camión ya terminó su ruta
    if tiempo_transcurrido >= tiempos_acumulados[-1]:
        return ruta[-1]  # El camión está en el último punto de la ruta

    # Determinar en qué segmento de la ruta se encuentra el camión
    for i in range(1, len(tiempos_acumulados)):
        if tiempo_transcurrido < tiempos_acumulados[i]:
            tiempo_en_segmento = tiempo_transcurrido - tiempos_acumulados[i-1]
            # Verificar si el camión está en servicio (esperando) en el punto
            if tiempo_en_segmento <= tiempo_servicio:
                # El camión está esperando en el punto i-1
                return ruta[i-1]
            else:
                # El camión está viajando hacia el siguiente punto
                tiempo_en_viaje = tiempo_en_segmento - tiempo_servicio
                distancia_segmento = manhattan_distance(ruta[i-1], ruta[i])
                fraccion_recorrida = (velocidad_camion * tiempo_en_viaje) / distancia_segmento
                fraccion_recorrida = min(max(fraccion_recorrida, 0), 1)  # Asegurar que esté entre 0 y 1

                # Calcular posición actual interpolando entre el punto i-1 y el punto i
                x_actual = ruta[i-1][0] + fraccion_recorrida * (ruta[i][0] - ruta[i-1][0])
                y_actual = ruta[i-1][1] + fraccion_recorrida * (ruta[i][1] - ruta[i-1][1])
                return [x_actual, y_actual]

    # Si no se encontró, devolver la última posición conocida
    return ruta[-1]

#Gif que muestra como aparecen dinamicamente los pedidos y las rutas que se hacen
def crear_gif_con_movimiento_camiones(simulacion, archivo_gif="simulacion_movimiento_camiones.gif"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, 20000)
    ax.set_ylim(0, 20000)

    # Colores para cada camión
    colores_camiones = ["cyan", "magenta", "orange"]
    velocidad_camion = ((25 * 1000) / 60)  # 25 km/h convertidos a metros por minuto

    # Función para actualizar cada cuadro de la animación
    def actualizar(frame):
        ax.clear()
        ax.set_xlim(0, 20000)
        ax.set_ylim(0, 20000)
        ax.set_title(f"Minuto {simulacion.registro_minuto_a_minuto[frame]['minuto']}")
        ax.scatter(10000, 10000, c="black", s=50, label="Depósito", marker='D')  # Depósito como diamante negro

        estado = simulacion.registro_minuto_a_minuto[frame]

        # Graficar pedidos
        for pedido in estado["pedidos"]:
            x, y = pedido["coordenadas"]

            if x == 10000 and y == 10000:
                continue

            if pedido["tipo"] == "Pick-up":
                ax.plot(x, y, 'yo')  # Amarillo para pickups (siempre)
            elif pedido["tipo"] == "Delivery":
                if pedido["entregado"]:
                    ax.plot(x, y, 'go')  # Verde para entregados
                elif pedido["estado"] == "Disponible":
                    if estado["minuto"] - pedido["minuto_llegada"] > 180:  # Delivery vencido
                        ax.plot(x, y, 'mo')  # Magenta para vencidos
                    else:
                        ax.plot(x, y, 'bo')  # Azul para disponibles
                else:
                    ax.plot(x, y, 'ro')  # Rojo para no disponibles

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

        # Añadir la leyenda
        leyenda_colores = [
            ("Depósito", "black", "D"),
            ("Pick-up", "yellow", "o"),
            ("Delivery disponible", "blue", "o"),
            ("Delivery entregado", "green", "o"),
            ("Delivery vencido", "magenta", "o"),
            ("Delivery no disponible", "red", "o"),
        ]
        for label, color, marker in leyenda_colores:
            ax.scatter([], [], c=color, marker=marker, label=label)  # Elemento vacío para la leyenda

        ax.legend(loc="upper right")

    # Crear la animación
    anim = animation.FuncAnimation(fig, actualizar, frames=len(simulacion.registro_minuto_a_minuto), interval=100)
    
    # Guardar el GIF
    anim.save(archivo_gif, writer="pillow")
    print(f"GIF creado: {archivo_gif}")

#Genera un mapa de calor para ver donde estuvieron las rutas mas concurridas
def generar_mapa_calor_rutas(simulacion, grid_size=100, archivo_png="heatmap_rutas.png"):
    # Dimensiones del mapa
    mapa_dim = 20000
    heatmap = np.zeros((mapa_dim // grid_size, mapa_dim // grid_size))

    # Iterar sobre los camiones y sus rutas
    for estado in simulacion.registro_minuto_a_minuto:
        for camion in estado["camiones"]:
            for ruta in camion["rutas_realizadas"]:
                for punto in ruta:
                    x, y = punto

                    # Ignorar el depósito
                    if x == 10000 and y == 10000:
                        continue

                    # Convertir coordenadas a índices del heatmap
                    i, j = int(y // grid_size), int(x // grid_size)
                    if 0 <= i < heatmap.shape[0] and 0 <= j < heatmap.shape[1]:
                        heatmap[i, j] += 1

    # Normalizar el heatmap para que los valores estén entre 0 y 1
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    # Graficar el mapa de calor
    plt.figure(figsize=(10, 10))
    plt.imshow(heatmap, cmap="Reds", origin="lower", extent=[0, mapa_dim, 0, mapa_dim])
    plt.colorbar(label="Frecuencia de paso")
    plt.title("Mapa de Calor: Frecuencia de paso de los camiones")
    plt.xlabel("Coordenadas X")
    plt.ylabel("Coordenadas Y")
    plt.savefig(archivo_png)
    plt.show()

    print(f"Mapa de calor guardado en {archivo_png}")

#Se utiliza para ver los tiempos de los registros historicos
def procesar_tiempos(arrivals, division_minutos):

    minutos = [[segundo // division_minutos for segundo in simulacion] for simulacion in arrivals]
    df = pd.DataFrame(minutos).T  # Transponer para tener simulaciones como columnas
    arribos_por_minuto = df.apply(lambda x: x.value_counts().sort_index()).fillna(0).astype(int)
    return arribos_por_minuto

# Función placeholder para calcular el tiempo de la ruta
def calcular_tiempo_ruta(ruta, velocidad_camion):
    distancia_total = calcular_distancia_ruta(ruta)
    tiempo_extra = (len(ruta) - 2) * 3 #3 minutos en entregar cada pedido
    return ((distancia_total / velocidad_camion)  + tiempo_extra)# Tiempo en minutos

#Calcula la distancia total de una ruta
def calcular_distancia_ruta(ruta):
    distancia_total = 0

    # Calcular la distancia entre cada par de puntos consecutivos en la ruta
    for i in range(1, len(ruta)):
        distancia_total += manhattan_distance(ruta[i-1], ruta[i])

    return distancia_total

#Calcula el beneficio totol adquirido por la simulacion
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
    for pedido in simulacion.pedidos_disponibles + simulacion.pedidos_entregados + simulacion.pedidos_tercerizados:
        if pedido.indicador == 0:  # Delivery
            beneficio_maximo += 2
        elif pedido.indicador == 1:  # Pick-up
            beneficio_maximo += 1

    # Calcular el porcentaje del beneficio máximo alcanzado
    porcentaje_recuperado = (beneficio / beneficio_maximo) * 100 if beneficio_maximo > 0 else 0

    print(f"Beneficio total: {beneficio}, Beneficio máximo: {beneficio_maximo}, \nPorcentaje recuperado: {porcentaje_recuperado:.2f}%")
    return porcentaje_recuperado

#Calcula la distacia total que recorren los camiones
def calcular_distancia_total(camiones):
    distancia_total = 0
    for camion in camiones:
        for ruta in camion.rutas:
            distancia_total += calcular_distancia_ruta(ruta)
    return distancia_total

#Registra los tiempo en lo que fueron entregados los deliveries
def registrar_tiempos_delivery(simulacion):
    # Lista para almacenar los datos de cada delivery (momento de aparición y recogida)
    registros_delivery = []

    # Iterar sobre todos los camiones y sus rutas

    for pedido in simulacion.pedidos_entregados:
        if pedido.indicador == 0:  # Identificar los pedidos de delivery
                registro = {
                    "momento_aparicion": pedido.minuto_llegada,
                    "Tiempo_transcurrido": pedido.tiempo_entrega
                }
                registros_delivery.append(registro)

    # Convertir a DataFrame
    df_registros = pd.DataFrame(registros_delivery)

    # Guardar en un archivo CSV
    output_path = "registros_delivery.csv"
    df_registros.to_csv(output_path, index=False)
    print(f"Archivo guardado en {output_path}")

#Asigna un area al pedido para separar los pedidos en areas, es una politica, que se rige por parametros
def asignar_area(punto, parametros):
    x, y = punto
    cx, cy = 10000, 10000  # Centro del mapa
    vector = np.array([x - cx, y - cy])
    angle = np.degrees(np.arctan2(vector[1], vector[0]))

    if angle < 0:
        angle += 360

    # Usar los dos parámetros de ángulo para definir los límites de las tres áreas
    limite_area1 = parametros["limite_area1"]
    limite_area2 = parametros["limite_area2"]

    if 0 <= angle < limite_area1:
        return 1  # Área 1
    elif limite_area1 <= angle < limite_area2:
        return 2  # Área 2
    else:
        return 3  # Área 3

