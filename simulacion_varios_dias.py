import pickle
import pandas as pd
from funciones_caso_base import *
from politica_final import simular_minuto_a_minuto

# Parámetros de las ventanas de tiempo (ajustados previamente en Optuna)
parametros_ventana_1 = {
    "min_pedidos_salida": 10,
    "porcentaje_reduccion_distancia": 50,
    "max_puntos_eliminados": 15,
    "tiempo_maximo_entrega": 180,  # Constante
    "x_minutos": 30,
    "limite_area1": 120,
    "limite_area2": 240,
    "peso_min_pedidos": 1.0,
    "peso_ventana_tiempo": 1.0,
    "umbral_salida": 1.5,
    "tiempo_minimo_pickup": 30,
    "max_aumento_distancia": 10,
    "tiempo_necesario_pick_up": 1200,
    "tiempo_restante_max": 150,
    "max_aumento_distancia_delivery": 100,
}

parametros_ventana_2 = parametros_ventana_1.copy()  # Puedes ajustar los valores de cada ventana si lo necesitas
parametros_ventana_3 = parametros_ventana_1.copy()

# Cargar los datos de la simulación para los 100 días
with open('Instancia Tipo III/scen_points_sample.pkl', 'rb') as f:
    puntos_simulaciones = pickle.load(f)
with open('Instancia Tipo III/scen_arrivals_sample.pkl', 'rb') as f:
    llegadas_simulaciones = pickle.load(f)
with open('Instancia Tipo III/scen_indicador_sample.pkl', 'rb') as f:
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
    simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)

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
print(f'Beneficio maximo en porcentaje: {benef_max}')
print(f'Beneficio minimo en porcentaje: {benef_min}\n')
print(f"Distancia Promedio Recorrida: {distancia_promedio}")
print(f"Tiempo Promedio de Entrega: {tiempo_promedio_entrega}\n")
print(f"Pickups Completados Promedio: {pickup_promedio}")
print(f"Deliveries Completados Promedio: {delivery_promedio}")

