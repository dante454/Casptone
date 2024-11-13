import numpy as np
from ruteo import cheapest_insertion_caso_base
import pickle
import matplotlib.pyplot as plt
from funciones_caso_base import *



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


def flujo_ruteo(camion, simulacion, minuto_actual):
    # 1. Obtener los pedidos disponibles
    pedidos_disponibles = simulacion.pedidos_disponibles

    # 3. Separar los pedidos según su área y seleccionar el área con más pedidos
    pedidos_a_rutear = separar_y_seleccionar_area(pedidos_disponibles)

    depot=[10000, 10000]
    # 4. Generar la ruta según los pedidos en el área con más pedidos
    ruta = cheapest_insertion_caso_base(points, depot, camion, minuto_actual, pedidos_a_rutear, tiempo_limite=180)

    ruta = eliminar_puntos_si_reducen_distancia(ruta, simulacion)
    # 7. Actualizar los pedidos entregados
    actualizar_estado_simulacion(simulacion, ruta)

    # 8. Actualizar el camión con la nueva ruta
    tiempo_ruta = calcular_tiempo_ruta(ruta, camion.velocidad)
    camion.asignar_ruta(ruta, tiempo_ruta, simulacion.minuto_actual)
    # 9. Devolver la ruta y el tiempo de la ruta
    return ruta, tiempo_ruta

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



# Función para actualizar el estado de la simulación, marcando los puntos de la ruta como visitados
def actualizar_estado_simulacion(simulacion, ruta):
    # Lista para almacenar los pedidos que se entregarán
    pedidos_a_entregar = []

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

                

def simular_minuto_a_minuto(simulacion, camiones, x_minutos):
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
                flujo_ruteo(camion, simulacion, simulacion.minuto_actual)
        
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
    else:
        return True  # Si se cumplen los criterios, el camión puede salir


# Función para gestionar la salida de los camiones
def gestionar_salida_camion(camion, simulacion):
    # Imprimir información del camión y el minuto actual
    print(f"Gestionando la salida del camión {camion.id} en el minuto {simulacion.minuto_actual}")

    # Llamar al flujo de ruteo para asignar una ruta al camión
    ruta, tiempo_ruta = flujo_ruteo(camion, simulacion)

    # Asignar la ruta generada al camión
    camion.asignar_ruta(ruta, tiempo_ruta)


def eliminar_puntos_si_reducen_distancia(ruta, simulacion, x_porcentaje=15, y_max_puntos=20):
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






with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
    points = pickle.load(f)[0]  # Seleccionar la primera simulación para este ejemplo
with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas = pickle.load(f)[0]
with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
    indicadores = pickle.load(f)[0]

arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

# Inicializar los camiones
camiones = [
    Camion(id=1, tiempo_inicial=0),
    Camion(id=2, tiempo_inicial=0),
    Camion(id=3, tiempo_inicial=0)
]


# Ejecutar la simulación con los camiones
x_minutos = 60  # Por ejemplo, los camiones pueden salir cada 30 minutos
simular_minuto_a_minuto(simulacion, camiones, x_minutos)

#registrar_tiempos_delivery(simulacion, camiones)
# Llamar a la función para crear el GIF
#crear_gif_con_movimiento_camiones(simulacion)

