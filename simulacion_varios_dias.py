
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
parametros_ventana_1 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 48, 'max_puntos_eliminados': 7, 'x_minutos': 14, 'limite_area1': 99, 'limite_area2': 219, 'peso_min_pedidos': 0.5053907930602788, 'peso_ventana_tiempo': 1.26559812361353, 'umbral_salida': 1.7215286984662614, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1000, 'tiempo_restante_max': 169, 'max_aumento_distancia_delivery': 71}
parametros_ventana_2 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 38, 'max_puntos_eliminados': 15, 'x_minutos': 15, 'limite_area1': 145, 'limite_area2': 185, 'peso_min_pedidos': 0.5036249735873504, 'peso_ventana_tiempo': 0.6160401293905916, 'umbral_salida': 1.1596366169682866, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 17, 'tiempo_necesario_pick_up': 1137, 'tiempo_restante_max': 107, 'max_aumento_distancia_delivery': 78}
parametros_ventana_3 = {'min_pedidos_salida': 17, 'porcentaje_reduccion_distancia': 54, 'max_puntos_eliminados': 6, 'x_minutos': 56, 'limite_area1': 112, 'limite_area2': 230, 'peso_min_pedidos': 1.5749264915561263, 'peso_ventana_tiempo': 1.9963865650894679, 'umbral_salida': 1.4696212191447602, 'tiempo_minimo_pickup': 23, 'max_aumento_distancia': 5, 'tiempo_necesario_pick_up': 1050, 'tiempo_restante_max': 109, 'max_aumento_distancia_delivery': 75}


# Cargar los datos de la simulación para los 100 días
with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
    puntos_simulaciones = pickle.load(f)
with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas_simulaciones = pickle.load(f)
with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
    indicadores_simulaciones = pickle.load(f)

# Inicializar listas para almacenar los resultados de los KPIs
beneficios = []
distancias_totales = []
tiempos_promedio_entrega = []
pickups_completados = []
deliveries_completados = []

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
    # x_minutos = 60  
    # simular_minuto_a_minuto(simulacion, camiones, x_minutos)

    # Recopilar los KPIs del día
    beneficio_total = calcular_beneficio(simulacion)
    distancia_total = calcular_distancia_total(camiones)
    tiempos_respuesta = [pedido.tiempo_entrega for pedido in simulacion.pedidos_entregados if pedido.tiempo_entrega is not None]
    tiempo_respuesta_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
    cantidad_pickups = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 1)
    cantidad_deliveries = sum(1 for pedido in simulacion.pedidos_entregados if pedido.indicador == 0)

    tiempos_promedio_entrega.append(tiempo_respuesta_promedio)
    beneficios.append(beneficio_total)
    distancias_totales.append(distancia_total)
    pickups_completados.append(cantidad_pickups)
    deliveries_completados.append(cantidad_deliveries)

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

