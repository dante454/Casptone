
#    -------------------  ¡¡¡¡ IMPORTANTE !!!!!! --------------------
#SI SE QUIERE SIMULAR LA POLITICA FINAL:
#Para correr este archivo es necesario comentar la linea 166, 167 y 318 del archivo politica_final

#SI SE QUIERE CORRER CASO BASE:
##Para correr este archivo es necesario comentar la linea 154, 155 y 258 del archivo politica_final


import pickle
import pandas as pd
from funciones_caso_base import *

#    -------------------  ¡¡¡¡ IMPORTANTE !!!!!! --------------------

#si se quiere simular Solucion inicial/Politica final dejar esta linea, si no comentarla
from politica_final import simular_minuto_a_minuto

#si se quiere ejecutar Caso_base ejecutar esta linea, si no comentarla:
#from caso_base_2 import simular_minuto_a_minuto


# Parámetros de las ventanas de tiempo (ajustados previamente en Optuna)


# parametros_ventana_1 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 47, 'max_puntos_eliminados': 16, 'x_minutos': 18, 'limite_area1': 147, 'limite_area2': 215, 'peso_min_pedidos': 1.6525938339343251, 'peso_ventana_tiempo': 1.8947957184968578, 'umbral_salida': 1.126101447963525, 'tiempo_minimo_pickup': 31, 'max_aumento_distancia': 16, 'tiempo_necesario_pick_up': 661, 'tiempo_restante_max': 106, 'max_aumento_distancia_delivery': 1048, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

# parametros_ventana_2 =  {'min_pedidos_salida': 3, 'porcentaje_reduccion_distancia': 54, 'max_puntos_eliminados': 15, 'x_minutos': 9, 'limite_area1': 140, 'limite_area2': 243, 'peso_min_pedidos': 1.8017927848294588, 'peso_ventana_tiempo': 1.325020645146538, 'umbral_salida': 1.488642659103274, 'tiempo_minimo_pickup': 37, 'max_aumento_distancia': 14, 'tiempo_necesario_pick_up': 975, 'tiempo_restante_max': 181, 'max_aumento_distancia_delivery': 1351, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

# parametros_ventana_3 = {'min_pedidos_salida': 12, 'porcentaje_reduccion_distancia': 42, 'max_puntos_eliminados': 17, 'x_minutos': 25, 'limite_area1': 110, 'limite_area2': 231, 'peso_min_pedidos': 1.0883231580184491, 'peso_ventana_tiempo': 1.0133168647668476, 'umbral_salida': 1.9840669226875491, 'tiempo_minimo_pickup': 34, 'max_aumento_distancia': 12, 'tiempo_necesario_pick_up': 1438, 'tiempo_restante_max': 68, 'max_aumento_distancia_delivery': 1355, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}


#instancia 2

parametros_ventana_1 =  {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 55, 'max_puntos_eliminados': 19, 'x_minutos': 60, 'limite_area1': 139, 'limite_area2': 270, 'peso_min_pedidos': 1.270769165494037, 'peso_ventana_tiempo': 0.5334298758833237, 'umbral_salida': 1.142787259922978, 'tiempo_minimo_pickup': 33, 'max_aumento_distancia': 20, 'tiempo_necesario_pick_up': 647, 'tiempo_restante_max': 97, 'max_aumento_distancia_delivery': 232, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

parametros_ventana_2 =  {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 43, 'max_puntos_eliminados': 11, 'x_minutos': 3, 'limite_area1': 126, 'limite_area2': 200, 'peso_min_pedidos': 1.9875097075448465, 'peso_ventana_tiempo': 1.9411077324851984, 'umbral_salida': 1.2940403662686877, 'tiempo_minimo_pickup': 36, 'max_aumento_distancia': 7, 'tiempo_necesario_pick_up': 1104, 'tiempo_restante_max': 132, 'max_aumento_distancia_delivery': 38, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

parametros_ventana_3 = {'min_pedidos_salida': 20, 'porcentaje_reduccion_distancia': 68, 'max_puntos_eliminados': 18, 'x_minutos': 14, 'limite_area1': 91, 'limite_area2': 265, 'peso_min_pedidos': 1.1700431872055927, 'peso_ventana_tiempo': 1.9398927740769498, 'umbral_salida': 1.0454057612407521, 'tiempo_minimo_pickup': 23, 'max_aumento_distancia': 10, 'tiempo_necesario_pick_up': 814, 'tiempo_restante_max': 111, 'max_aumento_distancia_delivery': 1224, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}


#instancia 4
# parametros_ventana_1 = {'min_pedidos_salida': 8, 'porcentaje_reduccion_distancia': 69, 'max_puntos_eliminados': 18, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'tiempo_minimo_pickup': 22, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

# parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 34, 'max_puntos_eliminados': 9, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

# parametros_ventana_3 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 33, 'max_puntos_eliminados': 18, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

instancia_archivo = 'Instancia Tipo I'

# Cargar los datos de la simulación para los 100 días
with open(f'{instancia_archivo}/scen_points_sample.pkl', 'rb') as f:
    puntos_simulaciones = pickle.load(f)
with open(f'{instancia_archivo}/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas_simulaciones = pickle.load(f)
with open(f'{instancia_archivo}/scen_indicador_sample.pkl', 'rb') as f:
    indicadores_simulaciones = pickle.load(f)

# Inicializar listas para almacenar los resultados de los KPIs
beneficios = []
distancias_totales = []
tiempos_promedio_entrega = []
pickups_completados = []
deliveries_completados = []
numero_rutas = []
beneficio_intervalos =[]
deliveries_por_intervalo = []
pickups_por_intervalo = []

# Ejecutar la simulación para cada uno de los 100 días
for dia in range(100):
    print(f"Simulando el día {dia + 1}...")

    # Cargar los datos específicos del día
    points = puntos_simulaciones[dia]
    llegadas = llegadas_simulaciones[dia]
    indicadores = indicadores_simulaciones[dia]

    # Procesar los arribos por minuto para este día
    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

    # Inicializar la simulación para el día
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Inicializar los camiones
    camiones = [
        Camion(id=1, tiempo_inicial=0),
        Camion(id=2, tiempo_inicial=0),
        Camion(id=3, tiempo_inicial=0)
    ]

    # Ejecutar la simulación de un día

    #    ------------------- ¡¡¡¡ IMPORTANTE !!!!!! --------------------
    #SI es para la solucion inicial ejecutar la siguente linea
    simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

    #si se esta simulando para el caso base ejecutar las siguentes lineas: SINO, COMENTARLAS
    x_minutos = 60  
    #simular_minuto_a_minuto(simulacion, camiones, x_minutos)

    # Recopilar los KPIs del día
    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)
    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)
    rutas = sum(len(camion.rutas) for camion in camiones )



    tiempos_promedio_entrega.append(tiempo_respuesta_promedio)
    beneficios.append(beneficio_total)
    distancias_totales.append(distancia_total)
    pickups_completados.append(cantidad_pickups)
    deliveries_completados.append(cantidad_deliveries)
    numero_rutas.append(rutas)
    beneficio_intervalos.append(simulacion.beneficio_por_intervalo)
    deliveries_por_intervalo.append(simulacion.deliveries_intervalos)
    pickups_por_intervalo.append(simulacion.pickups_intervalos)



#calcualr % minimo y maximo obtenido
benef_max = max(beneficios)
benef_min = min(beneficios)
dia_max_ganancia = beneficios.index(benef_max) 

# Calcular los KPIs promedio
beneficio_promedio = sum(beneficios) / len(beneficios)
distancia_promedio = sum(distancias_totales) / len(distancias_totales)
tiempo_promedio_entrega = sum(tiempos_promedio_entrega) / len(tiempos_promedio_entrega)
pickup_promedio = sum(pickups_completados) / len(pickups_completados)
delivery_promedio = sum(deliveries_completados) / len(deliveries_completados)
rutas_promedio = sum(numero_rutas) / len(numero_rutas)
largo_rutas_prom = distancia_promedio / rutas_promedio


# Mostrar los resultados
print('\n', '--'*16)
print("\nResultados de la Simulación de 100 Días:\n")
print(f"Beneficio Promedio Capturado en porcentaje: {beneficio_promedio}")
print(f'Beneficio maximo en porcentaje: {benef_max} en el dia {dia_max_ganancia}')
print(f'Beneficio minimo en porcentaje: {benef_min}\n')
print(f"Distancia Promedio Recorrida: {distancia_promedio}")
print(f"Tiempo Promedio de Entrega: {tiempo_promedio_entrega}\n")
print(f"Pickups Completados Promedio: {pickup_promedio}")
print(f"Deliveries Completados Promedio: {delivery_promedio}")
print(f'Largo de ruta promedio: {largo_rutas_prom}')
print(f'Rutas promedio {rutas_promedio}')

intervalos_agrupados = {}
for dia in beneficio_intervalos:
    for minuto, beneficio in dia:
        if minuto not in intervalos_agrupados:
            intervalos_agrupados[minuto] = []
        intervalos_agrupados[minuto].append(beneficio)

# Paso 2: Calcular el promedio por minuto
minutos = sorted(intervalos_agrupados.keys())
promedio_beneficio_por_minuto = [
    np.mean(intervalos_agrupados[minuto]) for minuto in minutos
]

# Paso 3: Graficar los resultados
plt.figure(figsize=(10, 6))
plt.plot(minutos, promedio_beneficio_por_minuto, marker="o", label="Beneficio Promedio")
plt.title("Tendencia del Beneficio Promedio por Intervalo de Tiempo")
plt.xlabel("Minuto")
plt.ylabel("Beneficio (%)")
plt.grid(True, linestyle="--", alpha=0.7)
plt.legend()
plt.tight_layout()

# Mostrar el gráfico
plt.show()

intervalos_deliveries_agrupados = {}
intervalos_pickups_agrupados = {}

for dia in deliveries_por_intervalo:
    for minuto, porcentaje_delivery in dia:
        if minuto not in intervalos_deliveries_agrupados:
            intervalos_deliveries_agrupados[minuto] = []
        intervalos_deliveries_agrupados[minuto].append(porcentaje_delivery)

for dia in pickups_por_intervalo:
    for minuto, porcentaje_pickup in dia:
        if minuto not in intervalos_pickups_agrupados:
            intervalos_pickups_agrupados[minuto] = []
        intervalos_pickups_agrupados[minuto].append(porcentaje_pickup)

# Paso 2: Calcular el promedio por intervalo
minutos = sorted(intervalos_deliveries_agrupados.keys())  # Usamos los mismos minutos para ambos porcentajes
promedio_deliveries_por_minuto = [
    sum(intervalos_deliveries_agrupados[minuto]) / len(intervalos_deliveries_agrupados[minuto])
    for minuto in minutos
]

promedio_pickups_por_minuto = [
    sum(intervalos_pickups_agrupados[minuto]) / len(intervalos_pickups_agrupados[minuto])
    for minuto in minutos
]

# Paso 3: Graficar los promedios
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(minutos, promedio_deliveries_por_minuto, label='Promedio Deliveries', marker='o')
plt.plot(minutos, promedio_pickups_por_minuto, label='Promedio Pickups', marker='x')

plt.xlabel('Minuto')
plt.ylabel('Porcentaje')
plt.title('Promedio de Porcentajes de Deliveries y Pickups por Intervalos')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()