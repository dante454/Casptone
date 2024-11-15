
import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import *
from optuna_analisis_sens import funcion_opti_optuna



# Función para inicializar una simulación con una cantidad específica de camiones y velocidad específica
def inicializar_simulacion(camion_count, velocidad, indx):
    # Cargar datos necesarios
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[indx]
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[indx]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones con la velocidad especificada
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    for camion in camiones:
        camion.velocidad = velocidad
    return simulacion, camiones

# Parámetros de simulación para cada ventana de tiempo
parametros_ventana_1 = {'min_pedidos_salida': 8, 'porcentaje_reduccion_distancia': 69, 'max_puntos_eliminados': 18, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'tiempo_minimo_pickup': 22, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016}
parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 34, 'max_puntos_eliminados': 9, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28}
parametros_ventana_3 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 33, 'max_puntos_eliminados': 18, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556}
def v_a_m(v):
    return ((v * 1000) / 60)
# Configuraciones del análisis
velocidad_inicial = v_a_m(25)  # Velocidad inicial en km/h
incremento_velocidad = v_a_m(5)  # Incremento en km/h por iteración
velocidad_maxima = v_a_m(200)  # Velocidad máxima deseada
beneficios = []
velocidades = [i for i in range(25,125,5)]

# Análisis de sensibilidad
velocidad = velocidad_inicial
for i in range(25,125,5):
    # Inicializar la simulación y los camiones con la velocidad actual
    beneficios_iteracion = []
    for i in range (10):
        simulacion, camiones = inicializar_simulacion(camion_count=3, velocidad=velocidad, indx=i)
    
    # Ejecutar la simulación
        simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)
    
    # Calcular beneficio acumulado
        beneficio_total = simulacion.calcular_beneficio_acumulado()
        beneficio_porcentaje = simulacion.calcular_porcentaje_beneficio(beneficio_total)

        beneficio_total = simulacion.calcular_beneficio_acumulado()
        beneficio_porcentaje = calcular_beneficio(simulacion)
    
    # Guardar resultados
        beneficios_iteracion.append(beneficio_porcentaje)

    promedio_recuperado = sum(beneficios_iteracion)/len(beneficios_iteracion)
    beneficios.append(promedio_recuperado)
    
    if promedio_recuperado >= 100:
        break
    # Incrementar la velocidad
    velocidad += incremento_velocidad

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.plot(velocidades, beneficios, marker='o')
plt.title("Análisis de sensibilidad: Beneficio vs Velocidad del camión")
plt.xlabel("Velocidad del camión (km/h)")
plt.ylabel("Beneficio (%)")
plt.grid()
plt.show()