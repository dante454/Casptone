import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import *

# Función para inicializar una simulación con una cantidad específica de camiones
def inicializar_simulacion(camion_count):
    # Cargar datos necesarios
    with open('Instancia Tipo IV/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[0]
    with open('Instancia Tipo IV/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[0]
    with open('Instancia Tipo IV/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[0]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones según el parámetro `camion_count`
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    return simulacion, camiones

# Parámetros de simulación para cada ventana de tiempo
parametros_ventana_1 = {'min_pedidos_salida': 16, 'porcentaje_reduccion_distancia': 51, 'max_puntos_eliminados': 13, 'x_minutos': 28, 'limite_area1': 129, 'limite_area2': 202, 'peso_min_pedidos': 1.532367269189741, 'peso_ventana_tiempo': 1.4864469743034632, 'umbral_salida': 1.4468673396614375, 'tiempo_minimo_pickup': 42, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 574, 'tiempo_restante_max': 188, 'max_aumento_distancia_delivery': 1396}
parametros_ventana_2 = {'min_pedidos_salida': 16, 'porcentaje_reduccion_distancia': 51, 'max_puntos_eliminados': 13, 'x_minutos': 28, 'limite_area1': 129, 'limite_area2': 202, 'peso_min_pedidos': 1.532367269189741, 'peso_ventana_tiempo': 1.4864469743034632, 'umbral_salida': 1.4468673396614375, 'tiempo_minimo_pickup': 42, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 574, 'tiempo_restante_max': 188, 'max_aumento_distancia_delivery': 1396}
parametros_ventana_3 = {'min_pedidos_salida': 16, 'porcentaje_reduccion_distancia': 51, 'max_puntos_eliminados': 13, 'x_minutos': 28, 'limite_area1': 129, 'limite_area2': 202, 'peso_min_pedidos': 1.532367269189741, 'peso_ventana_tiempo': 1.4864469743034632, 'umbral_salida': 1.4468673396614375, 'tiempo_minimo_pickup': 42, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 574, 'tiempo_restante_max': 188, 'max_aumento_distancia_delivery': 1396}

# Configuraciones del análisis
max_beneficio = 100  # Beneficio total deseado como porcentaje
beneficios = []
num_camiones = []
camion = 1

# Análisis de sensibilidad
for i in range (30):
    # Inicializar la simulación y los camiones
    simulacion, camiones = inicializar_simulacion(camion)
    
    # Ejecutar la simulación
    simular_minuto_a_minuto(simulacion, camiones, parametros_ventana_1, parametros_ventana_2, parametros_ventana_3)
    
    # Calcular beneficio acumulado
    beneficio_total = simulacion.calcular_beneficio_acumulado()
    beneficio_porcentaje = calcular_beneficio(simulacion)
    
    # Guardar resultados
    beneficios.append(beneficio_porcentaje)
    num_camiones.append(camion)
    
    # Condición de parada: si alcanzamos o superamos el 100% de beneficio
    if beneficio_porcentaje >= max_beneficio:
        break
    
    camion += 1

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.plot(num_camiones, beneficios, marker='o')
plt.title("Análisis de sensibilidad: Beneficio vs Cantidad de camiones")
plt.xlabel("Cantidad de camiones")
plt.ylabel("Beneficio (%)")
plt.grid()
plt.show()

