
import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_caso_base import *
from optuna_analisis_sens import funcion_opti_optuna



# Función para inicializar una simulación con una cantidad específica de camiones y velocidad específica
def inicializar_simulacion(camion_count, velocidad, indx):
    # Cargar datos necesarios
    with open('Instancia Tipo III/scen_points_sample.pkl', 'rb') as f:
        points = pickle.load(f)[indx]
    with open('Instancia Tipo III/scen_arrivals_sample.pkl', 'rb') as f:
        llegadas = pickle.load(f)[indx]
    with open('Instancia Tipo III/scen_indicador_sample.pkl', 'rb') as f:
        indicadores = pickle.load(f)[indx]

    arribos_por_minuto = procesar_tiempos([llegadas], division_minutos=60)[0]
    simulacion = EstadoSimulacion(minuto_inicial=520, puntos=points, indicadores=indicadores, arribos_por_minuto=arribos_por_minuto)

    # Crear camiones con la velocidad especificada
    camiones = [Camion(id=i+1, tiempo_inicial=0) for i in range(camion_count)]
    for camion in camiones:
        camion.velocidad = velocidad
    return simulacion, camiones

#Instancia 1
# parametros_ventana_1 = {'min_pedidos_salida': 8, 'porcentaje_reduccion_distancia': 69, 'max_puntos_eliminados': 18, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'tiempo_minimo_pickup': 22, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016}

# parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 34, 'max_puntos_eliminados': 9, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28}

# parametros_ventana_3 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 33, 'max_puntos_eliminados': 18, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556}


# instancia 2

# parametros_ventana_1 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 55, 'max_puntos_eliminados': 19, 'x_minutos': 60, 'limite_area1': 139, 'limite_area2': 270, 'peso_min_pedidos': 1.270769165494037, 'peso_ventana_tiempo': 0.5334298758833237, 'umbral_salida': 1.142787259922978, 'tiempo_minimo_pickup': 33, 'max_aumento_distancia': 20, 'tiempo_necesario_pick_up': 647, 'tiempo_restante_max': 97, 'max_aumento_distancia_delivery': 232}

# parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 43, 'max_puntos_eliminados': 11, 'x_minutos': 3, 'limite_area1': 126, 'limite_area2': 200, 'peso_min_pedidos': 1.9875097075448465, 'peso_ventana_tiempo': 1.9411077324851984, 'umbral_salida': 1.2940403662686877, 'tiempo_minimo_pickup': 36, 'max_aumento_distancia': 7, 'tiempo_necesario_pick_up': 1104, 'tiempo_restante_max': 132, 'max_aumento_distancia_delivery': 38}

# parametros_ventana_3 = {'min_pedidos_salida': 20, 'porcentaje_reduccion_distancia': 68, 'max_puntos_eliminados': 18, 'x_minutos': 14, 'limite_area1': 91, 'limite_area2': 265, 'peso_min_pedidos': 1.1700431872055927, 'peso_ventana_tiempo': 1.9398927740769498, 'umbral_salida': 1.0454057612407521, 'tiempo_minimo_pickup': 23, 'max_aumento_distancia': 10, 'tiempo_necesario_pick_up': 814, 'tiempo_restante_max': 111, 'max_aumento_distancia_delivery': 1224}

#instancia 3
parametros_ventana_1 = {'min_pedidos_salida': 8, 'porcentaje_reduccion_distancia': 69, 'max_puntos_eliminados': 18, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'tiempo_minimo_pickup': 22, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 34, 'max_puntos_eliminados': 9, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}

parametros_ventana_3 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 33, 'max_puntos_eliminados': 18, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556, 'tiempo_necesario_pick_up_en_ruta': 10, 'max_aumento_distancia_en_ruta': 13000}



 # instancia 4
# parametros_ventana_1 = {'min_pedidos_salida': 8, 'porcentaje_reduccion_distancia': 69, 'max_puntos_eliminados': 18, 'x_minutos': 36, 'limite_area1': 130, 'limite_area2': 263, 'peso_min_pedidos': 0.8539602391541146, 'peso_ventana_tiempo': 1.4716156151156219, 'umbral_salida': 1.2899961479169701, 'tiempo_minimo_pickup': 22, 'max_aumento_distancia': 13, 'tiempo_necesario_pick_up': 1338, 'tiempo_restante_max': 190, 'max_aumento_distancia_delivery': 1016}

# parametros_ventana_2 = {'min_pedidos_salida': 5, 'porcentaje_reduccion_distancia': 34, 'max_puntos_eliminados': 9, 'x_minutos': 16, 'limite_area1': 148, 'limite_area2': 184, 'peso_min_pedidos': 1.6641134475979422, 'peso_ventana_tiempo': 1.588743965974094, 'umbral_salida': 1.4367916479682685, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 8, 'tiempo_necesario_pick_up': 836, 'tiempo_restante_max': 11, 'max_aumento_distancia_delivery': 28}

# parametros_ventana_3 = {'min_pedidos_salida': 1, 'porcentaje_reduccion_distancia': 33, 'max_puntos_eliminados': 18, 'x_minutos': 15, 'limite_area1': 122, 'limite_area2': 225, 'peso_min_pedidos': 0.5389202543851898, 'peso_ventana_tiempo': 1.369371705453108, 'umbral_salida': 1.4795958635544573, 'tiempo_minimo_pickup': 43, 'max_aumento_distancia': 19, 'tiempo_necesario_pick_up': 1211, 'tiempo_restante_max': 96, 'max_aumento_distancia_delivery': 556}





def v_a_m(v):
    return ((v * 1000) / 60)
# Configuraciones del análisis
velocidad_inicial = v_a_m(25)  # Velocidad inicial en km/h
incremento_velocidad = v_a_m(5)  # Incremento en km/h por iteración
velocidad_maxima = v_a_m(200)  # Velocidad máxima deseada
beneficios = []
velocidades = []

# Análisis de sensibilidad
velocidad = velocidad_inicial
for v in range(25,125,5):

    # Inicializar la simulación y los camiones con la velocidad actual
    velocidad = v_a_m(v)
    velocidades.append(v)
    beneficios_iteracion = []
    for i in range (100):
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
    #velocidad += incremento_velocidad

# Graficar resultados
plt.figure(figsize=(10, 6))
plt.plot(velocidades, beneficios, marker='o')
plt.title("Análisis de sensibilidad: Beneficio vs Velocidad del camión")
plt.xlabel("Velocidad del camión (km/h)")
plt.ylabel("Beneficio (%)")
plt.grid()
plt.show()