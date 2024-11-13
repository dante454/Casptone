import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import *

# Función para inicializar una simulación con una cantidad específica de camiones y velocidad específica
def inicializar_simulacion(camion_count, velocidad):
    # Cargar datos necesarios
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[18]
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[18]
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[18]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones con la velocidad especificada
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    for camion in camiones:
        camion.velocidad = velocidad
    return simulacion, camiones

# Parámetros de simulación para cada ventana de tiempo
parametros_ventana_1 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 48, 'max_puntos_eliminados': 7, 'x_minutos': 14, 'limite_area1': 99, 'limite_area2': 219, 'peso_min_pedidos': 0.505, 'peso_ventana_tiempo': 1.265, 'umbral_salida': 1.721, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1000, 'tiempo_restante_max': 169, 'max_aumento_distancia_delivery': 71}
parametros_ventana_2 = {'min_pedidos_salida': 6, 'porcentaje_reduccion_distancia': 38, 'max_puntos_eliminados': 15, 'x_minutos': 15, 'limite_area1': 145, 'limite_area2': 185, 'peso_min_pedidos': 0.503, 'peso_ventana_tiempo': 0.616, 'umbral_salida': 1.159, 'tiempo_minimo_pickup': 17, 'max_aumento_distancia': 17, 'tiempo_necesario_pick_up': 1137, 'tiempo_restante_max': 107, 'max_aumento_distancia_delivery': 78}
parametros_ventana_3 = {'min_pedidos_salida': 17, 'porcentaje_reduccion_distancia': 54, 'max_puntos_eliminados': 6, 'x_minutos': 56, 'limite_area1': 112, 'limite_area2': 230, 'peso_min_pedidos': 1.574, 'peso_ventana_tiempo': 1.996, 'umbral_salida': 1.469, 'tiempo_minimo_pickup': 23, 'max_aumento_distancia': 5, 'tiempo_necesario_pick_up': 1050, 'tiempo_restante_max': 109, 'max_aumento_distancia_delivery': 75}

def v_a_m(v):
    return ((v * 1000) / 60)
# Configuraciones del análisis
velocidad_inicial = v_a_m(25)  # Velocidad inicial en km/h
incremento_velocidad = v_a_m(5)  # Incremento en km/h por iteración
velocidad_maxima = v_a_m(200)  # Velocidad máxima deseada
beneficios = []
velocidades = [i for i in range(25,200,5)]

# Análisis de sensibilidad
velocidad = velocidad_inicial
while velocidad <= velocidad_maxima:
    # Inicializar la simulación y los camiones con la velocidad actual
    simulacion, camiones = inicializar_simulacion(camion_count=3, velocidad=velocidad)
    
    # Ejecutar la simulación
    simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)
    
    # Calcular beneficio acumulado
    beneficio_total = simulacion.calcular_beneficio_acumulado()
    beneficio_porcentaje = simulacion.calcular_porcentaje_beneficio(beneficio_total)
    
    # Guardar resultados
    beneficios.append(beneficio_porcentaje)

    
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