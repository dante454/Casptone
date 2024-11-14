import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import *
from optuna_analisis_sens import funcion_opti_optuna





def analisis_sensibilidad(camion_max=20, iteraciones_optuna=100):
    beneficios_promedio = []
    num_camiones = []
    max_beneficio = 100  # Meta de beneficio como porcentaje

    # Cargar los datos de simulación
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        puntos_simulaciones = pickle.load(f)
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas_simulaciones = pickle.load(f)
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores_simulaciones = pickle.load(f)

    for camion_count in range(3, camion_max + 1):
        beneficios_iteracion = []

    # Cargar un conjunto diferente de puntos, arribos e indicadores
        points = puntos_simulaciones[2]
        llegadas = llegadas_simulaciones[2]
        indicadores = indicadores_simulaciones[2]
        arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
        
        # Optimizar parámetros para este día
        mejores_parametros = funcion_opti_optuna(points, arribos_por_minuto, indicadores, iteraciones_optuna)
        # Inicializar simulación y camiones con los parámetros optimizados
        

        for i in range(100):  # 100 iteraciones para cada número de camiones
            # Ejecutar la simulación
            points = puntos_simulaciones[i]
            llegadas = llegadas_simulaciones[i]
            indicadores = indicadores_simulaciones[i]
            arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]

            simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)
            camiones = [Camion(id=j+1, tiempo_inicial=0) for j in range(camion_count)]
        
            simular_minuto_a_minuto(simulacion, camiones, mejores_parametros[0], mejores_parametros[1], mejores_parametros[2])
            
            # Calcular beneficio de la iteración
            beneficio_total = simulacion.calcular_beneficio_acumulado()
            beneficios_iteracion.append(simulacion.calcular_porcentaje_beneficio(beneficio_total))  # Normalización del beneficio

        # Calcular el beneficio promedio para el número actual de camiones
        promedio_beneficio = sum(beneficios_iteracion) / len(beneficios_iteracion)
        beneficios_promedio.append(promedio_beneficio)
        num_camiones.append(camion_count)
        
        # Condición de parada si alcanzamos el 100% de beneficio
        if promedio_beneficio >= max_beneficio:
            break

    # Graficar el análisis de sensibilidad
    plt.figure(figsize=(10, 6))
    plt.plot(num_camiones, beneficios_promedio, marker='o')
    plt.title("Análisis de Sensibilidad: Beneficio Promedio vs. Cantidad de Camiones")
    plt.xlabel("Cantidad de Camiones")
    plt.ylabel("Beneficio Promedio (%)")
    plt.grid()
    plt.show()

# Ejecución del análisis de sensibilidad
analisis_sensibilidad(camion_max=20)