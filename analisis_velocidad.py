
import matplotlib.pyplot as plt
import pickle
from politica_final import simular_minuto_a_minuto, EstadoSimulacion, Camion
from funciones_complementarias import *
import parametros as p



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


instancia_archivo = 'Instancia Tipo IV'

if instancia_archivo == 'Instancia Tipo I':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_1
    parametros_ventana_2 = p.parametros_ventana_2_instancia_1
    parametros_ventana_3 = p.parametros_ventana_3_instancia_1
elif instancia_archivo == 'Instancia Tipo II':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_2
    parametros_ventana_2 = p.parametros_ventana_2_instancia_2
    parametros_ventana_3 = p.parametros_ventana_3_instancia_2
elif instancia_archivo == 'Instancia Tipo III':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_3
    parametros_ventana_2 = p.parametros_ventana_2_instancia_3
    parametros_ventana_3 = p.parametros_ventana_3_instancia_3
elif instancia_archivo == 'Instancia Tipo IV':
    parametros_ventana_1 = p.parametros_ventana_1_instancia_4
    parametros_ventana_2 = p.parametros_ventana_2_instancia_4
    parametros_ventana_3 = p.parametros_ventana_3_instancia_4


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