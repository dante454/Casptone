import numpy as np
from ruteo import generar_ruta
import pickle
import matplotlib.pyplot as plt
from funciones_caso_base import *


#Pasos a implementar forma inteligente y con un parametro modificable de priorizar los deliveries con los pick ups
#Forma inteligente de incertar un pick up a una ruta en movimiento
#Forma de descartar los pedidos de una ruta en caso de mejora
#Mejorar la iniciacion de la funcion para que esta se puedan modificar de forma intelegente los parametros

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


def flujo_ruteo(camion, simulacion, parametros):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    depot=[10000, 10000]
    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = generar_ruta(points, depot, camion, simulacion.minuto_actual, pedidos_a_rutear, parametros, tiempo_limite=180)


    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta, simulacion.minuto_actual)
    # 9. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta


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

# Función para actualizar el estado de la simulación, marcando los puntos de la ruta como visitados
def actualizar_estado_simulacion(simulacion, ruta):
    # Lista para almacenar los pedidos que se entregarán
    pedidos_a_entregar = []
    puntos_sin_pedidos = []

    # Para cada punto en la ruta, buscar el pedido correspondiente en pedidos disponibles
    for punto in ruta:
        pedidos_en_punto = [pedido for pedido in simulacion.pedidos_disponibles if np.array_equal(pedido.coordenadas, punto)]
        pedidos_a_entregar.extend(pedidos_en_punto)

    # Actualizar el estado de los pedidos y las listas de la simulación
    for pedido in pedidos_a_entregar:
        # Cambiar el estado del pedido a entregado
        pedido.entregar(simulacion.minuto_actual)
        # Mover el pedido a la lista de pedidos entregados
        simulacion.pedidos_entregados.append(pedido)

    # Remover los pedidos entregados de la lista de pedidos disponibles
    simulacion.pedidos_disponibles = [pedido for pedido in simulacion.pedidos_disponibles if pedido not in pedidos_a_entregar]

def simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3):
    # Inicia la simulación desde las 8:30 AM (minuto 630) hasta las 7:00 PM (1110 minutos)
    for minuto in range(520, 1020):
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


        # Actualizar tiempos de los camiones
        for camion in camiones:
            camion.actualizar_tiempo()
            
        # Evaluar si los camiones deben salir a rutear
        for camion in camiones:
            if evaluar_salida(camion, simulacion, parametros):
                # Gestionar el camión cuando sale a realizar una ruta
                flujo_ruteo(camion, simulacion, parametros)
        
        # Cada 30 minutos, calcular el porcentaje de beneficio captado
        if minuto % 30 == 0:
            beneficio_acumulado = simulacion.calcular_beneficio_acumulado()
            porcentaje_beneficio = simulacion.calcular_porcentaje_beneficio(beneficio_acumulado)
            simulacion.beneficio_por_intervalo.append((minuto, porcentaje_beneficio))

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

    print()
   
    #graficar_rutas_y_puntos(camiones, simulacion)
    #graficar_beneficio(simulacion)

def graficar_beneficio(simulacion):
    intervalos = [x[0] for x in simulacion.beneficio_por_intervalo]
    porcentajes = [x[1] for x in simulacion.beneficio_por_intervalo]

    if not porcentajes:
        print("No hay datos para graficar.")
        return

    plt.figure(figsize=(10, 5))
    plt.bar(intervalos, porcentajes, width=25, align='center')
    plt.xlabel('Minuto')
    plt.ylabel('Porcentaje de Beneficio Captado')
    plt.title('Porcentaje de Beneficio Captado cada 30 Minutos')
    plt.show()

# Función que evalúa los criterios de salida de los camiones
def evaluar_salida(camion, simulacion, parametros):
    if camion.tiempo_restante > 0:
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


def registrar_tiempos_delivery(simulacion, camiones):
    # Lista para almacenar los datos de cada delivery (momento de aparición y recogida)
    registros_delivery = []

    # Iterar sobre todos los camiones y sus rutas
    for camion in camiones:
        for pedido in simulacion.pedidos_entregados:
            if pedido.indicador == 0:  # Identificar los pedidos de delivery
                registro = {
                    "momento_aparicion": pedido.minuto_llegada,
                    "momento_recogida": pedido.tiempo_entrega
                }
                registros_delivery.append(registro)

    # Convertir a DataFrame
    df_registros = pd.DataFrame(registros_delivery)

    # Guardar en un archivo CSV
    output_path = "registros_delivery.csv"
    df_registros.to_csv(output_path, index=False)
    print(f"Archivo guardado en {output_path}")



# Parámetros de la simulación (ajustables por Optuna)
parametros_ventana_1 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 48, 'max_puntos_eliminados': 7, 'x_minutos': 14, 'limite_area1': 99, 'limite_area2': 219, 'peso_min_pedidos': 0.5053907930602788, 'peso_ventana_tiempo': 1.26559812361353, 'umbral_salida': 1.7215286984662614, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1000, 'tiempo_restante_max': 169, 'max_aumento_distancia_delivery': 71}
parametros_ventana_2 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 38, 'max_puntos_eliminados': 15, 'x_minutos': 15, 'limite_area1': 145, 'limite_area2': 185, 'peso_min_pedidos': 0.5036249735873504, 'peso_ventana_tiempo': 0.6160401293905916, 'umbral_salida': 1.1596366169682866, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 17, 'tiempo_necesario_pick_up': 1137, 'tiempo_restante_max': 107, 'max_aumento_distancia_delivery': 78}
parametros_ventana_3 = {'min_pedidos_salida': 17, 'porcentaje_reduccion_distancia': 54, 'max_puntos_eliminados': 6, 'x_minutos': 56, 'limite_area1': 112, 'limite_area2': 230, 'peso_min_pedidos': 1.5749264915561263, 'peso_ventana_tiempo': 1.9963865650894679, 'umbral_salida': 1.4696212191447602, 'tiempo_minimo_pickup': 23, 'max_aumento_distancia': 5, 'tiempo_necesario_pick_up': 1050, 'tiempo_restante_max': 109, 'max_aumento_distancia_delivery': 75}

# Cargar los datos de la simulación desde archivos pickle
with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
    points = pickle.load(f)[18]  # Seleccionar la primera simulación para este ejemplo
with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas = pickle.load(f)[18]
with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
    indicadores = pickle.load(f)[18]

arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

# Inicializar los camiones
camiones = [
    Camion(id=1, tiempo_inicial=0),
    Camion(id=2, tiempo_inicial=0),
    Camion(id=3, tiempo_inicial=0)
]

simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

#registrar_tiempos_delivery(simulacion, camiones)

# Llamar a la función para crear el GIF
#crear_gif_con_movimiento_camiones(simulacion)
